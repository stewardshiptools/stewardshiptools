########################################################################
# File_List.py.
# Purpose:
########################################################################

import shutil
import os
import sys
import csv
import zipfile
from assets.models import AssetType

# indir = '/home/geomemes/projects/cedar/filelists'
# outdir = '/home/geomemes/projects/cedar/filelists_out'

# infile = csv.reader(open(r'/home/geomemes/projects/cedar/cedar/scripts/data/HMTK_Charts_for_zip_OUT.csv', 'r'))
# infile = csv.reader(open(r'assets/scripts/data/HMTK_Charts_for_zip_OUT.csv', 'r'))
infile = csv.reader(open(r'assets/scripts/data/vid_files_for_zip_list_OUT.csv', 'r'))


def run(*args):
    # Skip header:
    next(infile)

    for row in infile:
        # print("row:", row)
        source_file = row[0]
        destination_file = row[1]
        doZip = row[2]

        # Get the source filename to save in the archive:
        srcfolder, archivename = os.path.split(source_file)

        # Redirect destination to substituted file path:
        # destination_file = destination_file.replace(path_substitution_A, path_substitution_B)

        # Get output dir and make it if it doesn't exist:
        destfolder, destfilename = os.path.split(destination_file)
        if not os.path.exists(destfolder):
            os.makedirs(destfolder)

        if doZip == "FALSE":
            # Straight copy the file to the output location
            print("Copying", source_file, "to", destination_file)
            shutil.copy2(source_file, destination_file)
        else:
            print("Zipping", source_file, "into", destination_file)
            with zipfile.ZipFile(destination_file, 'a') as thezip:
                thezip.write(source_file, archivename)
