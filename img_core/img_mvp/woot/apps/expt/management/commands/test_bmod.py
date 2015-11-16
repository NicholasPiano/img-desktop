# expt.command: step01_input

# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# local
from apps.expt.models import Series
from apps.expt.data import *
from apps.expt.util import *
from apps.img.util import cut_to_black, create_bulk_from_image_set, nonzero_mean, edge_image, scan_point

# util
import os
import numpy as np
from os.path import join, exists, splitext
from optparse import make_option
from subprocess import call
import matplotlib.pyplot as plt
from scipy.misc import imsave

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
      default='15', # some default
      help='Name of the series' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):

    # vars
    experiment_name = options['expt']
    series_name = options['series']
    out = '/Users/nicholaspiano/Desktop/out'
    series = Series.objects.get(name='15')
    composite = series.composites.get()

    for t in [112]:

    # load brightfield stack
      bf_gon = composite.gons.get(t=t, channel__name=1)
      bf = bf_gon.load()

      Zmean = bf[:,:,37]

      imsave(join(out, '260714_s15_constant37_{}.tiff'.format(t)), Zmean)
