# settings_template.py
from os.path import normpath, join
from django.conf import settings

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
IS_HAIDA = False
THUMBNAIL_DEBUG = True

# Override UTC default timezone set in settings_base.py
# TIME_ZONE = 'America/Vancouver'

# ALLOWED_HOSTS = ['*']     #  allow anyone to load a page.
# ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '209.121.136.58', '192.168.0.13']
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]',]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'django_cedar',
        'USER': 'django',
        'PASSWORD': 'this15DJANGO!!!',
        'HOST': 'localhost',
        'PORT': '5432',
    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'library.search_backend.CustomSolrEngine',
        'URL': 'http://127.0.0.1:8080/solr4/collection1'
    },
}

settings.CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    'LOCATION': 'cedar_cache',
}

# Override the default log location for communication if necessary:
# settings.LOGGING['handlers'].update(
#     {
#         'handler_for_communication': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': 'communication/logs/debug_local.log',
#             'formatter': 'cedar_verbose'
#         },
#     },
# )

# Simple values to avoid absolute paths.  These assume that the directories exist in the directory above your django project.
# e.g. /django-cedar/cedar  then /django-cedar/static etc.
STATIC_ROOT = normpath(join(settings.SITE_ROOT, 'static'))
MEDIA_ROOT = normpath(join(settings.SITE_ROOT, 'media'))
SECURE_MEDIA_ROOT = normpath(join(settings.SITE_ROOT, 'media-secure'))

# See readme for generating new key.
FIELD_ENCRYPTION_KEY = 'zu2TC0eCY27_jSK_Ta29r1ur3gGKb5Ptl0c6x-HUbYA='

# DEFAULT_USER_GROUP = 'name of role'  # The name of a group that should be assigned to all new users.

# OPENLAYERS_DRAW_ON_MAP_LON = -126
# OPENLAYERS_DRAW_ON_MAP_LAT = 54.9
# OPENLAYERS_DRAW_ON_MAP_ZOOM = 4


# DBVIEWS:
DBVIEWS_USER_ROLE = 'cedar_gis_user'

GOOGLE_OAUTH2_CLIENT_ID = "#######################################.apps.googleusercontent.com"
GOOGLE_OAUTH2_CLIENT_SECRET = "######################"

# If creating gmail mailboxes from a private device you may have to make sure your OAuth2 credentials are
# of type, "Other", and set GOOGLE_OAUTH2_PRIVATE_REDIRECT to True
#  http://stackoverflow.com/a/12004469
# This setting did not work for Me.
GOOGLE_OAUTH2_PRIVATE_REDIRECT = False

# The above private redirect didn't work for me running locally. Setting the below does. It requires a dns
# entry for the django machine so make a hosts entry for this domain and it should do.
# Set to None for machines with public IP:
# GOOGLE_OAUTH2_PRIVATE_REDIRECT_URL_OVERRIDE = 'http://geomemes-vm.example.com:8000/communication/authorize_gmail'
GOOGLE_OAUTH2_PRIVATE_REDIRECT_URL = None


# This broker url assumes rabbitmq has been set up.
# CELERY_RESULT_BACKEND="djcelery.backends.database:DatabaseBackend"
BROKER_URL = "amqp://username:password@hostname:5672/vhost"


# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # dummy backend.
'''
# Regular Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'X'
EMAIL_HOST_PASSWORD = 'X'
EMAIL_HOST_USER = 'X'
EMAIL_PORT = 587
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'X'
# SERVER_EMAIL = 'X'    # adam: I didn't need this one.
'''

'''
# Regular email backend - for traditional gmail account:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_HOST_USER = 'email@gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = 'email@gmail.com'

'''

# Gmail Email Backend - syntax error remains in smtp auth cmd.
# EMAIL_BACKEND = 'communication.utils.backends.GmailBackend'
# EMAIL_BACKEND_GMAIL_ADDRESS = 'adam@cedarbox.ca'

