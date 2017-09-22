import sys
import os
import re
import csv
from datetime import datetime
from development.models import DevelopmentProject, ConsultationStage, FileNo, FilingCode, DevelopmentProjectAction
from crm.models import Person, Organization
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

"""
Provide the relative path to the folder with the RTS import csv files - relative to the base cedar repo directory:

This script requires the following files to be present in that directory:
    rts.csv
    filing_codes.csv
    filing_codes_map.csv
    consultation_stages.csv
    subtype_tags_map.csv

Run:
    python manage.py runscript import_rts --script-args='tmp/data/kitselas'


"""


def run(*args):
    path_to_data_folder = args[0]

    if not os.path.exists(path_to_data_folder):
        sys.exit("!! Data file was not found:{}".format(path_to_data_folder))

    logger.info('Begin import.\n')

    header = [
        'Referral_id',  # to description field.
        'Proponent',  # crm.Org.name
        'Proponent_Contact_Name',  # crm.Person.name first/last
        'Proponent_Contact_Phone',  # crm.Person.phone
        'Referral_date',  # development.DevelopmentProject.initial_date
        'Response_due',  # development.DevelopmentProjectAction
        'Type',  # map to FilingCodes -> see type mapping sheet
        'Status',  # map to Consultation Stage -> see status mapping sheet
        'Sub_status',  # map to various fields -> see status mapping sheet
        'Invoice_date',  # development.DevelopmentProject.description
        'Payment_recd',  # development.DevelopmentProject.description
        'Initial_inv',  # development.DevelopmentProject.description
        'Initial_amt',  # development.DevelopmentProject.description
        'Act_cost',  # development.DevelopmentProject.description
        'Status',  # IGNORE - duplicate
        'Priority',  # development.DevelopmentProject.description
        'Closed_date',  # development.DevelopmentProject.description
        'Reference_number',  # development.DevelopmentProject.description
        'Rts_Number',  # development.FileNo - Org="RTS" type="Other"
        'Area',  # development.DevelopmentProject.area
        'Engage_lvl'  # development.DevelopmentProject.description
    ]

    with open(os.path.join(path_to_data_folder, 'rts.csv'), 'r') as csv_file:
        csv_dict = csv.DictReader(csv_file, delimiter=',', fieldnames=header)

        # burn the header row.
        next(csv_dict)

        # 1. Create the RTS Org if it doesn't exist (for holding "RTS_Number" FileNo entries)
        rts_org, created = Organization.objects.get_or_create(name='RTS')

        # 2. Load filing codes.
        import_file_codes(os.path.join(path_to_data_folder, 'filing_codes.csv'))
        file_code_map = map_rts_type_to_filing_code(os.path.join(path_to_data_folder, 'filing_codes_map.csv'))

        # 3. Load consultation stages
        import_consultation_stages(os.path.join(path_to_data_folder, 'consultation_stages.csv'))

        # 4. Load tags:
        substatus_to_tag = map_rts_substatus_to_tag(os.path.join(path_to_data_folder, 'subtype_tags_map.csv'))

        for row in csv_dict:
            # print("Title:{} - {} - {}".format(row['Proponent'].strip(), row['Rts_Number'].strip(), row['Referral_date'].strip()))
            # print("Referral_id:", row['Referral_id'].strip())

            '''
            Do Organization and People
            '''
            # Create organization and set contact phone
            org, created = Organization.objects.get_or_create(
                name=row['Proponent'].strip(),
            )
            org.phone = row['Proponent_Contact_Phone'].strip()
            org.save()
            logger.info("ORGANIZATION: {}. created? {}".format(org, created))

            # Create the person:
            if row['Proponent_Contact_Name'] == 'N/A':
                person = None
            else:
                person, created = Person.objects.get_or_create(
                    name_first=row['Proponent_Contact_Name'].split(" ")[0],
                    name_last=row['Proponent_Contact_Name'].split(" ")[1]
                )
                person.phone = row['Proponent_Contact_Phone'].strip()
                person.save()
                logger.info("PERSON: {}, created? {}".format(person, created))

            # add person to Org:
            if person:
                person.organizations.add(org)

            # make file no string here so we can use it in the title.
            rts_file_no_str = 'RTS-{}'.format(row['Rts_Number'])

            project, created_project = DevelopmentProject.objects.get_or_create(
                cedar_project_name='{} - {} - {}'.format(org.name, rts_file_no_str, row['Referral_date']),
                consultation_stage=determine_consultation_stage(row)
            )

            if person not in project.company_contact.all() and person is not None:
                project.company_contact.add(person)

            '''
            Do RTS Number
            '''
            rts_file_no, created = FileNo.objects.get_or_create(
                project=project,
                file_number=rts_file_no_str,
                organization=rts_org,
                org_type='other'
            )
            if created:
                logger.info('RTS Number: created new FileNo {} for RTS Org'.format(rts_file_no.file_number))

            '''
            Do FilingCode
            '''
            # assumes all possible filing code have already been created by the load.
            if row['Type'] in file_code_map.keys():
                fc = FilingCode.objects.get(label=file_code_map[row['Type']])
                project.filing_code = fc
                logger.info("added filing code {} to project.".format(fc))

            '''
            Do Due Date
            '''
            due_date = get_date(row['Response_due'])
            if due_date is not None:
                # turn it into a 9am timezone-aware datetime object.
                due_date = timezone.make_aware(due_date, timezone.get_default_timezone()) + timezone.timedelta(hours=9)
                # remove any prior development actions for this project (in case re are re-running this thing).
                if DevelopmentProjectAction.objects.filter(project=project).exists():
                    DevelopmentProjectAction.objects.filter(project=project).delete()
                due_date_obj, created = DevelopmentProjectAction.objects.get_or_create(
                    project=project,
                    label="Due date",
                    date=due_date
                )
                if created:
                    logger.info("DUE DATE: created new Development due date action: {}".format(due_date))

            '''
            Do remaining Dev Project Fields
            '''
            project.area = row['Area']
            project.initial_date = get_date(row['Referral_date'])

            desc = """
            Invoice Date: {Invoice_date}
            Payment Received: {Payment_recd}
            Initial Investment: {Initial_inv}
            Initial Amount: {Initial_amt}
            Actual Cost: {Act_cost}
            Priority: {Priority}
            Closed Date: {Closed_date}
            Reference Number: {Reference_number}
            Referral ID: {Referral_id}
            """.format(**row)  # how cool is that??

            project.description = desc
            project.status = determine_devprj_status(project)

            # Tags
            # Create a tag if this sub status has a mapped tag:
            if row['Sub_status'] in substatus_to_tag.keys():
                # Create tag here.
                tag_text = substatus_to_tag[row['Sub_status']].strip()
                logger.info("add tag \"{}\"".format(tag_text))
                project.tags.add(tag_text)
                # project.save()

            # Need:
            # Primary Authorization:
            # to be left "blank".
            # Final Decision:
            # To be left as "pending"

            project.save()

            if created_project:
                logger.info("PROJECT CREATED: {}".format(project))
            else:
                logger.info("PROJECT UPDATED: {}".format(project))

        logger.info('Import Done.\n')


