# woot.apps.img.models

# django
from django.db import models

# local
from apps.expt.models import Experiment, Series
from apps.expt.util import generate_id_token
from apps.img import algorithms

# util
import os
import re
from scipy.misc import imread, imsave, toimage
from skimage import exposure
import numpy as np

### Models
# http://stackoverflow.com/questions/19695249/load-just-part-of-an-image-in-python
class Composite(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='composites')
  series = models.ForeignKey(Series, related_name='composites')

  # properties
  id_token = models.CharField(max_length=8)

  # methods
  def __str__(self):
    return '{}, {} > {}'.format(self.experiment.name, self.series.name, self.id_token)

  def save_data_file(self):
    # save data on all cell instances
    pass

  def get_or_create_data_file(self, root, file_name):

    # metadata
    template = self.templates.get(name='data')
    metadata = template.dict(file_name)

    if self.series.name == metadata['series']:
      data_file, data_file_created = self.data_files.get_or_create(experiment=self.experiment, series=self.series, template=template, id_token=metadata['id'], data_type=metadata['type'], url=os.path.join(root, file_name), file_name=file_name)
      return data_file, data_file_created, 'created.' if data_file_created else 'already exists.'
    else:
      return None, False, 'does not match series.'

  def shape(self, d=2):
    return self.series.shape(d)

class Template(models.Model):
  # connections
  composite = models.ForeignKey(Composite, related_name='templates')

  # properties
  name = models.CharField(max_length=255)
  rx = models.CharField(max_length=255)
  rv = models.CharField(max_length=255)

  # methods
  def __str__(self):
    return '{}: {}'.format(self.name, self.rx)

  def match(self, string):
    return re.match(self.rx, string)

  def dict(self, string):
    return self.match(string).groupdict()

