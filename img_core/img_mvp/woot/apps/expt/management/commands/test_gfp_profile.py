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
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure

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
      gfp_gon = composite.gons.get(t=t, channel__name=0)
      gfp = gfp_gon.load()
      gfp = gf(exposure.rescale_intensity(gfp * 1.0), sigma=5)

      gfp_cut = gfp[80:140,760:840,:]
      rs, cs, zs = gfp_cut.shape

      # three points for different profiles
      # background point
      # 10,10
      background_profile = scan_point(gfp_cut, rs, cs, 0, 50)
      normal_background_profile = background_profile / background_profile.max()

      plt.plot(normal_background_profile, label='background')

      # interior
      # 30, 20
      interior_profile = scan_point(gfp_cut, rs, cs, 30, 20)
      normal_interior_profile = interior_profile / interior_profile.max()

      plt.plot(normal_interior_profile, label='interior')

      # edge
      # 30, 5
      edge_profile = scan_point(gfp_cut, rs, cs, 30, 5)
      normal_edge_profile = edge_profile / edge_profile.max()

      plt.plot(normal_edge_profile, label='edge')

      # plt.imshow(gfp_cut)
      plt.ylabel('z level')
      plt.xlabel('normalised intensity')
      plt.legend()
      plt.ylim([0,1.3])
      plt.show()