def import_file_codes(path_to_csv):
    """
    Loads the full set of C8 filing codes (client-defined)
    :param path_to_csv:
    :return: None
    """
    header = ['code', 'label']

    logger.info("Checking/creating filing codes.")
    with open(path_to_csv, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', fieldnames=header)

        # burn header
        next(csv_reader)

        for row in csv_reader:
            instance, created = FilingCode.objects.get_or_create(code=row['code'].strip(), label=row['label'].strip())
            if created:
                logger.info("created new filing code: {}".format(row['label']))
    logger.info("Checking/creating filing codes. Done.")


def map_rts_substatus_to_tag(path_to_csv):
    """
    Loads the all the tags from the subtype_tags_map.csv file. Returns a dict we can use
    later to figure out how to map subtypes to tags
    :param path_to_csv:
    :return: dict of subtype:tag
    """
    header = ['rts_subtype', 'tag']

    subtype_tag_map = {}

    logger.info("Loading subtype:tags map.")
    with open(path_to_csv, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', fieldnames=header)

        # burn header
        next(csv_reader)

        for row in csv_reader:
            subtype_tag_map[row['rts_subtype']] = row['tag']
            logger.info("TAG: subtype:tag - {}:{}".format(row['rts_subtype'], row['tag']))

    logger.info("Loading subtype:tags map. Done.")
    return subtype_tag_map


def map_rts_type_to_filing_code(path_to_csv):
    """
    Loads the csv that maps rts types to c8 filing codes.
    :param path_to_csv:
    :return: dict. key:value = rts_type:filing_code_label
    """
    header = ['rts_type', 'filing_label']

    logger.info("Loading rts_type/filing_code_label csv")
    with open(path_to_csv, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', fieldnames=header)

        # burn header
        next(csv_reader)

        data = {}
        for row in csv_reader:
            data[row['rts_type']] = row['filing_label']
            logger.info("MAP: RTS Type {} mapped to C8 Filing Label {}".format(row['rts_type'], row['filing_label']))

        return data


def import_consultation_stages(path_to_csv):
    """
    Loads the full set of C8 client-defined consultation stages
    :param path_to_csv:
    :return: None
    """
    header = ['stage_name', 'stage_weight']

    logger.info("Checking/creating consultation stages.")
    with open(path_to_csv, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',', fieldnames=header)

        # burn header
        next(csv_reader)

        for row in csv_reader:
            instance, created = ConsultationStage.objects.get_or_create(stage_name=row['stage_name'], stage_weight=row['stage_weight'])
            if created:
                logger.info("created new consultation stage: {} with weight: {}".format(row['stage_name'], row['stage_weight']))

    logger.info("Checking/creating consultation stages. Done.")


def determine_consultation_stage(data):
    """
    Figures out which consultation stage instance to give for this project. Makes use of:
        RTS Status field,
        RTS SubStatus field.
    Does not use a map csv file like the RTS Type -> Filing Code method. The mapping is hard-coded here.
    Assumes that ALL possible Consultation stage records have already been loaded.

    This could/should have been done with a "_map.csv" file.

    :param data: a row dict from a csv row reader
    :return: ConsultationStage instance
    """
    status_to_consulation_stage = {
        'APPROVED': 'Approved',
        'CANCELLED': 'Cancelled',
        'CONDITIONAL': 'Conditional Approval',
        'NEW': 'New',
        'NO ACTION': 'No Action',
        'PENDING': 'Pending',
        'PRE-RTS': 'Pre-Referral',
        'REJECTED': 'Rejected',
    }

    # there are 3 instances where the substatus has an effect on the consultation stage.
    substatus_to_consultation_stage = {
        'Information': 'Information Only',
        'InformationOnly': 'Information Only',
        'Not Approved': 'Rejected',
    }

    status = data['Status']
    substatus = data['Sub_status']

    if substatus in substatus_to_consultation_stage.keys():
        stage_name = substatus_to_consultation_stage[substatus]
    else:
        stage_name = status_to_consulation_stage[status]

    logger.info("determine consultation stage. rts_status: {}, rts_substatus: {}. consultation_stage: {}"
                .format(status, substatus, stage_name))
    c = ConsultationStage.objects.get(stage_name=stage_name)
    return c


def determine_devprj_status(project):
    """
    Figures out the DEV PRJ status (NOT RTS Status).
    Uses consultation stage -> status map that I made up using the main field map document
    :param project: development project instance with Consultation Stage field already set.
    :return:
    """
    consultation_stage_to_project_status = {
        'Approved': 'active',
        'Cancelled': 'inactive',
        'Conditional Approval': 'active',
        'New': 'active',
        'No Action': 'inactive',
        'Pending': 'active',
        'Pre-Referral': 'active',
        'Rejected': 'inactive',
        'Information Only': 'active',
    }
    return consultation_stage_to_project_status[project.consultation_stage.stage_name]


def determine_final_decision(project):
    """
    STUB IN
    Figures out the DEV PRJ final decision
    Uses DEV PRJ status, and Consultation Stages to figure out final decision.
    :param project: development project instance with Consultation Stage field already set.
    :return:
    """
    if project.status == 'active':
        return 'pending'
    else:
        None


def determine_tag(data, project):
    """
    STUB IN
    Figures out the DEV PRJ tags
    Uses RTS Sub Type tags map CSV (and field map specified in code).
    :param data: a row dict from csv reader
    :param project: development project instance.
    :return: list of tags
    """
    pass


def get_date(date_string):
    """
    The OS doesn't seem to suppor the string parsing syntax needed for the date format
    used by RTS: d/m/yyyy  (where d and m can be one or more characters.
    The datetime parse call should be: datetime.strptime('24/1/1980', '%-d/%-m/%YYYY')

    Do something with regex instead.

    :param date_string:
    :return:
    """
    # logger.info("Parsing date: {}".format(date_string))
    search = re.search('([0-9]+)/([0-9]+)/([0-9]+)', date_string)
    if search is not None:
        return datetime(
            month=int(search.groups()[0]),
            day=int(search.groups()[1]),
            year=int(search.groups()[2])
        )
    else:
        logger.error("date was none")
        return None
