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

      # 1. Convert track files to csv
      # for each track file in the track directory, if there is not a .csv file with the same name, then translate it into the new format

      # 2. Import tracks
      # select composite
      composite = experiment.composites.get()

      # add all track files to composite
      data_file_list = [f for f in os.listdir(composite.experiment.track_path) if (os.path.splitext(f)[1] in allowed_data_extensions and composite.experiment.path_matches_series(f, composite.series.name))]

      for df_name in data_file_list:
        print('step02 | data file {}... '.format(df_name), end='\r')
        data_file, data_file_created, status = composite.get_or_create_data_file(composite.experiment.track_path, df_name)
        print('step02 | data file {}... {}'.format(df_name, status))

      ### MARKERS
      for data_file in composite.data_files.filter(data_type='markers'):
        data = data_file.load()
        for i, marker_prototype in enumerate(data):
          track, track_created = composite.tracks.get_or_create(experiment=composite.experiment,
                                                                series=composite.series,
                                                                composite=composite,
                                                                channel=composite.channels.get(name=marker_prototype['channel']),
                                                                track_id=marker_prototype['id'])

          track_instance, track_instance_created = track.instances.get_or_create(experiment=composite.experiment,
                                                                                 series=composite.series,
                                                                                 composite=composite,
                                                                                 channel=composite.channels.get(name=marker_prototype['channel']),
                                                                                 t=int(marker_prototype['t']))

          marker, marker_created = track_instance.markers.get_or_create(experiment=composite.experiment,
                                                                        series=composite.series,
                                                                        composite=composite,
                                                                        channel=composite.channels.get(name=marker_prototype['channel']),
                                                                        track=track,
                                                                        r=int(marker_prototype['r']),
                                                                        c=int(marker_prototype['c']))

          print('step02 | processing marker ({}/{})... {} tracks, {} instances, {} markers'.format(i+1,len(data),composite.tracks.count(), composite.track_instances.count(), composite.markers.count()), end='\n' if i==len(data)-1 else '\r')

      # 3. Segment ZCOMP channel
      channel = composite.channels.get(name='-zcomp')
      marker_channel_name = '-zbf'

      channel.segment(marker_channel_name)

      # setup

      # 1. create primary from markers with marker_channel
      # - delete primary channel and files

      # 2. create pipeline and run
      # - delete

      # 3. import masks and create new mask channel
      cp_out_file_list = [f for f in os.listdir(self.composite.experiment.cp_path) if (suffix_id in f and '.tiff' in f)]
      # make new channel that gets put in mask path
      cp_template = self.composite.templates.get(name='cp')
      mask_template = self.composite.templates.get(name='mask')
      mask_channel = self.composite.mask_channels.create(name=suffix_id)

      for cp_out_file in cp_out_file_list:
        array = imread(os.path.join(self.composite.experiment.cp_path, cp_out_file))
        metadata = cp_template.dict(cp_out_file)
        mask_channel.get_or_create_mask(array, int(metadata['t']))

      print('import data files')
      # 4. import datafiles and access data
      data_file_list = [f for f in os.listdir(self.composite.experiment.cp_path) if (unique in f and '.csv' in f)]
      for df_name in data_file_list:
        data_file, data_file_created, status = self.composite.get_or_create_data_file(self.composite.experiment.cp_path, df_name)

      # 5. create cells and cell instances from tracks
      cell_data_file = self.composite.data_files.get(id_token=unique, data_type='Cells')
      data = cell_data_file.load()

      # load masks and associate with grayscale id's
      for t in range(self.composite.series.ts):
        mask_mask = mask_channel.masks.get(t=t)
        mask = mask_mask.load()

        t_data = list(filter(lambda d: int(d['ImageNumber'])-1==t, data))

        markers = marker_channel.markers.filter(track_instance__t=t)
        for marker in markers:
          # 1. create cell
          cell, cell_created = self.composite.experiment.cells.get_or_create(series=self.composite.series, track=marker.track)

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
                                                   mask=mask_mask,
                                                   marker=marker,
                                                   gray_value_id=gray_value_id)

            cell_mask_data = list(filter(lambda d: int(d['ObjectNumber'])==cell_mask.gray_value_id, t_data))[0]

            # 4. assign data
            cell_mask.r = cell_mask.marker.r
            cell_mask.c = cell_mask.marker.c
            cell_mask.t = t
            cell_mask.AreaShape_Area = float(cell_mask_data['AreaShape_Area'])
            cell_mask.AreaShape_Compactness = float(cell_mask_data['AreaShape_Compactness'])
            cell_mask.AreaShape_Eccentricity = float(cell_mask_data['AreaShape_Eccentricity'])
            cell_mask.AreaShape_EulerNumber = float(cell_mask_data['AreaShape_EulerNumber'])
            cell_mask.AreaShape_Extent = float(cell_mask_data['AreaShape_Extent'])
            cell_mask.AreaShape_FormFactor = float(cell_mask_data['AreaShape_FormFactor'])
            cell_mask.AreaShape_MajorAxisLength = float(cell_mask_data['AreaShape_MajorAxisLength'])
            cell_mask.AreaShape_MaximumRadius = float(cell_mask_data['AreaShape_MaximumRadius'])
            cell_mask.AreaShape_MeanRadius = float(cell_mask_data['AreaShape_MeanRadius'])
            cell_mask.AreaShape_MedianRadius = float(cell_mask_data['AreaShape_MedianRadius'])
            cell_mask.AreaShape_MinorAxisLength = float(cell_mask_data['AreaShape_MinorAxisLength'])
            cell_mask.AreaShape_Orientation = float(cell_mask_data['AreaShape_Orientation'])
            cell_mask.AreaShape_Perimeter = float(cell_mask_data['AreaShape_Perimeter'])
            cell_mask.AreaShape_Solidity = float(cell_mask_data['AreaShape_Solidity'])

            cell_mask.save()

            # for now
            cell_instance.set_from_masks()

          else:
            # for now
            cell_instance.set_from_markers()

      # 6. calculate cell velocities
      print('calculating velocities...')
      for cell in self.composite.experiment.cells.all():
        cell.calculate_velocities()

      # 4. Tile mod
      # Run mod
      print('step02 | processing mod_tile...', end='\r')

      print('step02 | processing mod_tile... done.{}'.format(spacer))

      # 5. Label mod
      # Run mod
      print('step02 | processing mod_label...', end='\r')

      print('step02 | processing mod_label... done.{}'.format(spacer))

    else:
      print('Please enter an experiment')
