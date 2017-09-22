from heritage.models import Project, Interview, InterviewerId, Session, InterviewAsset, SessionAsset
from assets.models import AssetType
from crm.models import Person, Role

from django.core.files import File
import os
import csv

"""
Imports Assets and links to interview sessions.....
python manage.py runscript build_asset_import_control --script-args='<top_level_data_folder>'

top_level_data_folder: should be 'D:\GIS\Clients\Geomemes\HaidaMTK\Data\HMTK data files\HMTK2007-2009 data' or similar.
report_file = path to csv import report file that is output.


"""

skip_filename_wildcards = []
skip_fileexts = []
skip_foldernames = ['All 2007 participants', ]

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


def determine_session(name, asset_type, qs_session):
    # print ("DETERMINE SESSION::", name, asset_type, qs_session)
    # input("INPUT")
    session = None

    if asset_type.type_of_asset == 'Audio':
        for session in qs_session:
            # if name.lower() in session.audio_file_code.lower():
            if name.lower() == session.audio_file_code.lower():
                return session

        # Handle: File: 'HMTK2007_CW_015_audio01' db shows: 'HMTK2007_CW_015_audio1'
        if name[-2:].isnumeric():
            print("Audio file case 2: ADJUSTING INPUT NAME FROM", name)
            new_name = name[:-2] + str(int(name[-2:]))
            print("Audio file case 2: ADJUSTED INPUT NAME TO", new_name)
            for session in qs_session:
                # if name.lower() in session.audio_file_code.lower():
                # print ("Filename", new_name.lower(), "dbname", session.audio_file_code.lower())
                if new_name.lower() == session.audio_file_code.lower():
                    return session

        # Handle: File: 'HMTK2007_RJ_002_audio2' DB shows 'HMTK2007_RJ_002_audio02'
        if not name[-2:].isnumeric() and name[-1:].isnumeric():
            print("Audio file case 3: ADJUSTING INPUT NAME FROM", name)
            new_name = name[:-1] + str(int(name[-1:])).zfill(2)
            print("Audio file case 3: ADJUSTED INPUT NAME TO", new_name)
            for session in qs_session:
                # if name.lower() in session.audio_file_code.lower():
                # print ("Filename", new_name.lower(), "dbname", session.audio_file_code.lower())
                if new_name.lower() == session.audio_file_code.lower():
                    return session


    elif asset_type.type_of_asset == 'Transcript':
        for session in qs_session:
            if name.lower() == session.transcription_file_code.lower().strip().replace(" ", "_"):
                return session

            # Handle: 'HMTK2008_RJ_003_trans3e'
            if not name[-1].isnumeric():
                new_name = name[:-1]
                if new_name.lower() == session.transcription_file_code.lower().strip().replace(" ", "_"):
                    return session



    elif asset_type.type_of_asset == 'Index':
        # Handle: 'HMTK2008_RJ_003_index6'
        try:
            arr = name.split("_")
            indexword = arr[3]
            # Check if this is a double-digit index number eg 'HMTK2007_RJ_002_index11.doc'
            if indexword[-2:].isnumeric():
                session_num = int(indexword[-2:])
                print("Looking for index with double-digit number.", indexword)
            else:
                session_num = int(indexword[-1])

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
        # It was decided Maps/Charts are not assigned to sessions.

        # # what about: HMTK2007_CW_001_photo1.jpg --- Not part of sessions.
        # for session in qs_session:
        #     # Handle: 'HMTK2008_RJ_003_7_Chart_3002'
        #     if 'chart' in name.lower():
        #         try:
        #             # print ("Checking chart session:", name)
        #             arr = name.split("_")
        #             session_num = int(arr[3])
        #
        #             if int(session.number) == session_num:
        #                 return session
        #         except Exception as err:
        #             print ("Checking map/chart session failed:", str(err))
        #             pass

        pass

    return None


def determine_project(interview_folder):
    interview_deets = interview_folder.split(" ")
    phase_code = -100000  # We want it to fail if it doesn't find a project
    if interview_deets[0] == 'HMTK2007':
        phase_code = 1
    elif interview_deets[0] == 'HMTK2008' or interview_deets[0] == 'HMTK2009':
        phase_code = 2
    return Project.objects.get(phase_code=phase_code)


def determine_interviewer(interview_folder):
    interview_deets = interview_folder.split(" ")
    return Person.objects.filter(initials=interview_deets[1], roles__name__contains="Interviewer")


def determine_participant_number(interview_folder):
    interview_deets = interview_folder.split(" ")
    participant_number = int(interview_deets[2])
    return participant_number


def skip(path, name, ext):
    # Todo: make SKIP only accept files, not folders, amd check a file's parent folder for skipability.
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

    report_file = args[1]
    report_file = open(report_file, 'w')
    report_file = csv.writer(report_file)
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

    report_file.writerow(header)

    interviewer_role = Role.objects.filter(name='Interviewer')

    interview_folders = []
    for root, dirs, files in os.walk(top_folder):
        interview_folders = dirs
        break

    # Iterate over the interview folders:
    for interview_folder in interview_folders:

        # Determine if this is a skippable top-level folder
        # Actually the only one it skips here is "All 2007 participants":
        if skip(os.path.join(top_folder, interview_folder), None, None):
            report_row = [
                None,
                None,
                None,
                os.path.join(top_folder, interview_folder),
                None,
                None,
                None,
                True  # Skip
            ]
            report_file.writerow(report_row)
            continue
        else:
            print("Doing folder:", interview_folder)

            project = determine_project(interview_folder)

            interviewer = determine_interviewer(interview_folder)

            participant_number = determine_participant_number(interview_folder)

            interview = Interview.objects.get(phase=project, participant_number=participant_number, primary_interviewer=interviewer)
            # print (interview)

            # Get the sessions for that interview:
            qs_sessions = Session.objects.filter(interview_id=interview.id)
            # print (qs_sessions.query)

            # Walk the interview subfolders. Treat each interview folder as root:
            for root, dirs, files in os.walk(os.path.join(top_folder, interview_folder)):
                print("interview data subfolder:", root)
                for file in files:
                    full_path = os.path.join(root, file)
                    name, ext = os.path.splitext(file)

                    # Check if this is a file/folder that shouldn't be imported:
                    if skip(full_path, name, ext):
                        print("Skipping:", full_path)
                        report_row = [
                            None,
                            None,
                            None,
                            full_path,
                            name,
                            ext,
                            None,
                            True  # Skip
                        ]
                        report_file.writerow(report_row)
                        continue

                    # print ("Looking at:", file)
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
                        file_type,
                        False  # Skip
                    ]
                    if report_file:
                        report_file.writerow(report_row)

                        # f = File(file=open(full_path, 'rb'), name=file)
                        #
                        # if session is not None:
                        #     new_asset = SessionAsset(
                        #         file=f,
                        #         project=session.interview.phase,
                        #         interview=session.interview,
                        #         session=session,
                        #         name=name + ext,
                        #         asset_type=file_type)
                        #
                        # else:
                        #     new_asset = InterviewAsset(
                        #         file=f,
                        #         project=interview.phase,
                        #         interview=interview,
                        #         name=name + ext,
                        #         asset_type=file_type)

                        # new_asset.save()

    return True
