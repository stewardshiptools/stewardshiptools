from heritage.models import Project, Interview, InterviewerId, Session, InterviewAsset, SessionAsset
from assets.models import AssetType
from crm.models import Person, Role

from django.core.files import File
import os
import csv

"""
Imports Assets and links to interview sessions.....
python manage.py runscript import_assets --script-args='<top_level_data_folder>' '<only_one_interview>'

top_level_data_folder: should be 'D:\GIS\Clients\Geomemes\HaidaMTK\Data\HMTK data files\HMTK2007-2009 data' or similar.
only_one_interview = can be used to restrict the import to only one interview. So 'HMTK2009 RJ 003 Ernie Wilson'
                    supply 'all' and the script will process all interview folders
report_file = path to csv import report file that is output.


"""

skip_filename_wildcards = []
skip_fileexts = []
skip_foldernames = ['Drafts', 'Drafts 1', 'Drafts 2', 'Drafts 3', 'All 2007 participants']

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

    print("Asset Type Is:", asset_type.type_of_asset)
    return asset_type


def determine_session(name, asset_type, qs_session):
    # print ("DETERMINE SESSION::", name, asset_type, qs_session)
    # input("INPUT")
    session = None

    if asset_type.type_of_asset == 'Audio':
        for session in qs_session:
            if name.lower() in session.audio_file_code.lower():
                return session
    elif asset_type.type_of_asset == 'Transcript':
        for session in qs_session:
            # Handle: 'HMTK2008_RJ_003_trans3e'
            if session.transcription_file_code.lower().strip().replace(" ", "_") in name.lower():
                return session
    elif asset_type.type_of_asset == 'Index':
        # Handle: 'HMTK2008_RJ_003_index6'
        try:
            arr = name.split("_")
            session_num = int(arr[3][-1])
            for session in qs_session:
                if int(session.number) == session_num:
                    return session

        except ValueError:
            print("Index file had bad session number")
            pass

    elif asset_type.type_of_asset == 'Bio':
        # Do not have session numbers.
        pass

    elif asset_type.type_of_asset == 'Map':
        # what about: HMTK2007_CW_001_photo1.jpg --- Not part of sessions.
        for session in qs_session:
            # Handle: 'HMTK2008_RJ_003_7_Chart_3002'
            if 'chart' in name.lower():
                try:
                    # print ("Checking chart session:", name)
                    arr = name.split("_")
                    session_num = int(arr[3])

                    if int(session.number) == session_num:
                        return session
                except Exception as err:
                    print("Checking map/chart session failed:", str(err))
                    pass
    return None


def skip(path, name, ext):
    # Test file name:
    try:
        if name[0] == '.':
            return True
        elif name[0] == '_.':
            return True
    except IndexError:
        pass
    except TypeError:
        pass

    # If this is a file, see if it's parent is skippable:
    if os.path.isfile(path):
        if os.path.split(os.path.dirname(path))[-1].lower() in [folder.lower() for folder in skip_foldernames]:  # Ugly, I know
            return True
    elif os.path.isdir(path):
        if os.path.split(path)[-1].lower() in [folder.lower() for folder in skip_foldernames]:
            return True

    # This is not a skipper if we make it this far
    return False


def run(*args):
    print("Begin asset import...")

    top_folder = args[0]
    # top_folder = r'/home/geomemes/HMTK_data_files/HMTK2007-2009 data'
    try:
        only_one_interview = args[1]
        if only_one_interview == 'all': only_one_interview = None  # Allows us to supply "all" and a csv file and it will
        # process all folders.
    except IndexError:
        only_one_interview = None

    try:
        report_file = args[2]
        report_file = open(report_file, 'w')
        report_file = csv.writer(report_file)
        header = [
            'project',
            'interview',
            'session',
            'filepath',
            'filename',
            'file_ext',
            'asset_type'
        ]

        report_file.writerow(header)

    except:
        print("Running without creating output file.")
        report_file = None

    interviewer_role = Role.objects.filter(name='Interviewer')

    interview_folders = []
    for root, dirs, files in os.walk(top_folder):
        interview_folders = dirs
        break

    # Iterate over the interview folders:
    for interview_folder in interview_folders:

        # Skip this folder if the only_one_interview arg was specified and this is
        # not that folder.
        if only_one_interview is not None and interview_folder != only_one_interview:
            continue
        elif skip(os.path.join(top_folder, interview_folder), None, None):
            continue
        else:
            print("Doing folder:", interview_folder)

            interview_deets = interview_folder.split(" ")

            project = Project.objects.get(phase_code=interview_deets[0])
            interviewer_initials = interview_deets[1]
            interview_number = int(interview_deets[2])

            # The interviewer table is wonky in the other imports scripts,
            # wonkifying here too. It should refer to the "Person" objects, not the
            # interviewer ID object:

            # Correct: Get the interview and interviewer objects:
            # interviewer = Person.objects.get(initials=interviewer_initials, roles=interviewer_role)
            # print (interviewer.id)

            # Wonky:
            interviewer = InterviewerId.objects.get(interviewer_id=interviewer_initials)
            print(interviewer.id)

            interview = Interview.objects.get(phase=project, interview_number=interview_number, interviewer_id_id=interviewer.id)
            print(interview)

            # Get the sessions for that interview:
            qs_sessions = Session.objects.filter(interview_id=interview.id)
            # print (qs_sessions.query)

            # Walk the interview subfolders. Treat each interview folder as root:
            for root, dirs, files in os.walk(os.path.join(top_folder, interview_folder)):
                print("interview data subfolder:", root)
                for file in files:
                    full_path = os.path.join(root, file)
                    name, ext = os.path.splitext(file)

                    # Check if this is a file/folder we should that shouldn't be imported:
                    if skip(full_path, name, ext):
                        print("Skipping:", full_path)
                        continue

                    if '.DS_Store' not in file:
                        print("Looking at:", file)
                        file_type = determine_type(file)

                        session = determine_session(name, file_type, qs_sessions)

                        # if session is not None:
                        #     print (" to session id/number :", session.id, '/', session.number)
                        # else:
                        #     print ("session not discovered.")

                        print("Adding:", file,
                              "to project:", project,
                              "interview:", interview,
                              "session:", session,
                              "type:", file_type)

                        report_row = [
                            project.phase_code,
                            interview,
                            session,
                            full_path,
                            name,
                            ext,
                            file_type
                        ]
                        if report_file:
                            report_file.writerow(report_row)

                        f = File(file=open(full_path, 'rb'), name=file)

                        if session is not None:
                            new_asset = SessionAsset(
                                file=f,
                                project=session.interview.phase,
                                interview=session.interview,
                                session=session,
                                name=name + ext,
                                asset_type=file_type)

                        else:
                            new_asset = InterviewAsset(
                                file=f,
                                project=interview.phase,
                                interview=interview,
                                name=name + ext,
                                asset_type=file_type)

                        new_asset.save()

    return True
