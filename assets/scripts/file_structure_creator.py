# _____________________________________________________________________
# File_structure_creator.py.
# Purpose: Creates folders and 0-size files for all files in input list
# Arg 1: input file list
# Arg 2: output folder
# _____________________________________________________________________

# python manage.py runscript file_structure_creator --script-args=/home/geomemes/projects/cedar/fake/herring_filelist.txt "/home/geomemes/projects/cedar/fake/Herring Interviews 1998"
# python /home/geomemes/projects/cedar/cedar/scripts/file_structure_creator.py /home/geomemes/projects/cedar/fake/herring_filelist.txt "/home/geomemes/projects/cedar/fake/Herring Interviews 1998"
# python /home/geomemes/projects/cedar/assets/scripts/file_structure_creator.py /home/geomemes/projects/cedar/fake/charts_filelist.txt "/home/geomemes/projects/cedar/fake/"
# python /home/geomemes/projects/cedar/assets/scripts/file_structure_creator.py /home/geomemes/projects/cedar/fake/HMTK2007-2009_general_files_filelist.txt "/home/geomemes/projects/cedar/fake/"
# python /home/geomemes/projects/cedar/assets/scripts/file_structure_creator.py /home/geomemes/projects/cedar/fake/HMTK2007-2009_unsorted_data_filelist.txt "/home/geomemes/projects/cedar/fake/"
# python /home/geomemes/projects/cedar/assets/scripts/file_structure_creator.py /home/geomemes/projects/cedar/fake/Spatial_admin_documents_filelist.txt "/home/geomemes/projects/cedar/fake/"
# python /home/geomemes/projects/cedar/assets/scripts/file_structure_creator.py /home/geomemes/projects/cedar/fake/Stu_files_data_organizing.xlsx_filelist.txt "/home/geomemes/projects/cedar/fake/"
# python /home/geomemes/projects/cedar/assets/scripts/file_structure_creator.py /home/geomemes/projects/cedar/fake/Verification_sessions_filelist.txt "/home/geomemes/projects/cedar/fake/"

# _____________________________________________________________________



import os
import sys


def run(*args):
    filelist_path = args[0]
    outfolder = args[1]

    filelist = open(filelist_path).readlines()

    print("filelist:", filelist_path)
    print("outfolder:", outfolder)

    for filepath in filelist:
        # newpath = str(filepath).replace(r'//GEONAS1/haida-mtk/', '').strip()
        newpath = str(filepath).replace(r'/data/hmtk-data/HMTK data files/', '').strip()
        basedir = os.path.join(os.path.dirname(newpath), outfolder)
        print('basedir:', basedir)
        newfile = os.path.join(basedir, newpath)
        newdir = os.path.dirname(newfile)

        print("newfile:", newfile)
        if not os.path.exists(newdir):
            os.makedirs(newdir)

        print(newpath)
        open(os.path.join(outfolder, newpath), 'a').close()


if __name__ == '__main__':
    # shift args for django:
    args = [sys.argv[1], sys.argv[2]]
    run(*args)
