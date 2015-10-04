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
from apps.img.util import scan_point, edge_image

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
    target_zmod = target_zmod_single.load() / 255.0 * (composite.series.zs - 1)

    # next_gfp = next_gfp_stack.load()
    # next_bf = next_bf_stack.load()

    # 1. find maximum from marker
    marker = composite.markers.get(pk=124)

    track_image = np.zeros(target_zmod.shape)

    class Traveller():
      movement_cost = 1
      directions = [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]
      spawned = False

      def __init__(self, r, c, z, direction_index, money):
        self.r = r
        self.c = c
        self.z = z
        self.direction_index = direction_index
        self.drdc()
        self.money = money

      def drdc(self):
        self.dr, self.dc = self.directions[self.direction_index]

      def move(self):
        # pick one of five directions in the direction of travel, find the one that costs the least money
        # get array of direction indices relative to current
        new_directions = [(abs(i), i if i>=0 else i+8) for i in range(self.direction_index-2, self.direction_index+3)]
        costs = []

        for cost_index, direction in new_directions:
          dr, dc = self.directions[direction]
          new_r, new_c = self.r+dr, self.c+dc

          if 0 <= new_r < composite.series.rs and 0 <= new_c < composite.series.cs and 0 <= self.r < composite.series.rs and 0 <= self.c < composite.series.cs and track_image[new_r, new_c]==0: # not out of bounds
            # print(new_r, new_c, self.r, self.c, dr, dc)
            # differences
            delta_z = int(target_zmod[new_r, new_c]) - int(target_zmod[self.r, self.c])
            new_z = target_zmod[new_r, new_c]

            delta_gfp = (int(target_gfp[new_r, new_c, new_z]) - int(target_gfp[self.r, self.c, self.z])) / float(target_gfp[self.r, self.c, self.z])
            delta_bf = (int(target_bf[new_r, new_c, new_z]) - int(target_bf[self.r, self.c, self.z])) / float(target_bf[self.r, self.c, self.z])
            delta_zmean = (int(target_zmean[new_r, new_c]) - int(target_zmean[self.r, self.c])) / float(target_zmean[self.r, self.c])

            # cost = delta_z
            # cost -= delta_gfp * 0.1
            cost = -delta_bf
            cost += -delta_zmean
            # cost *= (1.0 + 5*cost_index)
            cost += self.movement_cost
            costs.append({'cost':cost, 'direction':direction, 'z':new_z})

        if costs:
          min_direction = min(costs, key=lambda c: c['cost'])
          track_image[self.r, self.c] = 1
          self.r, self.c = tuple(np.array(self.directions[min_direction['direction']]) + np.array((self.r, self.c)))
          self.z = min_direction['z']
          self.money -= min_direction['cost']
        else:
          self.money = 0

    travellers = [Traveller(marker.r, marker.c, marker.z, 0, 10)]
    iterations = 0
    while sum([t.money for t in travellers])>0 and iterations < 50:
      iterations += 1
      for traveller in travellers:
        if traveller.money > 0:
          traveller.move()
          if not traveller.spawned:
            traveller.spawned = True
            travellers.append(Traveller(traveller.r+np.random.choice([-1,1]), traveller.c+np.random.choice([-1,1]), traveller.z, np.random.randint(0,6), 10))
        else:
          travellers.remove(traveller)

      print(len(travellers))

    # cut = target_zmean[marker.r-10: marker.r+10, marker.c-10: marker.c+10]
    # plt.imshow(cut)
    # plt.show()

    target_zmean[track_image==1] = 255
    plt.imshow(target_zmean)
    plt.show()
