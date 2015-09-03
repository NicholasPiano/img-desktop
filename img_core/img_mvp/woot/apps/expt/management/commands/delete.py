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
    cell_pks = options['cells'].split(',')

    if experiment_name!='' and series_name!='':
      experiment = Experiment.objects.get(name=experiment_name)
      series = experiment.series.get(name=series_name)

      # select composite
      composite = series.composites.get()

      # template
      template = composite.templates.get(name='source')

      # image root
      root = experiment.composite_path

      # select cell
      if len(cell_pks)>0:
        for pk in cell_pks:
          if pk != '':
            if series.cells.filter(pk=pk).count()!=0:
              cell = series.cells.get(pk=pk)

              # what do I need to know about a cell to completely remove it?
              # 1. all its cell instances
              # 2. The gray value of each cell instance in all the masks

              # steps
              # 1. for each cell instance, load all masks and change gray value to 0, save image
              for cell_instance in cell.instances.all():
                for cell_mask in cell_instance.masks.all():
                  print('Removing {} {} cell {}, cell instance {}, cell mask {}...'.format(experiment_name, series_name, cell.pk, cell_instance.pk, cell_mask.pk))
                  mask_mask = cell_mask.mask
                  mask = mask_mask.load()
                  mask[mask==cell_mask.gray_value_id] = 0

                  mask_mask.array = mask.copy()
                  mask_mask.save_array(root, template)
                  mask_mask.save()

                  cell_mask.delete()
                cell_instance.delete()
              cell.delete()

            else:
              print('No cell with primary key {} exists in {} {}, skipping...'.format(pk, experiment_name, series_name))

          else:
            print('No pk, skipping...')

          # redo data
          series.export_data()

          # redo video
          tile_mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_tile')

          # Run mod
          print('step02 | processing mod_tile...', end='\r')
          tile_mod.run(channel_unique_override=composite.current_zedge_unique)
          print('step02 | processing mod_tile... done.{}'.format(spacer))

      else:
        print('Please enter at least one cell to delete')

    else:
      print('Please enter an experiment')
