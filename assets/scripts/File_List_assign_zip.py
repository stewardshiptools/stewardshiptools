########################################################################
# File_List.py.
# Purpose:
########################################################################


import os
import sys
import csv

# infile = open(r'/home/geomemes/projects/cedar/cedar/scripts/data/HMTK_Charts_for_zip.csv', 'r')
# outfile = csv.writer(open(r'/home/geomemes/projects/cedar/cedar/scripts/data/HMTK_Charts_for_zip_OUT.csv', 'w'))

infile = open(r'assets/scripts/data/vid_files_for_zip_list.csv', 'r')
outfile = csv.writer(open(r'assets/scripts/data/vid_files_for_zip_list_OUT.csv', 'w'))
outfile.writerow(["SOURCE", "DESTINATION", "ZIP"])

# python manage.py runscript File_List_assign_zip

# After running, you should update the DESTINATION filepath to a new top-level folder

output_archive_files = {}


def run(*args):
    for line in infile.readlines():
        filepath = line.strip()
        head, filename = os.path.split(filepath)

        # Check for multiple file extensions in file name.
        arr = filename.split(".")
        name_no_ext = arr[0]

        output_archive = os.path.join(head, name_no_ext + ".zip")

        # print(filename)

        if not output_archive in output_archive_files.keys():
            output_archive_files[output_archive] = [filepath, ]
        else:
            output_archive_files[output_archive].append(filepath)

    # Check for files that shouldn't be zipped.
    non_zippers = {}
    for archive in output_archive_files.keys():
        zip_list = output_archive_files[archive]

        if len(zip_list) == 1:
            # print("we got a winner here. pop off archive and replace with original.")
            filename = zip_list[0]
            non_zippers[archive] = filename

    for archive in non_zippers:
        output_archive_files.pop(archive)
        output_archive_files[non_zippers[archive]] = [non_zippers[archive], ]

    for archive in output_archive_files.keys():
        for filepath in output_archive_files[archive]:
            zip = not filepath == archive
            outfile.writerow([filepath, archive, zip])
