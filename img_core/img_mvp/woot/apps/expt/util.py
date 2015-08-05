# apps.expt.util

# django
from django.db import models

# util
import random
import string

# vars
chars = string.ascii_uppercase + string.digits

# methods
def generate_id_token(app_name, obj_name):

  Obj = models.get_model(app_name, obj_name)

  def get_id_token():
    return random_string()

  id_token = get_id_token()
  while Obj.objects.filter(id_token=id_token).count()>0:
    id_token = get_id_token()

  return id_token

def random_string():
  return ''.join([random.choice(chars) for _ in range(8)]) #8 character string

def series_metadata_from_file(file_name):

  voxel_r_metadata_template = r'HardwareSetting\|ScannerSettingRecord\|dblVoxelX #1: (.*)\n'
  voxel_c_metadata_template = r'HardwareSetting\|ScannerSettingRecord\|dblVoxelY #1: (.*)\n'

  value = lambda lines, template: re.match(template, list(filter(lambda l: re.match(template, l) is not None, lines))[0].rstrip()).group(1)
  return value(lines, template)
