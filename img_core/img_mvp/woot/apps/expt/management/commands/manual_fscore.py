# expt.command: step01_input

# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# local
from apps.expt.models import Experiment
from apps.expt.data import *
from apps.expt.util import *
from apps.img.util import *

# util
import os
from os.path import join, exists
from optparse import make_option
from subprocess import call
import shutil as sh
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

  )

  args = ''
  help = ''

  def handle(self, *args, **options):

    # vars
    experiment_name = options['expt']
    series_name = options['series']

    # 1. create experiment and series
    if experiment_name!='' and series_name!='':
      experiment = Experiment.objects.get(name=experiment_name)
      series = experiment.series.get(name=series_name)
      composite = series.composites.get()

      t_channels = {}

      # compute fScore for each mask that is not
      for t in range(series.ts):

        channels = {'bmod':[], 'gmod':[], 'zmod':[]}
        # channels = {}

        for cell_instance in series.cell_instances.filter(track_instance__t=t):

          manual_mask = cell_instance.masks.get(channel__name__contains='2K5IF93D')
          manual_mask_img = manual_mask.load()

          for mask in cell_instance.masks.all():
            print('t={}, cpk={}, mpk={}'.format(t, cell_instance.pk, mask.pk))
            if 'PLG5WADE' in mask.channel.name or 'QBWO0G0U' in mask.channel.name or 'IPTELXPB' in mask.channel.name:
              mask_img = mask.load()

              fp = (mask_img - manual_mask_img > 0).sum()
              tp = (manual_mask_img & mask_img).sum()
              fn = (manual_mask_img - mask_img > 0).sum()

              # precision and recall
              precision = tp / (tp + fp)
              recall = tp / (tp + fn)

              # fscore
              fscore = 2 * (precision * recall) / (precision + recall)

              if 'gmod' in mask.channel.name:
                channels['gmod'].append(fscore)
              elif 'bmod' in mask.channel.name:
                channels['bmod'].append(fscore)
              else:
                channels['zmod'].append(fscore)

            # if mask.channel in channels:
            #   channels[mask.channel].append(fscore)
            # else:
            #   channels[mask.channel] = [fscore]

        for key, value in channels.items():
          if key in t_channels:
            t_channels[key].append(np.median(value))
          else:
            t_channels[key] = [np.median(value)]

      f = np.array(list(range(series.ts))) * series.tpf
      plt.plot(f, t_channels['zmod'], label='zEdge (R=3, $\Sigma$=3)')
      plt.plot(f, t_channels['bmod'], label='BPP')
      plt.plot(f, t_channels['gmod'], label='GMP')

      plt.legend(loc='lower right')
      plt.title('Median F-score over time for different preprocessing methods')
      plt.xlabel('Time (minutes)')
      plt.ylabel('Median F-score')
      plt.ylim([0,1.0])
      plt.show()

    else:
      print('Please enter an experiment')