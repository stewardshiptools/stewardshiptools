########################################################################
# File_List.py.
# Purpose: Prints all input_file names in supplied directory to a csv input_file.
# Arg 1: input directory
# Arg 2: output directory
# Arg 3: recursive TRUE/FALSE
# Arg 4: extension (eg. ".tif") --- optional.
########################################################################


import os
import sys
import csv
from assets.models import AssetType

indir = '/home/geomemes/projects/cedar/filelists'
outdir = '/home/geomemes/projects/cedar/filelists_out_1'

audio_types = ('.mp3', '.wav', '.aiff', '.aif')
video_types = ('.vob', '.dv', '.m2v',)
image_types = ('.jpg', '.jpeg', '.png', '.gif', '.tif', '.tiff')
document_types = ('.doc', '.docx', '.pdf')


def determine_type(filename):
    # types = Asset._meta.get_field('type').choices
    name, ext = os.path.splitext(filename)

    ext = ext.lower()
    asset_type = None

    if ext in audio_types:
        asset_type = AssetType.objects.get(type_of_asset='Audio')
    elif ext in video_types:
        asset_type = AssetType.objects.get(type_of_asset='Video')
    elif ext in image_types:
        if 'chart' in filename.lower():
            asset_type = AssetType.objects.get(type_of_asset='Map')
        elif 'map' in filename.lower():
            asset_type = AssetType.objects.get(type_of_asset='Map')
        else:
            asset_type = AssetType.objects.get(type_of_asset='Photo')
    elif ext in document_types:
        if "trans" in name.lower():
            asset_type = AssetType.objects.get(type_of_asset='Transcript')
        elif "bio" in name.lower():
            asset_type = AssetType.objects.get(type_of_asset='Bio')
        elif "notes" in name.lower():
            asset_type = AssetType.objects.get(type_of_asset='Note')
        elif "index" in name.lower():
            asset_type = AssetType.objects.get(type_of_asset='Index')
        else:
            asset_type = AssetType.objects.get(type_of_asset='Document')
    else:
        asset_type = AssetType.objects.get(type_of_asset='Uncategorized')

    # print ("Asset Type Is:", asset_type.type_of_asset)
    return asset_type


def run(*args):
    for root, dirs, files in os.walk(indir):
        print("root:", root)
        for file in files:
            print("reading file", file)
            infile = open(os.path.join(root, file), 'r')
            outfile = csv.writer(open(os.path.join(outdir, file), 'w'))
            outfile.writerow(
                ["project_phase_code", "interview", "session", "filepath", "filename", "file_ext", "asset_type", "skip", "QC", "QCComment",
                 "Draft Check"])

            for line in infile.readlines():
                filepath = line.strip()
                head, tail = os.path.split(filepath)
                name, ext = os.path.splitext(tail)
                asset_type = determine_type(tail)
                outfile.writerow(['', '', '', filepath, name, ext, asset_type, '', '', '', ''])

        break
