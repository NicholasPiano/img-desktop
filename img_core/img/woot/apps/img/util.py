# apps.img.util

# django

# local

# util
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.morphology import binary_erosion as erode

def cut_to_black(array):
  # coordinates of non-black
  r0 = np.argmax(np.any(array, axis=1))
  r1 = array.shape[0] - np.argmax(np.any(array, axis=1)[::-1])
  c0 = np.argmax(np.any(array, axis=0))
  c1 = array.shape[1] - np.argmax(np.any(array, axis=0)[::-1])

  # return cut
  return array[r0:r1,c0:c1], (r0,c0,(r1-r0),(c1-c0))

def edge_image(array): # assumed to be binary
  return array - erode(array)

# tests
def box_overlaps_marker(mask, marker):
  # box boundaries a0, a1
  # marker coordinate b
  # test a0 < b < a1
  return mask.r < marker.r and mask.r + mask.rs > mask.r and mask.c < marker.c and mask.c + mask.cs > marker.c

def mask_overlaps_marker(loaded_mask, marker):
  # test marker point is true in loaded mask
  return loaded_mask[marker.r, marker.c]

def box_overlaps_box(mask1, mask2):
  # one of the corners of one of the boxes must be within the other box, so test all 8 corners
  edge1 = mask1.r < mask2.r
  edge2 = mask1.r + mask1.rs > mask2.r + mask2.rs
  edge3 = mask1.c < mask2.c
  edge4 = mask1.c + mask1.cs > mask2.c + mask2.cs

  return not edge1 and not edge2 and not edge3 and not edge4

def box_overlaps_mask(mask, loaded_mask):
  overlap = np.any(loaded_mask[mask.r:mask.r+mask.rs, mask.c:mask.c+mask.cs])
  return overlap

def mask_overlaps_mask(loaded_mask1, loaded_mask2):
  s = loaded_mask1.astype(int) + loaded_mask2.astype(int)
  return np.any(s==2) # doubled up areas of overlap

def mask_is_adjacent_to_mask(loaded_mask1, loaded_mask2):
  # test for overlap of dilated masks
  self_dilated_int_array = dilate(loaded_mask1.astype(int))
  mask_dilated_int_array = dilate(loaded_mask2.astype(int))

  s = self_int_array + mask_int_array
  return np.any(s==2) # doubled up areas of overlap

def nonzero_mean(img):
  mask = img<0
  masked = np.ma.array(img, mask=mask)
  return masked.mean()

def nonzero_mean_thresholded_binary(img):
  nzm = nonzero_mean(img)
  return (img>nzm).copy()

def nonzero_mean_thresholded_preserve(img):
  nzm = nonzero_mean(img)
  img[img<nzm] = 0
  return img.copy()

class _Bulk():
  def __init__(self, gon_set, gon_stack, accessor_dict):
    self.gon_set = gon_set
    self.gon_stack = gon_stack
    self.accessor_dict = accessor_dict
    self.rv = {value:key for key, value in accessor_dict.items()}

  def slice(self, z=None, pk=None):
    if z is None:
      return self.gon_stack[:,:,self.accessor_dict[pk]]
    else:
      return self.gon_stack[:,:,self.accessor_dict[self.gon_set.get(z=z).pk]]

def create_bulk_from_image_set(img_set):

  # load entire set of mask gons as 3D box with accessor dictionary
  gon_stack = None
  accessor_dict = {}

  for i, gon in enumerate(img_set):
    m = gon.load()
    accessor_dict[gon.pk] = i
    if gon_stack is None:
      gon_stack = m
    else:
      gon_stack = np.dstack([gon_stack, m])

  return _Bulk(img_set, gon_stack, accessor_dict)

# for point, distance in spiral(centre=marker.centre(), direction='+r', gap=1, steps=10):

# def sign(i):
#   return -1 if i<0 else 1
#
# class Spiral():
#   def __init__(self, origin=(0,0), primary=0, target=1, size=1):
#     self.origin = _Point(None, None, origin[0], origin[1], 0)
#     self.current = self.origin
#     self.primary = primary
#     self.target = target
#     self.size = size
#     self.points = []
#
#   def step(self, steps):
#     while step < steps:
#       next_point = _Point(self.origin, self.current, 0, 0)
#       if self.current.primary==self.target:
#         if self.current.secondary==self.target:
#           self.target = -(self.target + sign(self.target))
#           next_point.primary = current.primary + sign(self.target)
#         else:
#           next_point.secondary = current.secondary + sign(self.target)
#       else:
#         next_point.primary = current.primary + sign(self.target)
#       self.points.append(next_point)
#       self.current = next_point
#
#     return self.current
#
#
#
# class _Point():
#   def __init__(self, origin, previous, primary, secondary, s):
#     self.origin = origin
#     self.previous = previous
#     self.primary = primary
#     self.secondary = secondary
#     self.s = s

#
# class Coord():
#   def __init__(self, origin, r, c):
#     self.origin = origin
#     self.r = r
#     self.c = c
#
#   def d(self):
#     return np.sqrt((origin.r - self.r)**2 + (origin.c - self.c)**2)
#
#   def t(self):
#     return ((self.r, self.c), self.d())

# origin = Coord(centre, centre[0], centre[1])
# start = Coord(origin, {'+r':gap, '-r':-gap, '+c':0, '-c':0}[direction], {'+r':0, '-r':0, '+c':gap, '-c':-gap}[direction])
# second = Coord(origin, {'+r':gap, '-r':-gap, '+c':0, '-c':0}[direction], {'+r':0, '-r':0, '+c':gap, '-c':-gap}[direction])




# def spiral():
#
#   spiral = []
#
#   steps = 100
#   step = 0
#   target = -1
#   origin = [0,0]
#   coord = [0,0]
#
#   while step < steps:
#     if coord[0]==target:
#       if coord[1]==target:
#         target = -(target + sign(target))
#         coord[0] += sign(target)
#       else:
#         coord[1] += sign(target)
#     else:
#       coord[0] += sign(target)
#     spiral.append(coord.copy())
#     step += 1
#
#   return spiral
