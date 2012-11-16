from voomza.config.common_settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

## Facebook

FACEBOOK_APP_ID = '111183162379123'
FACEBOOK_APP_SECRET = 'd9afe8c407fd0577883312f8b8b23204'

## Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'kombu_test',                      # Or path to database file if using sqlite3.
        'USER': 'kombu_test',                      # Not used with sqlite3.
        'PASSWORD': 'kombu_test',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}

## Celery

#CELERYD_CONCURRENCY = 2            # By default, the number of CPUs is used

# DB-backed
BROKER_URL = 'django://'
CELERY_RESULT_BACKEND = 'database'
CELERY_RESULT_DBURI = 'mysql://%s:%s@%s:%s/%s' % (
    DATABASES['default']['USER'],
    DATABASES['default']['PASSWORD'],
    DATABASES['default']['HOST'],
    DATABASES['default']['PORT'],
    DATABASES['default']['NAME']
)


## Static files storage

# Path for uploaded files
MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')

# URL prefix for media (uploaded) files
MEDIA_URL = '/media/'
#MEDIA_URL = '//s3.amazonaws.com/%s/' % AWS_STORAGE_BUCKET_NAME

# Needed for compressor's local cache?
STATIC_ROOT = os.path.join(ROOT_PATH, 'static')
COMPRESS_ROOT = STATIC_ROOT

# URL prefix for static files.
STATIC_URL = '/static/'
#STATIC_URL = '//s3.amazonaws.com/%s/' % STATICFILES_AWS_STORAGE_BUCKET_NAME
COMPRESS_URL = STATIC_URL


## Django settings

ROOT_URLCONF = 'voomza.config.dev.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'voomza.config.dev.wsgi.application'


## Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        }
}

