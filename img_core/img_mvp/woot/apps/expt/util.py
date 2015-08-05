# apps.expt.util

# django
from django.db import models

# util
import random
import string
import re

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

  value = lambda lines, template: re.match(template, list(filter(lambda l: re.match(template, l) is not None, lines))[0].rstrip()).group(1)

  voxel_r_metadata_template = r'HardwareSetting\|ScannerSettingRecord\|dblVoxelX #1: (.*)' # directly to rmop
  voxel_c_metadata_template = r'HardwareSetting\|ScannerSettingRecord\|dblVoxelY #1: (.*)' # directly to cmop
  total_z_metadata_template = r'HardwareSetting\|ScannerSettingRecord\|dblSizeZ #1: (.*)' # zmop = <ans> / zs
  tpf_in_seconds_metadata_template = r'HardwareSetting\|ScannerSettingRecord\|nDelayTime_s #1: (.*)' # tpf = <ans> / 60
  rs_template = r'HardwareSetting\|ScannerSettingRecord\|nFormatInDimension #1: (.*)'
  cs_template = r'HardwareSetting\|ScannerSettingRecord\|nFormatOutDimension #1: (.*)'
  zs_template = r'HardwareSetting\|ScannerSettingRecord\|nSections #1: (.*)'
  ts_template = r'HardwareSetting\|ScannerSettingRecord\|nRepeatActions #1: (.*)'

  metadata = {}

  with open(file_name) as inf_file:

    lines = inf_file.readlines()

    voxel_r = float(value(lines, voxel_r_metadata_template))
    voxel_c = float(value(lines, voxel_c_metadata_template))

    total_z = float(value(lines, total_z_metadata_template))
    tpf_in_seconds = float(value(lines, tpf_in_seconds_metadata_template))
    rs = float(value(lines, rs_template))
    cs = float(value(lines, cs_template))
    zs = float(value(lines, zs_template))
    ts = float(value(lines, ts_template))

    metadata['rmop'] = voxel_r
    metadata['cmop'] = voxel_c
    metadata['zmop'] = total_z / zs
    metadata['tpf'] = tpf_in_seconds / 60.0
    metadata['rs'] = int(rs)
    metadata['cs'] = int(cs)
    metadata['zs'] = int(zs)
    metadata['ts'] = int(ts)

  return metadata
