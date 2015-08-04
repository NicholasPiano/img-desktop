# expt.command: main.py

# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core import management

# local
from expt.models import Experiment
from expt.data import *

# util
import os
from optparse import make_option
import asyncio
import pythrust
import subprocess

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='050714-test', # some default
      help='Name of the experiment to import' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):

    # a number of things to do in this script.
    loop = asyncio.get_event_loop()
    api = pythrust.API(loop)

    asyncio.async(api.spawn())
    asyncio.async(api.window({'root_url': 'http://localhost:8000' }).show())

    loop.run_forever()
