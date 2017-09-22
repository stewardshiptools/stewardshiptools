from heritage.models import Project, Interview, Session, InterviewAsset, SessionAsset
from assets.models import AssetType
from crm.models import Person

from django.core.files import File
import csv
import sys
from datetime import datetime

"""
Run this script and feed it the import_assets_stage_1.csv file.
If the script encounters an error it will create an err.txt file
in the repo folder.
I suggest running the script and redirecting output eg:

    python manage.py runscript import_assets  --script-args='cedar/scripts/data/import_assets_stage_1.csv' > import_assets.log

Import fake assets:
    python manage.py runscript import_assets  --script-args='cedar/scripts/data/import_assets_stage_1_fake.csv' > import_assets_fake.log



"""



def run(*args):

    print ("Begin asset import...")

    try:
        control_file_path = args[0]
        control_file = open(control_file_path, 'r')
        err_filename = 'asset_import_err.txt'
        header = [
            'project_phase_code',
            'interview',
            'session',
            'filepath',
            'filename',
            'file_ext',
            'asset_type',
            'skip'
        ]
        control_dict = csv.DictReader(control_file, header)

    except:
        print ("Problem opening the control file:", control_file_path)
        sys.exit(0)

    for row in control_dict:
        # Skip the header row. Why didn't I have to do this before?
        if row['project_phase_code'] == 'project_phase_code': continue

        if row['skip'] != 'TRUE':
            print("getting project number:", row['project_phase_code'])
            project = Project.objects.get(phase_code=int(row['project_phase_code']))
            # print (project)

            # Get rid project name text clutter:
            interview_text = str(row['interview']).replace(project.name, '')
            session_text = str(row['session']).replace(project.name, '')

            # These splits depend on an extra space at the front of the string:
            interviewer_initials = interview_text.split(' ')[1]
            participant_number = int(interview_text.split(' ')[3])
            interviewer = Person.objects.filter(initials=interviewer_initials, roles__name__contains="Interviewer")
            interview = Interview.objects.get(phase=project,
                                              participant_number=participant_number,
                                              primary_interviewer=interviewer)

            # print("interview is:", interview)

            if row['session']:
                try:
                    session_num = session_text.split(' ')[4]
                    if session_num[0] == '0':
                        session_num = session_num[1:].strip()  # Pop off the leading zero if it's there.

                    session = Session.objects.get(interview=interview, number=session_num)
                except Exception as err:
                    print (row['session'])
                    print ("Could not find specified session:", err)
                    err_file = open(err_filename, 'a')
                    err_file.write("{},Could not find session: {},{}".format(datetime.now(), row['session'], '\n'))
                    err_file.close()

            else:
                session = None

            try:
                f = File(file=open(row['filepath'], 'rb'), name=row['filename'] + row['file_ext'])
            except FileNotFoundError:
                print("Could not find specified file:", row['filepath'])
                err_file = open(err_filename, 'a')
                err_file.write("{},File not found: {},{}".format(datetime.now(), row['filepath'], '\n'))
                err_file.close()
                continue

            if session:
                new_asset = SessionAsset(
                    file=f,
                    session=session,
                    name=row['filename'] + row['file_ext'],
                    asset_type=AssetType.objects.get(type_of_asset=row['asset_type']),
                    comment=row['filepath'])

                print("Adding Session Asset.", row['session'], row['filepath'])

            else:
                new_asset = InterviewAsset(
                    file=f,
                    interview=interview,
                    name=row['filename'] + row['file_ext'],
                    asset_type=AssetType.objects.get(type_of_asset=row['asset_type']),
                    comment=row['filepath'])
                print("Adding Interview Asset.", row['interview'], row['filepath'])

            new_asset.save()
