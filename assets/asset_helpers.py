# asset_helpers.py
# Functions to help manage asset files.

import logging

from django.core.files.storage import FileSystemStorage
from django.conf import settings
from cedar_settings.models import GeneralSetting

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# I put the generate file name method here to reduce clutter
# in models.py. Could just as well be in models.py.


# Used by Asset and SecureAsset models to set the upload (ie storage) location.
def generate_asset_file_name(instance, filename):
    # In case the storage_string hasn't been set
    # return just the file name (or else an errant '/'
    # will mess it all up.
    if instance.storage_string is None:
        return filename
    else:
        # Do not to use os.join here.
        return '/'.join([instance.storage_string, filename])


# Used by asset child models to figure out their folder paths.
def generate_heritage_project_asset_storage_string(project_obj):
    return "assets_project_" + str(project_obj.id)


# Used by asset child models to figure out their folder paths.
def generate_heritage_interview_asset_storage_string(interview_obj):
    project_string = generate_heritage_project_asset_storage_string(interview_obj.phase)
    interview_string = "assets_interview_" + str(interview_obj.id)
    return '/'.join([project_string, interview_string])


# Used by asset child models to figure out their folder paths.
def generate_heritage_session_asset_storage_string(session_obj):
    interview_string = generate_heritage_interview_asset_storage_string(session_obj.interview)
    session_string = "assets_session_" + str(session_obj.id)
    return '/'.join([interview_string, session_string])


def generate_project_asset_storage_string(project_obj):
    return "assets_project_" + str(project_obj.id)


# Generates human-readable file size string
# Useful in api stuff -- otherwise use the django
# template tags for this.
# http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
# or use humanize module.
def sizeof_fmt(num, suffix='B'):
    # suffixes = ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']
    suffixes = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']
    for unit in suffixes:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


###############################################################################
# Define secure file storage object using paths set in app settings.
# Used by the SecureAsset model.
# Secure assets can't be served by using the regular base_url (they would fail), so set it to None.
secure_file_storage = FileSystemStorage(location=settings.SECURE_MEDIA_ROOT, base_url=None)
