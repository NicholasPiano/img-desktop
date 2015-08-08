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
from os.path import join, exists, splitext, dirname
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

  )

  args = ''
  help = ''

  def handle(self, *args, **options):

    # vars
    experiment_name = '050714'
    series_name = '13'

    if experiment_name!='' and series_name!='':
      experiment = Experiment.objects.get(name=experiment_name)
      series = experiment.series.get(name=series_name)

      # paths, image files,
      composite = series.composites.get()
      template = composite.templates.get(name='source')

      channels = ['-zbf', '-zcomp', '-zmean', '-zmod']

      for channel_name in channels:
        channel = composite.channels.get(name=channel_name)

        for path in channel.paths.all():

          old_url = path.url

          # change path.file_name, path.url
          new_file_name = template.rv.format('050714', '13', channel_name, str_value(path.t, series.ts), str_value(path.z, series.zs))
          new_url = join(dirname(old_url), new_file_name)

          print(old_url, new_file_name, new_url)
          path.file_name = new_file_name
          path.url = new_url
          path.save()

    else:
      print('Please enter an experiment')
