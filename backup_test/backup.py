import datetime
import os
import re
from os.path import join, exists, splitext
import shutil as sh

revert = False

path_template_rx = r'(?P<year>.+)_(?P<month>.+)_(?P<day>.+)_(?P<hour>.+)_(?P<minute>.+)_(?P<second>.+)'
path_template_rv = '{}_{}_{}_{}_{}_{}'

# methods
def datetime_from_path(path):
  data = re.match(path_template_rx, path).groupdict()
  return datetime.datetime(year=data['year'], month=data['month'], day=data['day'], hour=data['hour'], minute=data['minute'], second=data['second'])

def path_from_datetime(datetime):
  return path_template_rv.format(datetime.year, datetime.month, datetime.day, datetime.hour, datetime.minute, datetime.second)

# vars
backup_path = './backup/'
django_path = ''
data_path = '.'

# create backup path if it does not exist
if not exists(backup_path):
  os.mkdir(backup_path)

# store previous datetime
previous_path = None if os.listdir(backup_path)==[] else max([path for path in os.listdir(backup_path)], key=lambda p: datetime_from_path(p))

# make new backup directory
now = datetime.datetime.now()
now_path = join(backup_path, path_from_datetime(now))

# copy files and folders
# - database file
db_path = join(settings.DJANGO_ROOT, 'db', 'img_db.sqlite3')
sh.copy2(db_path, join(now_path, 'img_db.sqlite3'))

experiment_paths = [p for p in os.listdir(data_path) if exists(join(p, 'img'))]
for experiment_path in experiment_paths:
  # - track directory
  sh.copytree(join(data_path, experiment_path, 'track'), join(now_path, experiment_path, 'track'))

  # - inf directory
  sh.copytree(join(data_path, experiment_path, 'inf'), join(now_path, experiment_path, 'inf'))

  # - data directory
  sh.copytree(join(data_path, experiment_path, 'data'), join(now_path, experiment_path, 'data'))

# revert?
if revert:
  # recreate system from last backup
  pass
