#!/usr/bin/env python

# django

# util
import os
import sys

# apps
import expt
import img
import cell

if __name__ == "__main__":
  os.environ["DJANGO_SETTINGS_MODULE"] = "woot.settings"
  import django.contrib.admin.apps
  from expt.exec import run

  from django.core.management import call_command
  call_command('syncdb', interactive=False)

  # run()
  # from django.core.management import execute_from_command_line
  # execute_from_command_line(sys.argv)
