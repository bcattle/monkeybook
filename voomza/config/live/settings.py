from voomza.config.common_settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

## Facebook

FACEBOOK_APP_ID = '524135734282912'
FACEBOOK_APP_SECRET = 'dc7bf6738d5ed766c8f780705c43fc8f'
FACEBOOK_CANVAS_PAGE = 'http://apps.facebook.com/yearbook/'

## Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yearbook_dev',
        'USER': 'yearbook',
        'PASSWORD': '8jmrnBsP',
        'HOST': 'rds-my-yearbook.cnqssbbdxaki.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
        }
}

## Sessions

SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_HOST = 'localhost'
SESSION_REDIS_PORT = 6379
SESSION_REDIS_DB = 0
SESSION_REDIS_PREFIX = 'session'

## Celery

CELERYD_POOL = 'celery.concurrency.gevent.TaskPool'
CELERYD_CONCURRENCY = 1000
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = BROKER_URL


## Static files storage

# Path for uploaded files
MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')

# URL prefix for media (uploaded) files
MEDIA_URL = '/media/'
#MEDIA_URL = '//s3.amazonaws.com/%s/' % AWS_STORAGE_BUCKET_NAME

# Needed for compressor's local cache?
STATIC_ROOT = '/home/ubuntu/src/voomza_static/'
COMPRESS_ROOT = STATIC_ROOT

# URL prefix for static files.
STATIC_URL = '/static/'
#STATIC_URL = '//s3.amazonaws.com/%s/' % STATICFILES_AWS_STORAGE_BUCKET_NAME
COMPRESS_URL = STATIC_URL


## Django settings

ROOT_URLCONF = 'voomza.config.live.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'voomza.config.live.wsgi.application'


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

