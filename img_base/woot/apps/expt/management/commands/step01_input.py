# expt.command: step01_input

# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# local
from apps.expt.models import Experiment
from apps.expt.data import *

# util
import os
from optparse import make_option

spacer = ' ' *  20

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
    > Converts image file names into searchable pixel space composite

    2. What data structures are input?
    > strings

    3. What data structures are output?
    > Experiment, Series, Path, Channel, Composite

    4. Is this stage repeated/one-time?
    > Repeated

    Steps:

    1. check if experiment name is in the base folder
    2. create a new experiment
    3. create a new series
    4. for each path in experiment folder, make a path object.
      - if path object matches the series, keep it, else delete
    5. make composite from series

    '''

    # vars
    experiment_name = options['expt']
    series_name = options['series']
    base_path = settings.DATA_ROOT

    if os.path.exists(os.path.join(base_path, experiment_name)):
      # 1. create experiment
      print('step01 | experiment path exists, experiment {}... '.format(experiment_name), end='\r')
      experiment, experiment_created = Experiment.objects.get_or_create(name=experiment_name)
      if experiment_created:
        # set metadata
        experiment.make_paths(os.path.join(base_path, experiment.name))
        experiment.get_metadata()
        print('step01 | experiment path exists, experiment {}...  created.'.format(experiment_name))
      else:
        print('step01 | experiment path exists, experiment {}... already exists.'.format(experiment_name))

      # 2. create series
      if experiment.is_allowed_series(series_name):
        print('step01 | series {}... '.format(series_name), end='\r')
        series, series_created = experiment.series.get_or_create(name=series_name)
        if series_created:
          print('step01 | series {}... created.'.format(series_name))
        else:
          print('step01 | series {}... already exists.'.format(series_name))

        # 3. for each path in the experiment folder, create new path if the series matches.
        for root in experiment.img_roots():

          img_files = [f for f in os.listdir(root) if (os.path.splitext(f)[1] in allowed_img_extensions and experiment.path_matches_series(f, series_name))]
          num_img_files = len(img_files)

          if num_img_files>0:
            for i, file_name in enumerate(img_files):
              path, path_created, path_message = experiment.get_or_create_path(series, root, file_name)
              print('step01 | adding image files in {}: ({}/{}) {} ...path {}{}'.format(root, i+1, num_img_files, file_name, path_message, spacer), end='\r' if i<num_img_files-1 else '\n')

          else:
            print('step01 | no files found in {}'.format(root))

        # 4. measurements
        print('step01 | setting measurements for {} series {}'.format(experiment_name, series_name))

        # rows and columns from image
        (rs,cs) = series.paths.get(channel__name='0', t=0, z=0).load().shape
        series.rs = rs
        series.cs = cs

        # z and t from counts
        series.zs = series.paths.filter(channel__name='0', t=0).count()
        series.ts = series.paths.filter(channel__name='0', z=0).count()

        series.save()

        # 5. create composite
        series.compose()

      else:
        print('step01 | {}/{} not a valid series.'.format(experiment_name, series_name))

    else:
      print('step01 | experiment path {} not found in {}'.format(experiment_name, base_path))
