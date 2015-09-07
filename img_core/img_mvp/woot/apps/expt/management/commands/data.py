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
      def convert_track_file(path, name_with_index):
        # names
        index_template = r'(?P<name>.+)_n[0-9]+'
        alt = r'(?P<name>.+)'
        name_match = re.match(index_template, name_with_index) if re.match(index_template, name_with_index) is not None else re.match(alt, name_with_index)
        name = name_match.group('name')
        csv_file_name = '{}_{}_markers.csv'.format(join(path, name), random_string())
        xls_file_name = '{}.xls'.format(join(path, name_with_index))

        tracks = {} # stores list of tracks that can then be put into the database

        with open(xls_file_name, 'rb') as track_file:

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

        with open(csv_file_name, 'w+') as out_file:
          out_file.write('expt,series,channel,id,t,r,c\n')
          for track_id, track in tracks.items():
            for frame in list(sorted(track, key=lambda t: t[2])):
              out_file.write('{},{},{},{},{},{},{}\n'.format(experiment_name,series_name,'-zcomp',track_id,frame[2],frame[0],frame[1]))

      # for each track file in the track directory, if there is not a .csv file with the same name, then translate it into the new format
      for file_name in [f for f in os.listdir(experiment.track_path) if ('.xls' in f and 'region' not in f and series_name in f)]:
        name_with_index, ext = splitext(file_name)
        convert_track_file(experiment.track_path, name_with_index)

      # 2. Import tracks
      # select composite
      composite = series.composites.get()

      # add all track files to composite
      data_file_list = [f for f in os.listdir(composite.experiment.track_path) if (os.path.splitext(f)[1] in allowed_data_extensions and composite.experiment.path_matches_series(f, composite.series.name) and 'regions' not in f)]

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

      # 3. Generate zDiff channel
      zdiff_mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_zdiff')

      # Run mod
      print('step02 | processing mod_zdiff...', end='\r')
      zdiff_mod.run()
      print('step02 | processing mod_zdiff... done.{}'.format(spacer))

      # 4. Segment zdiff channel
      zdiff_channel = composite.channels.get(name='-zdiff')
      zdiff_unique = zdiff_channel.segment(marker_channel_name='-zcomp')

      # 5. Generate zEdge channel
      zedge_mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_zedge')

      # Run mod
      print('step02 | processing mod_zedge...', end='\r')
      zedge_mod.run(channel_unique_override=zdiff_unique)
      print('step02 | processing mod_zedge... done.{}'.format(spacer))

      # 6. Segment zEdge channel
      zedge_channel = composite.channels.get(name='-zbf')
      zedge_unique = zedge_channel.segment(marker_channel_name='-zcomp', threshold_correction_factor=1.2)

      # 7. Export data to data directory
      series.export_data()

      # 8. Tile mod
      composite.current_zedge_unique = zedge_unique
      composite.save()
      tile_mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_tile')

      # Run mod
      print('step02 | processing mod_tile...', end='\r')
      tile_mod.run(channel_unique_override=zedge_unique)
      print('step02 | processing mod_tile... done.{}'.format(spacer))

    else:
      print('Please enter an experiment')
