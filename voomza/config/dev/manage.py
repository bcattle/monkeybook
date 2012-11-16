#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    PROJECT_ROOT = '/home/ubuntu/src/voomza4'
    APP_ROOT = os.path.join(PROJECT_ROOT, 'voomza', 'apps')
    sys.path.append(PROJECT_ROOT)
    sys.path.append(APP_ROOT)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voomza.config.dev.settings")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
