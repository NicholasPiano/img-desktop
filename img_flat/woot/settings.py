
########## IMPORT
import os
from datetime import timedelta
from os import mkdir
from os.path import abspath, basename, dirname, join, normpath, exists
from sys import path
import string
import json
import sys

from woot.django_settings import *
########## IMPORT


########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(abspath(__file__))

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION


########## APP CONFIGURATION
LOCAL_APPS = (
  'cell',
  'expt',
  'img',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS
########## END APP CONFIGURATION


########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DJANGO_ROOT, 'img_db.sqlite3'),
    }
}
########## END DATABASE CONFIGURATION
