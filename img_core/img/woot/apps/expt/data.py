# apps.expt.data

'''
Specific experiment and series information in the form of lists of prototype objects
'''
import os

### Classes
class _Experiment():
  def __init__(self, name, rmop, cmop, zmop, tpf):
    self.name = name
    self.rmop = rmop
    self.cmop = cmop
    self.zmop = zmop
    self.tpf = tpf

class _Series():
  def __init__(self, experiment, name):
    self.experiment = experiment
    self.name = name

class _Region():
  def __init__(self, experiment, series, name, description, index, vertical_sort_index):
    self.experiment = experiment
    self.series = series
    self.name = name
    self.description = description
    self.index = index
    self.vertical_sort_index = vertical_sort_index

### Data
experiments = (
  _Experiment(name='050714', rmop=0.5369, cmop=0.5369, zmop=1.482, tpf=10.7003),
  _Experiment(name='050714-test', rmop=0.5369, cmop=0.5369, zmop=1.482, tpf=10.7003),
  _Experiment(name='190714', rmop=0.501, cmop=0.5015, zmop=1.482, tpf=9.7408),
  _Experiment(name='260714', rmop=0.5696074, cmop=0.5701647, zmop=1.482, tpf=7.6807),
  _Experiment(name='260714-test', rmop=0.5696074, cmop=0.5701647, zmop=1.482, tpf=7.6807),
  _Experiment(name='280614', rmop=0.7941950, cmop=0.7934188, zmop=1.482, tpf=10.665),
)

series = (
  # 050714
  _Series(experiment='050714', name='13'),

  # 050714
  _Series(experiment='050714-test', name='13'),

  # 190714
  _Series(experiment='190714', name='12'),

  # 260714
  _Series(experiment='260714', name='12'),
  _Series(experiment='260714', name='13'),
  _Series(experiment='260714', name='14'),
  _Series(experiment='260714', name='15'),

  # 260714
  _Series(experiment='260714-test', name='12'),
  _Series(experiment='260714-test', name='13'),

  # 280614
  _Series(experiment='280614', name='7'),
)

