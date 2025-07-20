#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')
    django.setup()
    
    # Now start daphne
    from daphne.cli import CommandLineInterface
    sys.argv = ['daphne', '-p', '8000', 'configs.asgi:application']
    CommandLineInterface.entrypoint()
