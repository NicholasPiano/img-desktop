# expt.command: step01_input

# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# local
from apps.expt.models import Experiment
from apps.expt.data import *
from apps.expt.util import *
from apps.expt.pipeline import marker_pipeline

# util
import os
import re
from os.path import join, exists, splitext
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

    pipeline = marker_pipeline('260714_s13_7OFMC9VV_', '-zcomp-zedge-7OFMC9VV', 's13_ch-zcomp-primary-7OFMC9VV', 's13_ch-zedge')

    out_path = '/Volumes/transport/data/puzzle/260714/pipelines/test.cppipe'

    # pipeline = region_pipeline('s14_ch-zbf-regionprimary-8C3WCS1E', 's14_ch-zbf')

    with open(out_path, 'w+') as f:
      f.write(pipeline)