regions = (
  # 050714 - series 13
  _Region(experiment='050714', series='13', name='medium', description='Bottom of the environment in the medium', index=1, vertical_sort_index=4),
  _Region(experiment='050714', series='13', name='barrier-edge', description='Within one cell diameter of the barrier', index=2, vertical_sort_index=3),
  _Region(experiment='050714', series='13', name='barrier', description='Within the barrier', index=3, vertical_sort_index=2),
  _Region(experiment='050714', series='13', name='gel', description='Through the barrier in the gel region', index=4, vertical_sort_index=1),

  # 050714-test - series 13
  _Region(experiment='050714-test', series='13', name='medium', description='Bottom of the environment in the medium', index=1, vertical_sort_index=4),
  _Region(experiment='050714-test', series='13', name='barrier-edge', description='Within one cell diameter of the barrier', index=2, vertical_sort_index=3),
  _Region(experiment='050714-test', series='13', name='barrier', description='Within the barrier', index=3, vertical_sort_index=2),
  _Region(experiment='050714-test', series='13', name='gel', description='Through the barrier in the gel region', index=4, vertical_sort_index=1),

  # 190714 - series 12
  _Region(experiment='190714', series='12', name='medium', description='Bottom of the environment in the medium', index=1, vertical_sort_index=4),
  _Region(experiment='190714', series='12', name='barrier-edge', description='Within one cell diameter of the barrier', index=2, vertical_sort_index=3),
  _Region(experiment='190714', series='12', name='barrier', description='Within the barrier', index=3, vertical_sort_index=2),
  _Region(experiment='190714', series='12', name='gel', description='Through the barrier in the gel region', index=4, vertical_sort_index=1),

  # 260714 - series 12
  _Region(experiment='260714', series='12', name='medium', description='Bottom of the environment in the medium', index=1, vertical_sort_index=4),
  _Region(experiment='260714', series='12', name='barrier-edge', description='Within one cell diameter of the barrier', index=2, vertical_sort_index=3),
  _Region(experiment='260714', series='12', name='barrier', description='Within the barrier', index=3, vertical_sort_index=2),
  _Region(experiment='260714', series='12', name='gel', description='Through the barrier in the gel region', index=4, vertical_sort_index=1),

  # 260714 - series 13
  _Region(experiment='260714', series='13', name='medium', description='Bottom of the environment in the medium', index=1, vertical_sort_index=4),
  _Region(experiment='260714', series='13', name='barrier-edge', description='Within one cell diameter of the barrier', index=2, vertical_sort_index=3),
  _Region(experiment='260714', series='13', name='barrier', description='Within the barrier', index=3, vertical_sort_index=2),
  _Region(experiment='260714', series='13', name='gel', description='Through the barrier in the gel region', index=4, vertical_sort_index=1),

  # 260714 - series 14
  _Region(experiment='260714', series='14', name='medium', description='Bottom of the environment in the medium', index=1, vertical_sort_index=4),
  _Region(experiment='260714', series='14', name='barrier-edge', description='Within one cell diameter of the barrier', index=2, vertical_sort_index=3),
  _Region(experiment='260714', series='14', name='barrier', description='Within the barrier', index=3, vertical_sort_index=2),
  _Region(experiment='260714', series='14', name='gel', description='Through the barrier in the gel region', index=4, vertical_sort_index=1),

  # 260714 - series 15
  _Region(experiment='260714', series='15', name='medium', description='Bottom of the environment in the medium', index=1, vertical_sort_index=4),
  _Region(experiment='260714', series='15', name='barrier-edge', description='Within one cell diameter of the barrier', index=2, vertical_sort_index=3),
  _Region(experiment='260714', series='15', name='barrier', description='Within the barrier', index=3, vertical_sort_index=2),
  _Region(experiment='260714', series='15', name='gel', description='Through the barrier in the gel region', index=4, vertical_sort_index=1),

  # 260714-test - series 12
  _Region(experiment='260714-test', series='12', name='medium', description='Bottom of the environment in the medium', index=1, vertical_sort_index=4),
  _Region(experiment='260714-test', series='12', name='barrier-edge', description='Within one cell diameter of the barrier', index=2, vertical_sort_index=3),
  _Region(experiment='260714-test', series='12', name='barrier', description='Within the barrier', index=3, vertical_sort_index=2),
  _Region(experiment='260714-test', series='12', name='gel', description='Through the barrier in the gel region', index=4, vertical_sort_index=1),

  # 260714-test - series 13
  _Region(experiment='260714-test', series='13', name='medium', description='Bottom of the environment in the medium', index=1, vertical_sort_index=4),
  _Region(experiment='260714-test', series='13', name='barrier-edge', description='Within one cell diameter of the barrier', index=2, vertical_sort_index=3),
  _Region(experiment='260714-test', series='13', name='barrier', description='Within the barrier', index=3, vertical_sort_index=2),
  _Region(experiment='260714-test', series='13', name='gel', description='Through the barrier in the gel region', index=4, vertical_sort_index=1),

  # 280614 - series 7
  _Region(experiment='280614', series='7', name='medium', description='Bottom of the environment in the medium', index=1, vertical_sort_index=4),
  _Region(experiment='280614', series='7', name='barrier-edge', description='Within one cell diameter of the barrier', index=2, vertical_sort_index=3),
  _Region(experiment='280614', series='7', name='barrier', description='Within the barrier', index=3, vertical_sort_index=2),
  _Region(experiment='280614', series='7', name='gel', description='Through the barrier in the gel region', index=4, vertical_sort_index=1),

)

### Image file extensions
allowed_img_extensions = (
  '.tiff',
)

allowed_data_extensions = (
  '.csv',
)

### image filename templates
templates = {
  'source':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_ch(?P<channel>.+)_t(?P<t>[0-9]+)_z(?P<z>[0-9]+)\.(?P<extension>.+)$',
    'rv':r'{}_s{}_ch{}_t{}_z{}.tiff',
  },
  'mask':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_ch(?P<channel>.+)_t(?P<t>[0-9]+)\.(?P<extension>.+)$',
    'rv':r'{}_s{}_ch{}_t{}.tiff',
  },
  'cp':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_ch-(?P<channel>.+)_t(?P<t>[0-9]+)_z(?P<z>[0-9]+)_cp-(?P<secondary_channel>.+)\.(?P<extension>.+)$',
    'rv':r'{}_s{}_ch-{}_t{}_z{}_cp-{}.tiff',
  },
  'data':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_(?P<id>[A-Z0-9]{8})_(?P<type>.+)\.csv$',
    'rv':r'{}_s{}_{}_{}.csv',
  },
  'pipeline':{
    'rx':r'^(?P<name>.+)_(?P<id>[A-Z0-9]{8})\.cppipe$',
    'rv':r'{}_{}.cppipe',
  }
}

### Default paths
default_paths = {
  'storage':'img/storage/',
  'composite':'img/composite/',
  'region':'img/region/',
  'cp':'img/cp/',

  'output':'img/output/',
  'plot':'plot/',
  'track':'track/',
  'data':'data/',
  'pipeline':'pipelines/',
}
