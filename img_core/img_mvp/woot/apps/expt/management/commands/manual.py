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
from scipy.misc import imread, imsave, toimage
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
      unique = '2K5IF93D'
      unique_key = '-zcomp-8-1-1-zbf-8-5-5-2K5IF93D'
      marker_channel_name = '-zcomp-8-1-1'
      marker_channel = composite.channels.get(name=marker_channel_name)

      print('import masks')
      # 3. import masks and create new mask channel
      cp_out_file_list = [f for f in os.listdir(composite.experiment.cp_path) if (unique_key in f and '.tiff' in f)]
      # make new channel that gets put in mask path
      cp_template = composite.templates.get(name='cp')
      mask_template = composite.templates.get(name='mask')
      mask_channel = composite.mask_channels.create(name=unique_key)

      for cp_out_file in cp_out_file_list:
        array = imread(os.path.join(composite.experiment.cp_path, cp_out_file))
        metadata = cp_template.dict(cp_out_file)
        mask_channel.get_or_create_mask(array, int(metadata['t']))

      print('import data files')
      # 4. import datafiles and access data
      data_file_list = [f for f in os.listdir(composite.experiment.cp_path) if (unique in f and '.csv' in f)]
      for df_name in data_file_list:
        data_file, data_file_created, status = composite.get_or_create_data_file(composite.experiment.cp_path, df_name)

      # 5. create cells and cell instances from tracks
      cell_data_file = composite.data_files.get(id_token=unique, data_type='Cells')
      data = cell_data_file.load()

      # load masks and associate with grayscale id's
      for t in range(composite.series.ts):
        mask_mask = mask_channel.masks.get(t=t)
        mask = mask_mask.load()

        t_data = list(filter(lambda d: int(d['ImageNumber'])-1==t, data))

        markers = marker_channel.markers.filter(track_instance__t=t)
        for marker in markers:
          # 1. create cell
          cell, cell_created = composite.experiment.cells.get_or_create(series=composite.series, track=marker.track)

          # 2. create cell instance
          cell_instance, cell_instance_created = cell.instances.get_or_create(experiment=cell.experiment,
                                                                              series=cell.series,
                                                                              track_instance=marker.track_instance)

          # 3. create cell mask
          gray_value_id = mask[marker.r, marker.c]
          if gray_value_id!=0:
            cell_mask = cell_instance.masks.create(experiment=cell.experiment,
                                                   series=cell.series,
                                                   cell=cell,
                                                   channel=mask_channel,
                                                   mask=mask_mask,
                                                   marker=marker,
                                                   gray_value_id=gray_value_id)

            cell_mask_data = list(filter(lambda d: int(d['ObjectNumber'])==cell_mask.gray_value_id, t_data))[0]

            # 4. assign data
            cell_mask.r = cell_mask.marker.r
            cell_mask.c = cell_mask.marker.c
            cell_mask.t = t
            cell_mask.area = float(cell_mask_data['AreaShape_Area']) if str(cell_mask_data['AreaShape_Area']) != 'nan' else -1.0
            cell_mask.save()

    else:
      print('Please enter an experiment')
