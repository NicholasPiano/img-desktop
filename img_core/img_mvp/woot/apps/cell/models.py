# woot.apps.cell.models

# django
from django.db import models

# local
from apps.expt.models import Experiment, Series
from apps.img.models import Composite, Channel, Gon, Mask, MaskChannel
from apps.img.util import *

# util
import numpy as np
from scipy.ndimage.morphology import binary_dilation as dilate
from scipy.signal import find_peaks_cwt as find_peaks
import matplotlib.pyplot as plt

### Models
### MARKERS
class Track(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='tracks')
  series = models.ForeignKey(Series, related_name='tracks')
  composite = models.ForeignKey(Composite, related_name='tracks')
  channel = models.ForeignKey(Channel, related_name='tracks')

  # properties
  track_id = models.IntegerField(default=0)

class TrackInstance(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='track_instances')
  series = models.ForeignKey(Series, related_name='track_instances')
  composite = models.ForeignKey(Composite, related_name='track_instances')
  channel = models.ForeignKey(Channel, related_name='track_instances')
  track = models.ForeignKey(Track, related_name='instances')

  # properties
  t = models.IntegerField(default=0)

class Marker(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='markers')
  series = models.ForeignKey(Series, related_name='markers')
  composite = models.ForeignKey(Composite, related_name='markers')
  channel = models.ForeignKey(Channel, related_name='markers', null=True)
  gon = models.ForeignKey(Gon, related_name='markers', null=True)
  track = models.ForeignKey(Track, related_name='markers')
  track_instance = models.ForeignKey(TrackInstance, related_name='markers')

  # properties
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)

### REALITY
## CELL
class Cell(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cells')
  series = models.ForeignKey(Series, related_name='cells')
  track = models.OneToOneField(Track, related_name='cell')

  # properties
  

class CellInstance(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_instances')
  series = models.ForeignKey(Series, related_name='cell_instances')
  cell = models.ForeignKey(Cell, related_name='instances')
  track_instance = models.OneToOneField(TrackInstance, related_name='cell_instance')

  # properties
  area = models.IntegerField(default=0)

  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)
  t = models.IntegerField(default=0)

  # methods
  def R(self):
    return self.r*self.series.rmop

  def C(self):
    return self.c*self.series.cmop

  def Z(self):
    return self.z*self.series.zmop

  def T(self):
    return self.t*self.series.tpf

  def A(self):
    return self.area*self.series.rmop*self.series.cmop

  def raw_line(self):
    return '{},{},{},{},{},{},{},{}\n'.format(
      self.experiment.name,
      self.series.name,
      self.cell.pk,
      self.r,
      self.c,
      self.z,
      self.t,
      self.area,
    )

  def line(self):
    return '{},{},{},{},{},{},{},{},{}\n'.format(
      self.experiment.name,
      self.series.name,
      self.cell.pk,
      self.R(),
      self.C(),
      self.Z(),
      self.t,
      self.T(),
      self.A(),
    )

class CellMask(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_masks')
  series = models.ForeignKey(Series, related_name='cell_masks')
  cell = models.ForeignKey(Cell, related_name='masks')
  cell_instance = models.ForeignKey(CellInstance, related_name='masks')
  channel = models.ForeignKey(MaskChannel, related_name='cell_masks')
  mask = models.ForeignKey(Mask, related_name='cell_masks')
  marker = models.ForeignKey(Marker, related_name='cell_masks')

  # properties
  gray_value_id = models.IntegerField(default=0)

  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)
  t = models.IntegerField(default=0)

  # 4. cell profiler
  area = models.IntegerField(default=0)

  # methods
  def R(self):
    return self.r*self.series.rmop

  def C(self):
    return self.c*self.series.cmop

  def Z(self):
    return self.z*self.series.zmop

  def T(self):
    return self.t*self.series.tpf

  def A(self):
    return self.area*self.series.rmop*self.series.cmop

  def raw_line(self):
    return '{},{},{},{},{},{},{},{}\n'.format(
      self.experiment.name,
      self.series.name,
      self.cell.pk,
      self.r,
      self.c,
      self.z,
      self.t,
      self.area,
    )

  def line(self):
    return '{},{},{},{},{},{},{},{},{}\n'.format(
      self.experiment.name,
      self.series.name,
      self.cell.pk,
      self.R(),
      self.C(),
      self.Z(),
      self.t,
      self.T(),
      self.A(),
    )

  def load(self):
    mask = self.mask.load()
    mask[mask!=self.gray_value_id] = 0
    mask[mask>0] = 1
    return mask
