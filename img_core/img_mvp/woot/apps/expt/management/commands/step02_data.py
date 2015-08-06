# expt.command: step01_input

# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# local
from apps.expt.models import Experiment
from apps.expt.data import *
from apps.expt.util import *

# util
import os
from os.path import join, exists
from optparse import make_option
from subprocess import call

spacer = ' ' *  20

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='', # some default
      help='Name of the experiment to import' # who cares
    ),

    make_option('--series', # option that will appear in cmd
      action='store', # no idea
      dest='series', # refer to this in options variable
      default='', # some default
      help='Name of the series' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):

    # vars
    experiment_name = options['expt']
    series_name = options['series']

    if experiment_name!='' and series_name!='':
      # 1. Convert track files to csv
      def convert_track_file(file_name):
        pass

      # for each track file in the track directory, if there is not a .csv file with the same name, then translate it into the new format
      

      # 2. Import tracks

      # 3. Segment ZCOMP channel

      # 4. Export data to data directory

    else:
      print('Please enter an experiment')
