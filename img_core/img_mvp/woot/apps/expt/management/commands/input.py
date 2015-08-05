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
from os.path import join, exists
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

    make_option('--lif', # option that will appear in cmd
      action='store', # no idea
      dest='lif', # refer to this in options variable
      default='', # some default
      help='Name of the .lif archive' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):

    # vars
    experiment_name = options['expt']
    series_name = options['series']
    lif_name = options['lif']
    data_root = settings.DATA_ROOT
    lif_root = settings.LIF_ROOT
    bfconvert = join(data_root, 'bftools', 'bfconvert')
    showinf = join(data_root, 'bftools', 'showinf')

    # 1. create experiment and series
    if experiment_name!='':
      print('step01 | experiment path exists, experiment {}... '.format(experiment_name), end='\r')
      experiment, experiment_created = Experiment.objects.get_or_create(name=experiment_name)
      if experiment_created:
        # set metadata
        experiment.make_paths(os.path.join(base_path, experiment.name))
        experiment.get_templates()
        print('step01 | experiment path exists, experiment {}...  created.'.format(experiment_name))
      else:
        print('step01 | experiment path exists, experiment {}... already exists.'.format(experiment_name))

      print('step01 | series {}... '.format(series_name), end='\r')
      series, series_created = experiment.series.get_or_create(name=series_name)
      if series_created:
        print('step01 | series {}... created.'.format(series_name))
      else:
        print('step01 | series {}... already exists.'.format(series_name))

      # 2. if lif is not extracted, do it.
      if len(os.listdir(experiment.storage_path))==0:

        # extract lif
        lif_path = join(lif_root, lif_name)
        lif_template = '{}/{}_s%s_ch%c_t%t_z%z.tiff'.format(experiment_path, experiment_name)

        # run extract
        print('step01 | Extracting lif ')
        call('{} {} {}'.format(bfconvert, lif_path, lif_template))

      else:
        print('step01 | .lif already extracted for experiment {}, series {}; continuing... '.format(experiment_name, series_name))

      # 3. series measurements
      series_metadata_file_name = join(experiment.inf_path, '{}_s{}.txt'.format(experiment_name, series_name))
      if not exists(series_metadata_file_name):

        # run show inf
        lif_path = join(lif_root, lif_name)
        print('step01 | Extracting lif metadata for experiment {}, series {}... '.format(experiment_name, series_name))
        call('{} -nopix {} > {}'.format(showinf, lif_path, series_metadata_file_name))

        series_metadata = series_metadata_from_file(series_metadata_file_name)

        series.rmop = series_metadata['rmop']
        series.cmop = series_metadata['cmop']
        series.zmop = series_metadata['zmop']
        series.tpf = series_metadata['tpf']
        series.rs = series_metadata['rs']
        series.cs = series_metadata['cs']
        series.zs = series_metadata['zs']
        series.ts = series_metadata['ts']
        series.save()

      # 4. import specified series
      if series_name!='':
        # for each path in the experiment folder, create new path if the series matches.
        for root in experiment.img_roots():

          img_files = [f for f in os.listdir(root) if (os.path.splitext(f)[1] in allowed_img_extensions and experiment.path_matches_series(f, series_name))]
          num_img_files = len(img_files)

          if num_img_files>0:
            for i, file_name in enumerate(img_files):
              path, path_created, path_message = experiment.get_or_create_path(series, root, file_name)
              print('step01 | adding image files in {}: ({}/{}) {} ...path {}{}'.format(root, i+1, num_img_files, file_name, path_message, spacer), end='\r' if i<num_img_files-1 else '\n')

          else:
            print('step01 | no files found in {}'.format(root))

        # 5. measurements
        print('step01 | setting measurements for {} series {}'.format(experiment_name, series_name))

        # 6. composite
        print('step01 | creating composite for {} series {}'.format(experiment_name, series_name))
        composite = series.compose()

        # 7. make zmod channels
        if composite.channels.filter(name='-zmod').count()==0:
          mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_zmod')

          # 3. Run mod
          print('step01 | processing mod_zmod...', end='\r')
          mod.run()
          print('step01 | processing mod_zmod... done.{}'.format(spacer))

        else:
          print('step01 | zmod already exists...')

      else:
        print('Please enter a series')

    else:
      print('Please enter an experiment')
