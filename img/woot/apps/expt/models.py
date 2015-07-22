# apps.expt.models

# django
from django.db import models

# local
from apps.expt.data import *
from apps.expt.util import generate_id_token, random_string
from apps.expt.pipeline import marker_pipeline, region_pipeline

# util
import os
import re
from scipy.misc import imread, imsave
import numpy as np
import subprocess

spacer = ' ' *  20

### Models
class Experiment(models.Model):
  # properties
  name = models.CharField(max_length=255)

  # 1. location
  base_path = models.CharField(max_length=255)
  storage_path = models.CharField(max_length=255)
  composite_path = models.CharField(max_length=255)
  mask_path = models.CharField(max_length=255)
  cp_path = models.CharField(max_length=255)

  output_path = models.CharField(max_length=255)
  plot_path = models.CharField(max_length=255)
  track_path = models.CharField(max_length=255)
  data_path = models.CharField(max_length=255)
  pipeline_path = models.CharField(max_length=255)

  # 2. scaling
  rmop = models.FloatField(default=0.0) # microns over pixel ratio
  cmop = models.FloatField(default=0.0)
  zmop = models.FloatField(default=0.0)
  tpf = models.FloatField(default=0.0) # minutes in a frame

  def __str__(self):
    return self.name

  def make_paths(self, base_path):
    # fetch default paths from settings
    self.base_path = base_path
    self.storage_path = os.path.join(self.base_path, default_paths['storage'])
    self.composite_path = os.path.join(self.base_path, default_paths['composite'])
    self.cp_path = os.path.join(self.base_path, default_paths['cp'])

    self.output_path = os.path.join(self.base_path, default_paths['output'])
    self.plot_path = os.path.join(self.base_path, default_paths['plot'])
    self.track_path = os.path.join(self.base_path, default_paths['track'])
    self.data_path = os.path.join(self.base_path, default_paths['data'])
    self.pipeline_path = os.path.join(self.base_path, default_paths['pipeline'])

    self.save()

    for path in [self.composite_path, self.cp_path, self.output_path, self.plot_path, self.track_path, self.data_path, self.pipeline_path]:
      if not os.path.exists(path):
        os.makedirs(path)

  def prototype(self):
    return list(filter(lambda x: x.name==self.name, experiments))[0]

  def get_metadata(self):
    # data
    prototype = self.prototype()
    self.rmop = prototype.rmop
    self.cmop = prototype.cmop
    self.zmop = prototype.zmop
    self.tpf = prototype.tpf

    # templates
    for name, template in templates.items():
      self.templates.get_or_create(name=name, rx=template['rx'], rv=template['rv'])

    self.save()

  def is_allowed_series(self, series_name):
    return (series_name in [s.name for s in filter(lambda x: x.experiment==self.name, series)])

  def img_roots(self):
    return [self.storage_path, self.composite_path]

  def path_matches_series(self, path, series_name):

    # match template
    match_template = None
    for template in self.templates.all():
      match_template = template if template.match(path) is not None else match_template

    if match_template is not None:

      # metadata
      metadata = match_template.dict(path)

      return series_name == metadata['series']

    else:
      return False

  def get_or_create_path(self, series, root, file_name, template=None):

    # match template
    match_template = template
    if match_template is None:
      for template in self.templates.all():
        match_template = template if template.match(file_name) is not None else match_template

    if match_template is not None:

      # metadata
      metadata = match_template.dict(file_name)

      if series.name == metadata['series']:
        # channel
        channel, channel_created = self.channels.get_or_create(name=metadata['channel'])

        # path
        path, created = self.paths.get_or_create(series=series, template=match_template, channel=channel, url=os.path.join(root, file_name), file_name=file_name)
        if created:
          path.t = int(metadata['t'])
          if 'z' in metadata:
            path.z = int(metadata['z'])
          path.save()

        return path, created, 'created.' if created else 'already exists.'

      else:
        return None, False, 'does not match series.'

    else:
      return None, False, 'does not match template.'

  def save_marker_pipeline(self, series_name=None, primary_channel_name=None, secondary_channel_name=None):
    # 1. make unique key
    unique = random_string()
    unique_key = '{}{}-{}'.format(primary_channel_name, secondary_channel_name, unique)

    # 2. format and save file
    pipeline_text = marker_pipeline('{}_s{}_{}_'.format(self.name, series_name, unique), unique_key, primary_channel_name, secondary_channel_name)
    with open(os.path.join(self.pipeline_path, 'markers.cppipe'), 'w+') as open_pipeline_file:
      open_pipeline_file.write(pipeline_text)

    return unique, unique_key

  def save_region_pipeline(self, primary_channel_name=None, secondary_channel_name=None):
    # 1. make unique key
    unique_key = '{}{}-{}'.format(primary_channel_name, secondary_channel_name, random_string())

    # 2. format and save file
    pipeline_text = region_pipeline(unique_key, primary_channel_name, secondary_channel_name)
    with open(os.path.join(self.pipeline_path, 'regions.cppipe')) as open_pipeline_file:
      open_pipeline_file.write(pipeline_text)

    return unique_key

  def run_pipeline(self, key='marker'):
    pipeline = os.path.join(self.pipeline_path, 'markers.cppipe')
    if key!='marker':
      pipeline = os.path.join(self.pipeline_path, 'regions.cppipe')
    cmd = '/Applications/CellProfiler.app/Contents/MacOS/CellProfiler -c -r -i {} -o {} -p {}'.format(self.composite_path, self.cp_path, pipeline)
    subprocess.call(cmd, shell=True)

