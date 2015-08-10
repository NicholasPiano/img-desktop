# expt.command: step01_input

# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# local

# util
import os
from os.path import join, exists, splitext
from optparse import make_option
from subprocess import call
import datetime
import re
import shutil as sh

spacer = ' ' *  20

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--revert', # option that will appear in cmd
      action='store_true', # no idea
      dest='revert', # refer to this in options variable
      default=False, # some default
      help='Name of the experiment to import' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):

    path_template_rx = r'(?P<year>.+)_(?P<month>.+)_(?P<day>.+)_(?P<hour>.+)_(?P<minute>.+)_(?P<second>.+)'
    path_template_rv = '{}_{}_{}_{}_{}_{}'

    # methods
    def datetime_from_path(path):
      data = re.match(path_template_rx, path).groupdict()
      return datetime.datetime(year=int(data['year']), month=int(data['month']), day=int(data['day']), hour=int(data['hour']), minute=int(data['minute']), second=int(data['second']))

    def path_from_datetime(datetime):
      return path_template_rv.format(datetime.year, datetime.month, datetime.day, datetime.hour, datetime.minute, datetime.second)

    # vars
    backup_path = settings.BACKUP_ROOT
    site_path = settings.SITE_ROOT
    data_path = settings.DATA_ROOT

    # create backup path if it does not exist
    if not exists(backup_path):
      os.mkdir(backup_path)

    # store previous datetime
    backup_path_list = [p for p in os.listdir(backup_path) if '.DS' not in p]
    previous_path = None if backup_path_list==[] else max(backup_path_list, key=lambda p: datetime_from_path(p))

    # make new backup directory
    now = datetime.datetime.now()
    now_path = join(backup_path, path_from_datetime(now))
    os.mkdir(now_path)

    # copy files and folders
    # - database file
    db_path = join(site_path, 'db', 'img_db.sqlite3')
    sh.copy2(db_path, join(now_path, 'img_db.sqlite3'))
    print('copying db file from {} to {}'.format(db_path, join(now_path, 'img_db.sqlite3')))

    experiment_paths = [p for p in os.listdir(data_path) if (os.path.isdir(join(data_path, p)) and 'img' in os.listdir(join(data_path, p)))]
    for experiment_path in experiment_paths:
      # - track directory
      print('experiment {}, copying track directory from {} to {}'.format(experiment_path, join(data_path, experiment_path, 'track'), join(now_path, experiment_path, 'track')))
      sh.copytree(join(data_path, experiment_path, 'track'), join(now_path, experiment_path, 'track'))

      # - inf directory
      print('experiment {}, copying inf directory from {} to {}'.format(experiment_path, join(data_path, experiment_path, 'inf'), join(now_path, experiment_path, 'inf')))
      sh.copytree(join(data_path, experiment_path, 'inf'), join(now_path, experiment_path, 'inf'))

      # - data directory
      print('experiment {}, copying data directory from {} to {}'.format(experiment_path, join(data_path, experiment_path, 'data'), join(now_path, experiment_path, 'data')))
      sh.copytree(join(data_path, experiment_path, 'data'), join(now_path, experiment_path, 'data'))

    # revert?
    if options['revert'] and previous_path is not None:
      # recreate system from last backup
      print('Reverting...')
      print('Removing db {}'.format(db_path))
      os.remove(db_path)
      new_db_path = join(previous_path, 'img_db.sqlite3')
      print('Adding new db {}'.format(new_db_path))
      sh.copy2(join(backup_path, new_db_path), join(site_path, 'db'))

      for experiment_path in experiment_paths:
        # - track directory
        print('experiment {}, removing track directory...'.format(experiment_path))
        sh.rmtree(join(data_path, experiment_path, 'track'))
        print('experiment {}, copying track directory from {} to {}'.format(experiment_path, join(backup_path, previous_path, experiment_path, 'track'), join(data_path, experiment_path, 'track')))
        sh.copytree(join(backup_path, previous_path, experiment_path, 'track'), join(data_path, experiment_path, 'track'))

        # - inf directory
        print('experiment {}, removing inf directory...'.format(experiment_path))
        sh.rmtree(join(data_path, experiment_path, 'inf'))
        print('experiment {}, copying inf directory from {} to {}'.format(experiment_path, join(backup_path, previous_path, experiment_path, 'inf'), join(data_path, experiment_path, 'inf')))
        sh.copytree(join(backup_path, previous_path, experiment_path, 'inf'), join(data_path, experiment_path, 'inf'))

        # - data directory
        print('experiment {}, removing data directory...'.format(experiment_path))
        sh.rmtree(join(data_path, experiment_path, 'data'))
        print('experiment {}, copying data directory from {} to {}'.format(experiment_path, join(backup_path, previous_path, experiment_path, 'data'), join(data_path, experiment_path, 'data')))
        sh.copytree(join(backup_path, previous_path, experiment_path, 'data'), join(data_path, experiment_path, 'data'))
