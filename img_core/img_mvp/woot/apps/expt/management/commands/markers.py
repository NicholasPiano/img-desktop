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

      # 2. Import tracks
      # select composite
      composite = series.composites.get()

      # add all track files to composite
      data_file_list = [f for f in os.listdir(composite.experiment.track_path) if (os.path.splitext(f)[1] in allowed_data_extensions and composite.experiment.path_matches_series(f, composite.series.name) and 'regions' not in f)]

      for df_name in data_file_list:
        print('data file {}... '.format(df_name), end='\r')
        data_file, data_file_created, status = composite.get_or_create_data_file(composite.experiment.track_path, df_name)
        print('data file {}... {}'.format(df_name, status))

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

          print('processing marker ({}/{})... {} tracks, {} instances, {} markers'.format(i+1,len(data),composite.tracks.count(), composite.track_instances.count(), composite.markers.count()), end='\n' if i==len(data)-1 else '\r')

      # iterate through each channel in composite and create a zedge channel for each of them.
      mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_zedge')

      # Run mod
      for sigma in [1,2,3,4,5]:
        for R in [1,2,3,4,5]:
          print('processing mod_zmod sigma={} R={}...'.format(sigma, R), end='\r')
          mod.run(sigma=sigma, R=R, dz=dz)
          print('processing mod_zmod sigma={} R={}... done.{}'.format(sigma, R, spacer))

    else:
      print('Please enter an experiment')