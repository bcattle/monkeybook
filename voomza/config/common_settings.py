import djcelery
djcelery.setup_loader()

## Our app settings

YEARBOOK_HASH_LENGTH = 10


## Installed aps

OUR_APPS = (
    'account',
    'core',
    'yearbook',
    'backend',
    'store',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'south',
    'djcelery',
    'django_facebook',
#    'dajaxice',
    'compressor',
)
INSTALLED_APPS += OUR_APPS

## Auth

AUTH_PROFILE_MODULE = 'account.UserProfile'
LOGIN_URL = '/'


## Facebook

FACEBOOK_DEFAULT_SCOPE = [
    'email',
    'user_birthday',
    'user_relationships',
    'user_likes',
    'user_photos',
    'user_photo_video_tags',
    'user_location',
    'user_checkins',
    'user_status',
    'friends_likes',
    'friends_photos',
    'friends_photo_video_tags',
#    'friends_status',
    'read_stream',
    # TODO:
#    'publish_actions',
]

FACEBOOK_STORE_LOCAL_IMAGE = False
FACEBOOK_STORE_LIKES = False
FACEBOOK_STORE_FRIENDS = False      # Suppress this in the fb app, we do it ourselves
FACEBOOK_CELERY_STORE = True
FACEBOOK_CELERY_TOKEN_EXTEND = True


## Amazon AWS

AWS_ACCESS_KEY_ID = 'AKIAJNKCFRLQ6NGG44AQ'
AWS_SECRET_ACCESS_KEY = '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'

from boto.s3.connection import OrdinaryCallingFormat
AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()
AWS_QUERYSTRING_AUTH = False


## Admins

ADMINS = (
    ('Voomza Admin', 'admin@voomza.com'),
    ('Bryan Cattle', 'bryan@voomza.com'),
)
MANAGERS = ADMINS


## Paths and locations

import os
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

TEMPLATE_DIRS = (
#    os.path.join(ROOT_PATH, 'templates'),
)

# Additional locations of static files
STATICFILES_DIRS = (
    # use absolute paths
    os.path.join(ROOT_PATH, 'assets'),
    )

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
#    'dajaxice.finders.DajaxiceFinder',
)


## General Django settings

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-a66lr&amp;kmv+ubi@y_prjq*m#ryoo*8bk$pee@$h^*vm%ek)#)-'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.http.ConditionalGetMiddleware',
#     'django.middleware.gzip.GZipMiddleware',
)

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += (
    'django_facebook.context_processors.facebook',
    'django.core.context_processors.request',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_facebook.auth_backends.FacebookBackend',
)
