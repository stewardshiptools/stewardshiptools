import sys
import os
import csv
from development.models import DevelopmentProject, ConsultationStage, FileNo
from crm.models import Person

"""
Save your csv data file in development/scripts/data. The script takes the NAME of the file,
not the full path.

python manage.py runscript import_DAs_from_C7 --script-args='data.csv'

e.g.
python manage.py runscript import_DAs_from_C7 --script-args='gnn_cedar7_da_export_20160729_2.csv'

"""


def run(*args):
    # path_to_csv = args[0]
    path_to_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/{}'.format(args[0])))

    if not os.path.exists(path_to_csv):
        sys.exit("!! Data file was not found:{}".format(path_to_csv))

    print('Beginning import.\n')

    # I used the below to get clean headers.
    # with open(path_to_csv, 'r') as csv_file:
    #     for row in csv.reader(csv_file, delimiter='|'):
    #         for col in row:
    #             print (col)
    #         break

    header = [
        'Drupal NID',
        'FN - FILE - NUM',
        'Mailharvest harvest code',
        'Title',
        'Project Description',
        'Filing code',
        '3. Authorization type',
        'Project group',
        'Active',
        'Stage',
        'Company or Government File',
        'Location Description',
        'Government contact(s)',
        'Proponent contact(s)'
    ]

    with open(path_to_csv, 'r') as csv_file:
        csv_dict = csv.DictReader(csv_file, delimiter='|', fieldnames=header)

        next(csv_dict)

        for row in csv_dict:
            # for col in header:
            # print(row[col])
            # print("{}: {}".format(row['Drupal NID'], row['Location Description']))

            consultation_stage, created_stage = ConsultationStage.objects.get_or_create(stage_name=row['Stage'])

            p, created = DevelopmentProject.objects.get_or_create(
                cedar_project_name=row['Title'],
                consultation_stage=consultation_stage
            )

            if row['Active'] == 'Yes':
                status = 'active'
            else:
                status = 'inactive'

            p.credar_project_name = row['Title']
            p.cedar_project_code = row['Mailharvest harvest code']
            p.status = status
            p.description = row['Project Description']
            p.government_contact = csv2peoplelist(row['Government contact(s)'])
            p.external_file_no = csv2filenolist(row['Company or Government File'])
            p.company_contact = csv2peoplelist(row['Proponent contact(s)'])

            p.save()

            if created:
                print("created project:", p)
            else:
                print("updated project:", p)
        print('\nFinished.')


def csv2filenolist(csv_string):
    filenumbers = []
    for item in csv_string.split(","):
        num, created = FileNo.objects.get_or_create(file_number=item, org_type='government')
        if created:
            print("created FileNo:", num)
        filenumbers.append(num)
    return filenumbers


def csv2peoplelist(csv_string):
    people = []
    for item in csv_string.split(","):
        pieces = item.split(" ")
        fname = pieces[0]
        lname = " ".join(pieces[1:])
        p, created = Person.objects.get_or_create(name_first=fname, name_last=lname)
        if created:
            print("created person:", p)
        people.append(p)
    return people
