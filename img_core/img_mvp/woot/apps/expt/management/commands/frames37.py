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
      default='260714', # some default
      help='Name of the experiment to import' # who cares
    ),

    make_option('--series', # option that will appear in cmd
      action='store', # no idea
      dest='series', # refer to this in options variable
      default='13', # some default
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
      experiment = Experiment.objects.get(name=experiment_name)
      series = experiment.series.get(name=series_name)
      composite = series.composites.get()

      for t in range(120):
        print('t={}'.format(t))

        modes = []
        for rn in ['1','2','3','pillar1','pillar2']:
          region_instance = series.region_instances.get(region__name=rn, region_track_instance__t=t)
          region_masks = region_instance.masks.all()

          mode = region_instance.mode_gray_value_id
          if mode in modes:
            print('########## CONFLICT')

          modes.append(mode)

          print('region={} mode={}'.format(region_instance.region.name, region_instance.mode_gray_value_id), end=' ')

          for rm in region_masks:
            print(rm.gray_value_id, end='')

          print('')

    else:
      print('Please enter an experiment')
