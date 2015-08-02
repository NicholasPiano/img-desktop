#!/usr/bin/env python

# util
import os
import sys

# apps
import expt
import img
import cell

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "woot.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
