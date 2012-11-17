from voomza.config.common_settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

## Facebook

FACEBOOK_APP_ID = '111183162379123'
FACEBOOK_APP_SECRET = 'd9afe8c407fd0577883312f8b8b23204'
FACEBOOK_CANVAS_PAGE = 'http://apps.facebook.com/yearbook_dev/'


## Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yearbook_dev',
        'USER': 'yearbook',
        'PASSWORD': 'yearbook',
        'HOST': '127.0.0.1',
        'PORT': '3306',
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
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
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
        },
        'console': {
#            'level':'DEBUG',
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        # Log everything to console
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
            },
    }
}

