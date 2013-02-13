from voomza.config.common_settings import *

DEBUG = True
#DEBUG = False
TEMPLATE_DEBUG = DEBUG
#COMPRESS_ENABLED = True

## Facebook

FACEBOOK_APP_ID = '113413968821031'
FACEBOOK_APP_SECRET = '8b1adb6503a4590eb3d2c4e7409357ee'
FACEBOOK_CANVAS_PAGE = 'http://apps.facebook.com/yearbook_allstar'

## Stripe

STRIPE_SECRET_KEY       = 'sk_test_aUxwCNe9yrBDJz47A59fDCZx'
STRIPE_PUBLISHABLE_KEY  = 'pk_test_e32OejkBMZNS4Ow59szBFYNu'
#STRIPE_SECRET_KEY       = 'sk_live_A4Ycn1r9hbZnYlABFRqoEiq4'
#STRIPE_PUBLISHABLE_KEY  = 'pk_live_4l4RVHNEZtCWbpJF3Azel5oY'

## Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yearbook_live',
        'USER': 'yearbook',
        'PASSWORD': '8jmrnBsP',
        'HOST': 'yearbook-live.cnqssbbdxaki.us-west-2.rds.amazonaws.com',
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


## S3 storage

AWS_STORAGE_BUCKET_NAME = 'yearbook-allstar'
#DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
DEFAULT_FILE_STORAGE = 'voomza.apps.core.storage.CachedS3BotoStorage'
STATICFILES_STORAGE = DEFAULT_FILE_STORAGE
COMPRESS_STORAGE = DEFAULT_FILE_STORAGE

## Static files storage

# Path for uploaded files
MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')

# URL prefix for media (uploaded) files
MEDIA_URL = '/media/'

# Needed for compressor's local cache?
STATIC_ROOT = '/home/ubuntu/src/voomza_static/'
#COMPRESS_ROOT = STATIC_ROOT

# URL prefix for static files.
#STATIC_URL = '/static/'
STATIC_URL = '//s3-us-west-2.amazonaws.com/%s/' % AWS_STORAGE_BUCKET_NAME
#COMPRESS_URL = STATIC_URL


## Django settings

ROOT_URLCONF = 'voomza.config.live.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'voomza.config.live.wsgi.application'


## Raven / Sentry configuration

#RAVEN_CONFIG = {
#    'dsn': 'https://0212e4c55eaa40379c1ba782c8137510:96e96df4f883498d83a130c86e965db0@sentry.voomza.com/2',
#}


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

