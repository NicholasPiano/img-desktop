# import
import os
import re
import numpy as np
from skimage import exposure
from scipy.misc import imread, imsave
from scipy.ndimage.measurements import center_of_mass as com
from os.path import abspath, basename, dirname, join, normpath, exists
from scipy.ndimage.morphology import binary_erosion as erode
from scipy.ndimage.morphology import binary_dilation as dilate
from scipy.ndimage.filters import gaussian_filter as gf
import matplotlib.pyplot as plt

# paths
base_path = dirname(abspath(__file__))
t_path = join(base_path, '30')
bf_path = join(t_path, 'bf')
cell_path = join(t_path, 'cell')

# load images
z = lambda n: int(re.match(r'^(?P<experiment>.+)_s(?P<series>.+)_ch(?P<channel>.+)_t(?P<t>[0-9]+)_z(?P<z>[0-9]+)\.(?P<extension>.+)$', n).group('z'))
load = lambda p, n: exposure.rescale_intensity(imread(join(p, n)) * 1.0)

bf = {z(name):{'img':load(bf_path, name), 'name':name} for name in os.listdir(bf_path) if '.DS' not in name}
zmod = load(t_path, '050714_s13_ch-zmod_t30_z0.tiff')
zmean = load(t_path, '050714_s13_ch-zmean_t30_z0.tiff')
zbf = load(t_path, '050714_s13_ch-zbf_t30_z0.tiff')
marker = load(t_path, 'primary_t30.tif')

# vars
r0, r1 = 360, 475 # bounding box
c0, c1 = 230, 305

_C = com(marker!=0) # marker location
marker_r, marker_c = int(_C[0]), int(_C[1])
cut = lambda img: img[r0:r1,c0:c1]
cut_r, cut_c = marker_r - r0, marker_c - c0

# generate zcomp
zcomp = zbf * zmean

def binary_edge(binary):
  return binary - erode(binary)

def edges_touching(binary_inside, binary_outside):
  # 1. get edge of outside
  binary_outside_edge = binary_edge(binary_outside).astype(int)

  # 2. add to inside
  binary_sum = binary_outside_edge + binary_inside.astype(int)

  # 3. if any pixel value is 2, then touching
  return np.any(binary_sum==2)

def box_edges_on(binary_img):
  return np.any(binary_img[0,:]==1) or np.any(binary_img[:,0]==1) or np.any(binary_img[binary_img.shape[0]-1,:]==1) or np.any(binary_img[:,binary_img.shape[1]-1]==1)

def get_sorted_edge(binary_img):
  # get distance transform
  D = distance_transform_edt(binary_img)
  max_r, max_c = np.where(D==D.max())[0][0], np.where(D==D.max())[1][0]

  # cut to edge
  edge = binary_img - erode(binary_img)

  # get list of edge points
  edge_points = list(zip(np.where(edge==1)[0], np.where(edge==1)[1]))

  # sort initially by distance from distance transform maximum
  sorted_edge = [min(edge_points, key=lambda e: np.sqrt((e[0]-max_r)**2 + (e[1]-max_c)**2))]

  # count through edge points
  index = 0
  while index < len(edge_points) - 1:
    current_edge = sorted_edge[index]
    next_edge = min(filter(lambda e: e not in sorted_edge, edge_points), key=lambda d: np.sqrt((d[0]-current_edge[0])**2 + (d[1]-current_edge[1])**2))
    sorted_edge.append(next_edge)
    index += 1

  return (max_r, max_c), sorted_edge
