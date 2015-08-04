#!/usr/bin/env python

# django

# util
import os
import sys

if __name__ == "__main__":
  os.environ["DJANGO_SETTINGS_MODULE"] = "woot.settings"

  # apps
  import expt.models
  import img.models
  import cell.models
  import django.contrib.admin.apps
  import django.contrib.auth.apps
  import django.contrib.contenttypes.apps
  import django.contrib.sessions.apps
  import django.contrib.messages.apps
  import django.contrib.staticfiles.apps

  from django.core.management import execute_from_command_line
  execute_from_command_line(sys.argv)
