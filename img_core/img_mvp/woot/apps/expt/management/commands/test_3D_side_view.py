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
from scipy.ndimage.filters import gaussian_filter as gf

spacer = ' ' *  20

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='050714', # some default
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
    out = '/Users/nicholaspiano/Desktop/out'
    series = Series.objects.get()
    composite = series.composites.get()

    # load brightfield stack
    gfp_gon = composite.gons.get(t=0, channel__name=0)
    gfp = gfp_gon.load()
    gfp = gf(gfp, sigma=1)

    # interior point
    r, c = 470, 276
    data_interior = scan_point(gfp, composite.series.rs, composite.series.cs, r, c, size=1)
    normalised_data_interior = np.array(data_interior) / np.max(data_interior)

    plt.plot(gf(normalised_data_interior, sigma=3), np.arange(len(normalised_data_interior)))
    plt.ylabel('Z (focal planes)')
    plt.xlabel('normalised intensity')
    # plt.show()

    side_view = gfp[470, 250:300, :]
    # plt.imshow(side_view, cmap='Greys_r')
    plt.show()
