# expt.command: step01_input

# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# local
from apps.expt.models import Experiment
from apps.img.models import Gon
from apps.expt.data import *
from apps.expt.util import *

# util
import os
import numpy as np
from os.path import join, exists, splitext, dirname
from optparse import make_option
from subprocess import call
import shutil as sh
import matplotlib.pyplot as plt

spacer = ' ' *  20

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

  )

  args = ''
  help = ''

  def handle(self, *args, **options):
    g = Gon.objects.get(pk=1081)
    binary_image, object_count = g.segment_primary(60, 80)

    print(object_count)
    plt.imshow(binary_image)
    plt.show()
