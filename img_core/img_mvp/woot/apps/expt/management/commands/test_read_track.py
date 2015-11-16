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
  option_list = BaseCommand.option_list + ()

  args = ''
  help = ''

  def handle(self, *args, **options):

    # vars
    base_path = '/Users/nicholaspiano/Desktop/out'
    in_path = join(base_path, 'track.xls')
    out_path = join(base_path, 'track')

    names = [61,62,68,69,70,80]

    def convert_track_file(path):
      frames = {} # by frame
      tracks = {} # stores list of tracks that can then be put into the database

      with open(path, 'rb') as track_file:

        lines = track_file.read().decode('mac-roman').split('\n')[1:-1]
        for i, line in enumerate(lines): # omit title line and final blank line
          line = line.split('\t')

          # details
          track_id = int(float(line[1]))
          r = int(float(line[4]))
          c = int(float(line[3]))
          t = int(float(line[2])) - 1

          if track_id in tracks:
            tracks[track_id].append((r,c,t))
          else:
            tracks[track_id] = [(r,c,t)]

          if t in frames:
            frames[t].append((r,c))
          else:
            frames[t] = [(r,c)]

      return frames

    frames = convert_track_file(in_path)

    for frame in frames:
      point_list = frames[frame]

      blank = np.zeros((512,1024))

      for r,c in point_list:
        blank[r-3:r+2,c-3:c+2] = 255

      imsave(join(out_path, 'track_{}.tiff'.format(str_value(frame, len(frames)))), blank)
