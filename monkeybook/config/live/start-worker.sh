#!/bin/bash

# Path, settings
WEBAPP_ROOT="/home/ubuntu/src"
PROJECT_ROOT="$WEBAPP_ROOT/monkeybook"
APP_ROOT="$PROJECT_ROOT/monkeybook"
export PYTHONPATH="$PYTHONPATH:$PROJECT_ROOT:$APP_ROOT:$APP_ROOT/apps:$APP_ROOT/lib"
export DJANGO_SETTINGS_MODULE=monkeybook.config.live.settings

# Activate virtualenv
source $PROJECT_ROOT/venv/bin/activate

echo `which python`

# Run
exec ./manage.py celery worker -l INFO -f ~/celery_info.log -n ubuntu1
#exec ./manage.py celery worker -l DEBUG -f /var/log/celery_debug.log
