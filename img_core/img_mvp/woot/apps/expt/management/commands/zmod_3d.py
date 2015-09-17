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
from skimage import exposure
import numpy as np
from scipy.misc import imsave
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter as gf

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

    # 1. create experiment and series
    if experiment_name!='' and series_name!='':
      experiment = Experiment.objects.get(name=experiment_name)
      series = experiment.series.get(name=series_name)
      composite = series.composites.get()

      gfp_gon = composite.gons.get(channel__name='0', t=0)
      gfp = gfp_gon.load()
      gfp = exposure.rescale_intensity(gfp * 1.0)
      # gfp = gf(gfp, sigma=1)


      for i in range(gfp.shape[2]):
        imsave(join(experiment.plot_path, 'gfp_{}.png'.format(i)), gfp[:,:,i])

    else:
      print('Please enter an experiment')