### GONS
class Channel(models.Model):
  # connections
  composite = models.ForeignKey(Composite, related_name='channels')

  # properties
  name = models.CharField(max_length=255)

  # methods
  def __str__(self):
    return '{} > {}'.format(self.composite.id_token, self.name)

  def segment(self, marker_channel_name):

    # setup
    print('getting marker channel')
    marker_channel = self.composite.channels.get(name=marker_channel_name)

    # 1. create primary from markers with marker_channel
    print('running primary')
    marker_channel_primary_name = marker_channel.primary()

    # 2. create pipeline and run
    print('run pipeline')
    unique, suffix_id = self.composite.experiment.save_marker_pipeline(series_name=self.composite.series.name, primary_channel_name=marker_channel_primary_name, secondary_channel_name=self.name)
    self.composite.experiment.run_pipeline()

    print('import masks')
    # 3. import masks and create new mask channel
    cp_out_file_list = [f for f in os.listdir(self.composite.experiment.cp_path) if (suffix_id in f and '.tiff' in f)]
    # make new channel that gets put in mask path
    cp_template = self.composite.templates.get(name='cp')
    mask_template = self.composite.templates.get(name='mask')
    mask_channel = self.composite.mask_channels.create(name=suffix_id)

    for cp_out_file in cp_out_file_list:
      array = imread(os.path.join(self.composite.experiment.cp_path, cp_out_file))
      metadata = cp_template.dict(cp_out_file)
      mask_channel.get_or_create_mask(array, int(metadata['t']))

    print('import data files')
    # 4. import datafiles and access data
    data_file_list = [f for f in os.listdir(self.composite.experiment.cp_path) if (unique in f and '.csv' in f)]
    for df_name in data_file_list:
      data_file, data_file_created, status = self.composite.get_or_create_data_file(self.composite.experiment.cp_path, df_name)

    # 5. create cells and cell instances from tracks
    cell_data_file = self.composite.data_files.get(id_token=unique, data_type='Cells')
    data = cell_data_file.load()

    # load masks and associate with grayscale id's
    for t in range(self.composite.series.ts):
      mask_mask = mask_channel.masks.get(t=t)
      mask = mask_mask.load()

      t_data = list(filter(lambda d: int(d['ImageNumber'])-1==t, data))

      markers = marker_channel.markers.filter(track_instance__t=t)
      for marker in markers:
        # 1. create cell
        cell, cell_created = self.composite.experiment.cells.get_or_create(series=self.composite.series, track=marker.track)

        # 2. create cell instance
        cell_instance, cell_instance_created = cell.instances.get_or_create(experiment=cell.experiment,
                                                                            series=cell.series,
                                                                            track_instance=marker.track_instance)

        # 3. create cell mask
        cell_mask = cell_instance.masks.create(experiment=cell.experiment,
                                               series=cell.series,
                                               cell=cell,
                                               mask=mask_mask,
                                               marker=marker,
                                               gray_value_id=mask[marker.c, marker.r])

        cell_mask_data = list(filter(lambda d: int(d['ObjectNumber'])==cell_mask.gray_value_id, t_data))[0]

        # 4. assign data
        cell_mask.AreaShape_Area = float(cell_mask_data['AreaShape_Area'])
        cell_mask.t = t
        cell_mask.AreaShape_Perimeter = float(cell_mask_data['AreaShape_Perimeter'])
        cell_mask.r = cell_mask.marker.r
        cell_mask.c = cell_mask.marker.c
        cell_mask.save()

  def segment_regions(self, region_marker_channel_name):
    pass

  # methods
  def region_labels(self):
    return np.unique([region_marker.region_track.name for region_marker in self.region_markers.all()])

  def get_or_create_gon(self, array, t, r=0, c=0, z=0, rs=None, cs=None, zs=1, path=None):
    # self.defaults
    rs = self.composite.series.rs if rs is None else rs
    cs = self.composite.series.cs if cs is None else cs
    path = self.composite.experiment.composite_path if path is None else path

    # build
    gon, gon_created = self.gons.get_or_create(experiment=self.composite.experiment, series=self.composite.series, composite=self.composite, t=t)
    gon.set_origin(r,c,z,t)
    gon.set_extent(rs,cs,zs)

    gon.array = array
    gon.save_array(path, self.composite.templates.get(name='source'))
    gon.save()

    return gon, gon_created

  def primary(self):
    if self.composite.channels.filter(name='{}-primary'.format(self.name)).count()==0:
      if self.markers.count()!=0:
        channel_name = ''

        # 1. loop through time series
        for t in range(self.composite.series.ts):
          # load all markers for this frame
          markers = self.markers.filter(track_instance__t=t)

          # blank image
          blank = np.zeros(self.composite.shape())

          for i, marker in enumerate(markers):
            print('primary for composite {} {} {} channel {} | t{}/{}'.format(self.composite.experiment.name, self.composite.series.name, self.composite.id_token, self.name, t, self.composite.series.ts), end='\n' if t==self.composite.series.ts-1 else '\r')
            blank[marker.c-3:marker.c+2, marker.r-3:marker.r+2] = 255

          marker_channel, marker_channel_created = self.composite.channels.get_or_create(name='{}-primary'.format(self.name))
          channel_name = marker_channel.name
          blank_gon, blank_gon_created = marker_channel.get_or_create_gon(blank, t)

        return channel_name

      else:
        print('primary for composite {} {} {} channel {} | no markers have been defined.'.format(self.composite.experiment.name, self.composite.series.name, self.composite.id_token, self.name))

    else:
      print('primary for composite {} {} {} channel {} has already been created.'.format(self.composite.experiment.name, self.composite.series.name, self.composite.id_token, self.name))
      return '{}-primary'.format(self.name)

  def region_primary(self):
    if self.composite.channels.filter(name='{}-regions'.format(self.name)).count()==0:
      if self.region_markers.count()!=0:
        # 1. loop through time series
        for t in range(self.composite.series.ts):
          # load all markers for this frame
          markers = self.region_markers.filter(region_track_instance__t=t)

          blank_sum = np.zeros(self.composite.shape()) # gather all primaries

          for name in self.region_labels():

            # markers per region
            region_markers = markers.filter(region_track__name=name)

            # blank image
            blank = np.zeros(self.composite.shape())

            for marker in region_markers:
              blank[marker.r, marker.c] = 255

            for r in range(blank.shape[0]):
              for c in range(blank.shape[1]):
                print('region primary for composite {} {} {} channel {} | t{}/{} region {} r{} c{}'.format(self.composite.experiment.name, self.composite.series.name, self.composite.id_token, self.name, t, self.composite.series.ts-1, name, r, c), end='\n' if t==self.composite.series.ts-1 else '\r')
                up = blank[:r,c]
                down = blank[r:,c]
                left = blank[r,:c]
                right = blank[r,c:]
                if up.sum()>0 and down.sum()>0 and left.sum()>0 and right.sum()>0:
                  blank[r,c] = 255

            blank_sum += blank

          # create channel and add blank sum
          region_channel, region_channel_created = self.composite.channels.get_or_create(name='{}-regions'.format(self.name))
          blank_sum_gon, blank_sum_gon_created = region_channel.get_or_create_gon(blank_sum, t)

      else:
        print('region primary for composite {} {} {} channel {} | no region markers have been defined.'.format(self.composite.experiment.name, self.composite.series.name, self.composite.id_token, self.name))

    else:
      print('region primary for composite {} {} {} channel {} has already been created.'.format(self.composite.experiment.name, self.composite.series.name, self.composite.id_token, self.name))

