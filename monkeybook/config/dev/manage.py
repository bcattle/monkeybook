#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    PROJECT_ROOT = '/home/ubuntu/src/monkeybook'
    APP_ROOT = os.path.join(PROJECT_ROOT, 'monkeybook', 'apps')
    LIB_ROOT = os.path.join(PROJECT_ROOT, 'monkeybook', 'lib')
    sys.path.append(PROJECT_ROOT)
    sys.path.append(APP_ROOT)
    sys.path.append(LIB_ROOT)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monkeybook.config.dev.settings")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
