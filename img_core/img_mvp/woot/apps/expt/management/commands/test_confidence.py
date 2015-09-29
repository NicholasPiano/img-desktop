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
import numpy as np
from os.path import join, exists, splitext, dirname
from optparse import make_option
from subprocess import call
import shutil as sh

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

  )

  args = ''
  help = ''

  def handle(self, *args, **options):

    # vars
    experiment_name = '050714'
    series_name = '13'

    if experiment_name!='' and series_name!='':
      experiment = Experiment.objects.get(name=experiment_name)
      series = experiment.series.get(name=series_name)

      areas = [cell_instance.AreaShape_Area for cell_instance in series.cell_instances.all()]
      mean_area = np.mean(areas)
      std_area = np.std(areas)

      for cell in series.cells.all():
        cell_areas = [cell_instance.AreaShape_Area for cell_instance in cell.instances.all()]
        mean_cell_area = np.mean(cell_areas)
        std_cell_area = np.std(cell_areas)
        mean_std_cell_area = np.mean(np.abs(np.array(areas) - mean_cell_area)) / std_cell_area

        '''
        The confidence of a cell instance should be determined by a comparison of its difference in area
        to that of the local mean and the global mean.

        '''
        print(cell.pk)
        for cell_instance in cell.instances.all():

          cell_instance_area = cell_instance.AreaShape_Area
          cell_instance_std_distance = np.abs(cell_instance_area - mean_cell_area) / std_cell_area

          print(mean_std_cell_area, cell_instance_std_distance)

        # print('global mean: {}, global std: {}, local mean: {}, local std: {}'.format(mean_area, std_area, mean_cell_area, std_cell_area))

    else:
      print('Please enter an experiment.')
