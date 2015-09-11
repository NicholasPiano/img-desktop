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
      experiment = Experiment.objects.get(name=experiment_name)
      series = experiment.series.get(name=series_name)

      # select composite
      composite = series.composites.get()

      zbf_channel = composite.channels.get(name='-zbf-8-5-5')

      # for sigma in [1,2,3,4,5]:
      #   for R in [1,2,3,4,5]:
      #     print('-zedge-8-{}-{}'.format(R, sigma))
      #     zbf_channel.outline(composite.mask_channels.get(name__contains='-zedge-8-{}-{}'.format(R, sigma)).name)
      #
      # # bmod
      # print('bmod')
      # zbf_channel.outline(composite.mask_channels.get(name__contains='bmod').name)

      # gmod
      print('gmod')
      zbf_channel.outline(composite.mask_channels.get(name__contains='gmod').name)

    else:
      print('Please enter an experiment')
