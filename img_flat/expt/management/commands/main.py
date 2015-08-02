# expt.command: main.py

# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# local
from expt.models import Experiment
from expt.data import *

# util
import os
from optparse import make_option

# execute
from expt.kivy.models import *

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
    # 1. start the main kivy application

    cell_track_app = CellApp()
    cell_track_app.run()
