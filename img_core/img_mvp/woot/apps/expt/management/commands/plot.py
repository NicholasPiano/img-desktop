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
import matplotlib.pyplot as plt

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

    make_option('--cells', # option that will appear in cmd
      action='store', # no idea
      dest='cells', # refer to this in options variable
      default='', # some default
      help='' # who cares
    ),

    make_option('--properties', # option that will appear in cmd
      action='store', # no idea
      dest='properties', # refer to this in options variable
      default='', # some default
      help='' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):

    # vars
    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
    linestyles = ['-', '-+', '--', '-*']
    experiment_name = options['expt']
    series_name = options['series']
    cells = [int(c) for c in options['cells'].split(',')]
    properties = [p for p in options['properties'].split(',')]

    plot_headers = {
      'r': '(units um) row value',
      'c': '(units um) column value',
      'z': '(units um) plane value',
      'vr': '(units um/min) row speed',
      'vr': '(units um/min) column speed',
      'vr': '(units um/min) plane speed',
      'v': '(units um/min) total speed',
      'area': '(units um^2) area of attachment, projection',
      'compactness':'',
      'eccentricity':'',
      'eulerNumber':'',
      'formFactor':'',
      'orientation':'',
      'solidity':'',
    }

    # 1. create experiment and series
    if experiment_name!='' and series_name!='':
      experiment = Experiment.objects.get(name=experiment_name)
      series = experiment.series.get(name=series_name)

      if len(properties) <= 2 and len(properties) > 0:
        flag = True
        for p in properties:
          if p not in plot_headers.keys():
            flag = False

        if flag:
          if len(cells) > 0:
            fig = plt.figure()

            ax1 = fig.add_subplot(111)
            ax1.set_xlabel('Time (min)')
            ax1.set_ylabel('"{}" ... {}'.format(properties[0], plot_headers[properties[0]]))

            for i, cell_id in enumerate(cells):
              cell = series.cells.get(pk=cell_id)
              cell_x = [cell_instance.T() for cell_instance in cell.instances.order_by('t')]

              property_dict = {
                'r': [cell_instance.R() for cell_instance in cell.instances.order_by('t')],
                'c': [cell_instance.C() for cell_instance in cell.instances.order_by('t')],
                'z': [cell_instance.Z() for cell_instance in cell.instances.order_by('t')],
                'vr': [cell_instance.VR() for cell_instance in cell.instances.order_by('t')],
                'vc': [cell_instance.VC() for cell_instance in cell.instances.order_by('t')],
                'vz': [cell_instance.VZ() for cell_instance in cell.instances.order_by('t')],
                'v': [cell_instance.V() for cell_instance in cell.instances.order_by('t')],
                'area': [cell_instance.A() for cell_instance in cell.instances.order_by('t')],
                'compactness': [cell_instance.AreaShape_Compactness for cell_instance in cell.instances.order_by('t')],
                'eccentricity': [cell_instance.AreaShape_Eccentricity for cell_instance in cell.instances.order_by('t')],
                'eulerNumber': [cell_instance.AreaShape_EulerNumber for cell_instance in cell.instances.order_by('t')],
                'formFactor': [cell_instance.AreaShape_FormFactor for cell_instance in cell.instances.order_by('t')],
                'orientation': [cell_instance.AreaShape_Orientation for cell_instance in cell.instances.order_by('t')],
                'solidity': [cell_instance.AreaShape_Solidity for cell_instance in cell.instances.order_by('t')],
              }
              cell_y = property_dict[properties[0]]

              ax1.plot(cell_x, cell_y, '-', label='cell {}'.format(cell_id))

            if len(properties)>1:
              ax2 = fig.add_subplot(111, frameon=False)

              ax2.set_xlabel('Time (frames)')
              ax2.xaxis.set_label_position('top')
              ax2.xaxis.set_ticks_position('top')
              ax2.set_ylabel('"{}" ... {}'.format(properties[1], plot_headers[properties[1]]))
              ax2.yaxis.set_label_position('right')
              ax2.yaxis.set_ticks_position('right')

              for i, cell_id in enumerate(cells):
                cell = series.cells.get(pk=cell_id)
                cell_x = [cell_instance.t for cell_instance in cell.instances.order_by('t')]

                property_dict = {
                  'r': [cell_instance.R() for cell_instance in cell.instances.order_by('t')],
                  'c': [cell_instance.C() for cell_instance in cell.instances.order_by('t')],
                  'z': [cell_instance.Z() for cell_instance in cell.instances.order_by('t')],
                  'vr': [cell_instance.VR() for cell_instance in cell.instances.order_by('t')],
                  'vc': [cell_instance.VC() for cell_instance in cell.instances.order_by('t')],
                  'vz': [cell_instance.VZ() for cell_instance in cell.instances.order_by('t')],
                  'v': [cell_instance.V() for cell_instance in cell.instances.order_by('t')],
                  'area': [cell_instance.A() for cell_instance in cell.instances.order_by('t')],
                  'compactness': [cell_instance.AreaShape_Compactness for cell_instance in cell.instances.order_by('t')],
                  'eccentricity': [cell_instance.AreaShape_Eccentricity for cell_instance in cell.instances.order_by('t')],
                  'eulerNumber': [cell_instance.AreaShape_EulerNumber for cell_instance in cell.instances.order_by('t')],
                  'formFactor': [cell_instance.AreaShape_FormFactor for cell_instance in cell.instances.order_by('t')],
                  'orientation': [cell_instance.AreaShape_Orientation for cell_instance in cell.instances.order_by('t')],
                  'solidity': [cell_instance.AreaShape_Solidity for cell_instance in cell.instances.order_by('t')],
                }
                cell_y = property_dict[properties[1]]

                ax2.plot(cell_x, cell_y, '--', label='cell {}'.format(cell_id))

            plt.title('{} for cells {}'.format(properties, cells), y=1.2, x=1.2)
            plt.legend()
            plt.show()

          else:
            print('Please enter some cells to plot')

        else:
          print('Please enter one or two properties from this list:')
          for header, description in plot_headers.items():
            print('"{}" ... {}'.format(header, description))

      else:
        print('Please enter one or two properties:')
        for header, description in plot_headers.items():
          print('"{}" ... {}'.format(header, description))

    else:
      print('Please enter an experiment and series.')
