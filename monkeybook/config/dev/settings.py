from monkeybook.config.common_settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
COMPRESS_ENABLED = False

ALLOWED_HOSTS = ['localhost',]


## Facebook

FACEBOOK_APP_ID = '111183162379123'
FACEBOOK_APP_SECRET = 'd9afe8c407fd0577883312f8b8b23204'
FACEBOOK_CANVAS_PAGE = 'http://apps.facebook.com/yearbook_dev/'

## Stripe

STRIPE_SECRET_KEY       = 'sk_test_aUxwCNe9yrBDJz47A59fDCZx'
STRIPE_PUBLISHABLE_KEY  = 'pk_test_e32OejkBMZNS4Ow59szBFYNu'

## Mixpanel

MIXPANEL_API_TOKEN = 'd777afd9cbbb0a60d303f18ccd05ce67'

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

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'yearbook_dev',
#        'USER': 'yearbook',
#        'PASSWORD': 'yearbook',
#        'HOST': '127.0.0.1',   # empty = localhost
#        'PORT': '',   # empty = default
#    }
#}



## Sessions

SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_HOST = 'localhost'
SESSION_REDIS_PORT = 6379
SESSION_REDIS_DB = 0
SESSION_REDIS_PREFIX = 'session'

## Celery

CELERYD_POOL = 'celery.concurrency.gevent.TaskPool'
#CELERYD_CONCURRENCY = 10000
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
STATIC_ROOT = os.path.join(ROOT_PATH, 'static')
COMPRESS_ROOT = STATIC_ROOT

# URL prefix for static files.
STATIC_URL = '/static/'
#STATIC_URL = '//s3.amazonaws.com/%s/' % STATICFILES_AWS_STORAGE_BUCKET_NAME
COMPRESS_URL = STATIC_URL


## Django settings

ROOT_URLCONF = 'monkeybook.config.dev.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'monkeybook.config.dev.wsgi.application'


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

