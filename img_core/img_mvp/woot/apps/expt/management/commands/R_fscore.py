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

      # compute fScore for each mask that is not
      for R in [1,2,3,4,5]:

        R_fs = []

        for sigma in [1,2,3,4,5]:

          sigma_fs = []

          channel_name_contains = 'zedge-8-{}-{}'.format(R, sigma)

          for cell_instance in series.cell_instances.all():
            print(R, sigma, cell_instance.pk)

            gmod_mask = cell_instance.masks.get(channel__name__contains='2K5IF93D')
            # if cell_instance.masks.filter(channel__name__contains='QBWO0G0U').count()!=0:
            #   gmod_mask = cell_instance.masks.get(channel__name__contains='QBWO0G0U')

            gmod_mask_img = gmod_mask.load()

            if cell_instance.masks.filter(channel__name__contains=channel_name_contains).count()!=0:
              mask = cell_instance.masks.get(channel__name__contains=channel_name_contains)

              mask_img = mask.load()

              fp = (mask_img - gmod_mask_img > 0).sum()
              tp = (gmod_mask_img & mask_img).sum()
              fn = (gmod_mask_img - mask_img > 0).sum()

              # precision and recall
              precision = tp / (tp + fp)
              recall = tp / (tp + fn)

              # fscore
              fscore = 2 * (precision * recall) / (precision + recall)

              sigma_fs.append(fscore)

          R_fs.append(np.mean(sigma_fs))

        plt.plot([1,2,3,4,5], R_fs, label='R={}'.format(R))

      plt.legend(loc='lower right')
      plt.title('Fscore vs. increasing $\Sigma$ for constant R')
      plt.xlabel('$\Sigma$')
      plt.ylabel('Fscore')
      plt.ylim([0,1.0])
      plt.show()



    else:
      print('Please enter an experiment')