class Series(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='series')

  # properties
  name = models.CharField(max_length=255)

  # extent
  rs = models.IntegerField(default=-1)
  cs = models.IntegerField(default=-1)
  zs = models.IntegerField(default=-1)
  ts = models.IntegerField(default=-1)

  # methods
  def __str__(self):
    return '{} > {}'%(self.experiment.name, self.name)

  def prototype(self):
    return filter(lambda x: x.name==self.name and x.experiment==self.experiment.name, series)[0]

  def compose(self):

    # composite
    composite, composite_created = self.composites.get_or_create(experiment=self.experiment, id_token=generate_id_token('img', 'Composite'))

    # templates
    for template in self.experiment.templates.all():
      composite_template, composite_template_created = composite.templates.get_or_create(name=template.name)
      if composite_template_created:
        composite_template.rx = template.rx
        composite_template.rv = template.rv
        composite_template.save()

    # iterate over paths
    for channel in self.experiment.channels.all():
      composite_channel, composite_channel_created = composite.channels.get_or_create(name=channel.name)

      for t in range(self.ts):

        # path set
        path_set = self.paths.filter(channel=channel, t=t)

        # if the total number of paths is less than a great gon, do not make one. Save only individual gons.
        if path_set.count()==self.zs:

          # gon
          gon, gon_created = self.gons.get_or_create(experiment=self.experiment, composite=composite, channel=composite_channel, t=t)
          if gon_created:
            gon.set_origin(0,0,0,t)
            gon.set_extent(self.rs, self.cs, self.zs)

          for z in range(self.zs):

            # path
            path = path_set.get(channel=channel, t=t, z=z)
            template = composite.templates.get(name=path.template.name)
            gon.template = template
            gon.paths.get_or_create(composite=composite, channel=composite_channel, template=template, url=path.url, file_name=path.file_name, t=t, z=z)

            # sub gon
            sub_gon, sub_gon_created = self.gons.get_or_create(experiment=self.experiment, gon=gon, channel=composite_channel, template=template, t=t, z=z)
            E = z==self.zs-1 and t==self.ts-1
            if sub_gon_created:
              print('step01 | composing {} series {}... channel {} t{} z{}... created.{}'.format(self.experiment.name, self.name, channel.name, t, z, spacer), end='\n' if E else '\r')
              sub_gon.set_origin(0,0,z,t)
              sub_gon.set_extent(self.rs, self.cs, 1)
              sub_gon.paths.create(composite=composite, channel=composite_channel, template=template, url=path.url, file_name=path.file_name, t=t, z=z)

            else:
              print('step01 | composing {} series {}... channel {} t{} z{}... already exists.{}'.format(self.experiment.name, self.name, channel.name, t, z, spacer), end='\n' if E else '\r')

            sub_gon.save()

          gon.save()


        else: # disfuse gon structure (reduced, regions)
          L = len(path_set) - 1
          for i, path in enumerate(path_set):
            E = i==L and t==self.ts-1
            print('step01 | composing {} series {}... channel {} t{} z{}... created diffuse.{}'.format(self.experiment.name, self.name, channel.name, t, path.z, spacer), end='\n' if E else '\r')

            template = composite.templates.get(name=path.template.name)
            gon, gon_created = self.gons.get_or_create(experiment=self.experiment, composite=composite, channel=composite_channel, template=template, t=t, z=path.z)
            if gon_created:
              gon.set_origin(0,0,path.z,t)
              gon.set_extent(self.rs, self.cs, 1)

              gon.paths.create(composite=composite, channel=composite_channel, template=template, url=path.url, file_name=path.file_name, t=t, z=path.z)

            gon.save()

    composite.save()

  def vertical_sort_for_region_index(self, index):
    region = list(filter(lambda x: x.experiment==self.experiment.name and x.series==self.name and x.index==index, regions))[0]
    return region.vertical_sort_index

  def shape(self, d=2):
    if d!=3:
      return (self.rs, self.cs)
    else:
      return (self.rs, self.cs, self.zs)

class PathChannel(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='channels')

  # properties
  name = models.CharField(max_length=255)

  # methods
  def __str__(self):
    return '{}: {}'.format(self.experiment.name, self.name)

class Template(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='templates')

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

class Path(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='paths')
  series = models.ForeignKey(Series, related_name='paths')
  channel = models.ForeignKey(PathChannel, related_name='paths')
  template = models.ForeignKey(Template, related_name='paths')

  # properties
  url = models.CharField(max_length=255)
  file_name = models.CharField(max_length=255)
  t = models.IntegerField(default=0)
  z = models.IntegerField(default=0)

  # methods
  def __str__(self):
    return '{}: {}'.format(self.experiment.name, self.url)

  def load(self):
    return imread(self.url)
