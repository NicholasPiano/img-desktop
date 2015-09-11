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
import shutil as sh

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

    make_option('--sigma', # option that will appear in cmd
      action='store', # no idea
      dest='sigma', # refer to this in options variable
      default='5', # some default
      help='' # who cares
    ),

    make_option('--R', # option that will appear in cmd
      action='store', # no idea
      dest='R', # refer to this in options variable
      default='5', # some default
      help='' # who cares
    ),

    make_option('--dz', # option that will appear in cmd
      action='store', # no idea
      dest='dz', # refer to this in options variable
      default='-8', # some default
      help='' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):

    # vars
    experiment_name = options['expt']
    series_name = options['series']
    sigma = int(options['sigma'])
    R = int(options['R'])
    dz = int(options['dz'])

    # 1. create experiment and series
    if experiment_name!='' and series_name!='':
      experiment = Experiment.objects.get(name=experiment_name)
      series = experiment.series.get(name=series_name)
      composite = series.composites.get()

      mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_zmod')

      # Run mod
      for sigma in [1]:
        for R in [2,3,4,5]:
          print('processing mod_zmod sigma={} R={}...'.format(sigma, R), end='\r')
          mod.run(sigma=sigma, R=R, dz=dz)
          print('processing mod_zmod sigma={} R={}... done.{}'.format(sigma, R, spacer))

    else:
      print('Please enter an experiment')