class Gon(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='gons')
  series = models.ForeignKey(Series, related_name='gons')
  composite = models.ForeignKey(Composite, related_name='gons', null=True)
  template = models.ForeignKey(Template, related_name='gons', null=True)
  channel = models.ForeignKey(Channel, related_name='gons')
  gon = models.ForeignKey('self', related_name='gons', null=True)

  # properties
  id_token = models.CharField(max_length=8, default='')

  # 1. origin
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)
  t = models.IntegerField(default=-1)

  # 2. extent
  rs = models.IntegerField(default=-1)
  cs = models.IntegerField(default=-1)
  zs = models.IntegerField(default=1)

  # 3. data
  array = None

  # methods
  def set_origin(self, r, c, z, t):
    self.r = r
    self.c = c
    self.z = z
    self.t = t
    self.save()

  def set_extent(self, rs, cs, zs):
    self.rs = rs
    self.cs = cs
    self.zs = zs
    self.save()

  def shape(self):
    if self.zs==1:
      return (self.rs, self.cs)
    else:
      return (self.rs, self.cs, self.zs)

  def t_str(self):
    return str('0'*(len(str(self.series.ts)) - len(str(self.t))) + str(self.t))

  def z_str(self, z=None):
    return str('0'*(len(str(self.series.zs)) - len(str(self.z if z is None else z))) + str(self.z if z is None else z))

  def load(self):
    self.array = []
    for path in self.paths.order_by('z'):
      array = imread(path.url)
      self.array.append(array)
    self.array = np.dstack(self.array).squeeze() # remove unnecessary dimensions
    return self.array

  def save_array(self, root, template):
    # 1. iterate through planes in bulk
    # 2. for each plane, save plane based on root, template
    # 3. create path with url and add to gon

    if not os.path.exists(root):
      os.makedirs(root)

    file_name = template.rv.format(self.experiment.name, self.series.name, self.channel.name, self.t, '{}')
    url = os.path.join(root, file_name)

    if len(self.array.shape)==2:
      imsave(url.format(self.z), self.array)
      self.paths.create(composite=self.composite if self.composite is not None else self.gon.composite, channel=self.channel, template=template, url=url.format(self.z), file_name=file_name.format(self.z), t=self.t, z=self.z)

    else:
      for z in range(self.array.shape[2]):
        plane = self.array[:,:,z].copy()

        imsave(url.format(z+self.z), plane) # z level is offset by that of original gon.
        self.paths.create(composite=self.composite, channel=self.channel, template=template, url=url.format(self.z), file_name=file_name.format(self.z), t=self.t, z=z+self.z)

        # create gons
        gon = self.gons.create(experiment=self.composite.experiment, series=self.composite.series, channel=self.channel, template=template)
        gon.set_origin(self.r, self.c, z, self.t)
        gon.set_extent(self.rs, self.cs, 1)

        gon.array = plane.copy().squeeze()

        gon.save_array(self.experiment.composite_path, template)
        gon.save()

### GON STRUCTURE AND MODIFICATION ###
class Path(models.Model):
  # connections
  composite = models.ForeignKey(Composite, related_name='paths')
  gon = models.ForeignKey(Gon, related_name='paths')
  channel = models.ForeignKey(Channel, related_name='paths')
  template = models.ForeignKey(Template, related_name='paths')

  # properties
  url = models.CharField(max_length=255)
  file_name = models.CharField(max_length=255)
  t = models.IntegerField(default=0)
  z = models.IntegerField(default=0)

  # methods
  def __str__(self):
    return '{}: {}'.format(self.composite.id_token, self.file_name)

  def load(self):
    return imread(self.url)

