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
    bf_gon = composite.gons.get(t=0, channel__name=1)
    bf = bf_gon.load()

    # scan
    # data = scan_point(bf, composite.series.rs, composite.series.cs, r, c, size=1)
    # normalised_data = np.array(data) / np.max(data)

    bf37 = bf[:,:,37]
    display = np.dstack([bf37,bf37,bf37])

    # dark edge point
    r, c = 462, 276
    data_dark_edge = scan_point(bf, composite.series.rs, composite.series.cs, r, c, size=1)
    normalised_data_dark_edge = np.array(data_dark_edge) / np.max(data_dark_edge)

    # interior point
    r, c = 470, 276
    data_interior = scan_point(bf, composite.series.rs, composite.series.cs, r, c, size=1)
    normalised_data_interior = np.array(data_interior) / np.max(data_interior)

    # background point
    r, c = 440, 276
    data_background = scan_point(bf, composite.series.rs, composite.series.cs, r, c, size=1)
    normalised_data_background = np.array(data_background) / np.max(data_background)

    # plot
    plt.plot(normalised_data_dark_edge, label='dark edge')
    plt.plot(normalised_data_interior, label='interior')
    plt.plot(normalised_data_background, label='background')
    plt.legend()
    plt.ylabel('normalised intensity')
    plt.xlabel('Z (focal plane)')
    plt.show()

    # display[r,c,0] = 255
    # plt.imshow(display)
    # plt.show()
