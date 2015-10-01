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
import numpy as np
from os.path import join, exists, splitext
from optparse import make_option
from subprocess import call
import matplotlib.pyplot as plt

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

    make_option('--cells', # option that will appear in cmd
      action='store', # no idea
      dest='cells', # refer to this in options variable
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
    cell_groups = options['cells'].split(';')

    if experiment_name!='' and series_name!='':
      experiment = Experiment.objects.get(name=experiment_name)
      series = experiment.series.get(name=series_name)

      # select composite
      composite = series.composites.get()

      # template
      template = composite.templates.get(name='mask')

      # image root
      root = experiment.composite_path

      # 1. convert cell groups to dictionary
      cell_dictionary = {}
      for group in cell_groups:
        parsed_group = [int(value) for value in group[1:-1].split(',')]
        cell_id = parsed_group[0]
        cell = series.cells.get(pk=cell_id)

        if len(parsed_group)==1:
          # add all cell instances to cell_dictionary
          for cell_instance in cell.instances.all():
            if cell_instance.t in cell_dictionary:
              cell_dictionary[cell_instance.t].append(cell_instance.pk)
            else:
              cell_dictionary[cell_instance.t] = [cell_instance.pk]

        else:
          t = parsed_group[1]
          cell_instance = cell.instances.get(t=t)
          if cell_instance.t in cell_dictionary:
            cell_dictionary[cell_instance.t].append(cell_instance.pk)
          else:
            cell_dictionary[cell_instance.t] = [cell_instance.pk]

      # 2. load each frame and delete from image
      mask_channel = composite.mask_channels.get(name__contains=composite.current_zedge_unique)

      # determine marker
      for t, cell_instance_pk_list in cell_dictionary.items():
        # load image
        mask_mask = mask_channel.masks.get(t=t)
        mask = mask_mask.load()

        for cell_instance_pk in cell_instance_pk_list:
          # delete mask from mask image
          cell_instance = series.cell_instances.get(pk=cell_instance_pk)

          marker = cell_instance.track_instance.markers.get()
          r, c = marker.r, marker.c

          print(cell_instance.AreaShape_Area, (mask==mask[r,c]).sum(), mask[r,c], np.unique(mask), np.sum(mask>0))
          plt.imshow(mask)
          plt.show()
          mask[mask==mask[r,c]] = 0
          print(cell_instance.AreaShape_Area, (mask==mask[r,c]).sum(), mask[r,c], np.unique(mask), np.sum(mask>0))
          plt.imshow(mask)
          plt.show()

          # delete cell instance
          cell_instance.masks.all().delete()
          cell_instance.delete()

        mask_mask.array = mask.copy()
        mask_mask.save_array(root, template)

      # 3. recreate data file
      series.export_data()

      # 4. recreate tile image
      tile_mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_tile')

      # Run mod
      print('step02 | processing mod_tile...', end='\r')
      tile_mod.run(channel_unique_override=composite.current_zedge_unique)
      print('step02 | processing mod_tile... done.{}'.format(spacer))
