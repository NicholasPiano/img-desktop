# expt.command: step01_input

# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# local
from apps.expt.models import Experiment
from apps.img.models import Gon, Composite
from apps.cell.models import Marker
from apps.expt.data import *
from apps.expt.util import *
from apps.img.util import scan_point

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

    composite = Composite.objects.get(experiment__name='260714', series__name='15')

    # frames
    previous_frame_index = 0
    target_frame_index = 1
    next_frame_index = 2

    # stacks
    previous_gfp_stack = composite.gons.get(t=previous_frame_index, channel__name='0')
    previous_bf_stack = composite.gons.get(t=previous_frame_index, channel__name='1')

    target_gfp_stack = composite.gons.get(t=target_frame_index, channel__name='0')
    target_bf_stack = composite.gons.get(t=target_frame_index, channel__name='1')
    target_zmean_single = composite.gons.get(t=target_frame_index, channel__name='-zmean')
    target_zbf_single = composite.gons.get(t=target_frame_index, channel__name='-zbf')
    target_zmod_single = composite.gons.get(t=target_frame_index, channel__name='-zmod')

    next_gfp_stack = composite.gons.get(t=next_frame_index, channel__name='0')
    next_bf_stack = composite.gons.get(t=next_frame_index, channel__name='1')

    # images
    # previous_gfp = previous_gfp_stack.load()
    # previous_bf = previous_bf_stack.load()

    target_gfp = target_gfp_stack.load()
    target_bf = target_bf_stack.load()
    target_zmean = target_zmean_single.load()
    target_zbf = target_zbf_single.load()
    target_zmod = target_zmod_single.load() / 255.0 * composite.series.zs

    # next_gfp = next_gfp_stack.load()
    # next_bf = next_bf_stack.load()

    # 1. find maximum from marker
    marker = composite.markers.get(pk=124)

    
