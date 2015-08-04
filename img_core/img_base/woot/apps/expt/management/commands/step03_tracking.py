# expt.command: step03_tracking

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.img.models import Composite
from apps.expt.util import *
from apps.expt.data import *

# util
import os
from optparse import make_option
import numpy as np

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='050714-test', # some default
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
    '''
    1. What does this script do?
    > Make images that can be recognized by CellProfiler by multiplying smoothed GFP with the flattened Brightfield

    2. What data structures are input?
    > Channel

    3. What data structures are output?
    > Channel

    4. Is this stage repeated/one-time?
    > One-time

    Steps:

    1. Select composite
    2. Call pmod mod on composite
    3. Run

    '''

    # select composite
    composite = Composite.objects.get(experiment__name=options['expt'], series__name=options['series'])

    # add all track files to composite
    data_file_list = [f for f in os.listdir(composite.experiment.track_path) if (os.path.splitext(f)[1] in allowed_data_extensions and composite.experiment.path_matches_series(f, composite.series.name))]

    for df_name in data_file_list:
      print('step03 | data file {}... '.format(df_name), end='\r')
      data_file, data_file_created, status = composite.get_or_create_data_file(composite.experiment.track_path, df_name)
      print('step03 | data file {}... {}'.format(df_name, status))

    ### REGIONS
    # 1. check for existing track files
    # 2. prompt or if no tracking files start region interface
    # if composite.data_files.filter(data_type__in=['markers','regions']).count()!=0:
    #   print()
    # else:
    # 3. save data
    # 4. make region tracks and instances

    # for data_file in composite.data_files.filter(data_type='regions'):
    #   data = data_file.load()
    #   for i, region_prototype in enumerate(data):
    #     region_track, region_track_created = composite.region_tracks.get_or_create(experiment=composite.experiment,
    #                                                                                series=composite.series,
    #                                                                                composite=composite,
    #                                                                                name=region_prototype['region'])
    #
    #     region_track_instance, region_track_instance_created = region_track.instances.get_or_create(experiment=composite.experiment,
    #                                                                                                 series=composite.series,
    #                                                                                                 composite=composite,
    #                                                                                                 t=int(region_prototype['t']))
    #
    #     region_track_marker, region_track_marker_created = region_track_instance.markers.get_or_create(experiment=composite.experiment,
    #                                                                                                    series=composite.series,
    #                                                                                                    composite=composite,
    #                                                                                                    channel=composite.channels.get(name=region_prototype['channel']),
    #                                                                                                    region_track=region_track,
    #                                                                                                    r=int(region_prototype['r']),
    #                                                                                                    c=int(region_prototype['c']))
    #
    #     print('step03 | processing region marker ({}/{})... {} tracks, {} instances, {} markers'.format(i+1,len(data),composite.region_tracks.count(), composite.region_track_instances.count(), composite.region_markers.count()), end='\n' if i==len(data)-1 else '\r')

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

        print('step03 | processing marker ({}/{})... {} tracks, {} instances, {} markers'.format(i+1,len(data),composite.tracks.count(), composite.track_instances.count(), composite.markers.count()), end='\n' if i==len(data)-1 else '\r')