class Mod(models.Model):
  # connections
  composite = models.ForeignKey(Composite, related_name='mods')

  # properties
  id_token = models.CharField(max_length=8)
  algorithm = models.CharField(max_length=255)
  date_created = models.DateTimeField(auto_now_add=True)

  # methods
  def run(self):
    ''' Runs associated algorithm to produce a new channel. '''
    algorithm = getattr(algorithms, self.algorithm)
    algorithm(self.composite, self.id_token, self.algorithm)

### MASKS
class MaskChannel(models.Model):
  # connections
  composite = models.ForeignKey(Composite, related_name='mask_channels')

  # properties
  name = models.CharField(max_length=255)

  # methods
  def __str__(self):
    return 'mask {} > {}'.format(self.composite.id_token, self.name)

  def get_or_create_mask(self, array, t, r=0, c=0, rs=None, cs=None, path=None):
    # self.defaults
    rs = self.composite.series.rs if rs is None else rs
    cs = self.composite.series.cs if cs is None else cs
    path = self.composite.experiment.composite_path if path is None else path

    # build
    mask, mask_created = self.masks.get_or_create(experiment=self.composite.experiment, series=self.composite.series, composite=self.composite, t=t)
    mask.set_origin(r,c,t)
    mask.set_extent(rs,cs)

    mask.array = array
    mask.save_array(path, self.composite.templates.get(name='mask'))
    mask.save()

    return mask, mask_created

class Mask(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='masks')
  series = models.ForeignKey(Series, related_name='masks')
  composite = models.ForeignKey(Composite, related_name='masks', null=True)
  channel = models.ForeignKey(MaskChannel, related_name='masks')
  template = models.ForeignKey(Template, related_name='masks', null=True)

  # properties
  id_token = models.CharField(max_length=8, default='')
  url = models.CharField(max_length=255)
  file_name = models.CharField(max_length=255)

  # 1. origin
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  t = models.IntegerField(default=-1)

  # 2. extent
  rs = models.IntegerField(default=-1)
  cs = models.IntegerField(default=-1)

  # 3. data
  array = None

  # methods
  def set_origin(self, r, c, t):
    self.r = r
    self.c = c
    self.t = t
    self.save()

  def set_extent(self, rs, cs):
    self.rs = rs
    self.cs = cs
    self.save()

  def shape(self):
    return (self.rs, self.cs)

  def t_str(self):
    return str('0'*(len(str(self.series.ts)) - len(str(self.t))) + str(self.t))

  def load(self):
    array = imread(self.url)
    self.array = (exposure.rescale_intensity(array * 1.0) * (len(np.unique(array)) - 1)).astype(int) # rescale to contain integer grayscale id's.
    return self.array

  def save_array(self, root, template):
    # 1. iterate through planes in bulk
    # 2. for each plane, save plane based on root, template
    # 3. create path with url and add to gon

    if not os.path.exists(root):
      os.makedirs(root)

    self.file_name = template.rv.format(self.experiment.name, self.series.name, self.channel.name, self.t)
    self.url = os.path.join(root, self.file_name)

    imsave(self.url, self.array)

### DATA
class DataFile(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='data_files')
  series = models.ForeignKey(Series, related_name='data_files')
  composite = models.ForeignKey(Composite, related_name='data_files')
  template = models.ForeignKey(Template, related_name='data_files')

  # properties
  id_token = models.CharField(max_length=8)
  data_type = models.CharField(max_length=255)
  url = models.CharField(max_length=255)
  file_name = models.CharField(max_length=255)

  data = []

  # methods
  def load(self):
    self.data = []
    with open(self.url) as df:
      headers = []
      for n, line in enumerate(df.readlines()):
        if n==0: # title
          headers = line.rstrip().split(',')
        else:
          line_dict = {}
          for i, token in enumerate(line.rstrip().split(',')):
            line_dict[headers[i]] = token
          self.data.append(line_dict)
    return self.data

    # parse cell profiler results spreadsheet into array that can be used to make cell instances
    # 1. generate dictionary keys from title line
    # 2. return array of dictionaries
