# import
import os
import re
from skimage import exposure
from scipy.misc import imread, imsave
from scipy.ndimage.measurements import center_of_mass as com
from os.path import abspath, basename, dirname, join, normpath, exists
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

# generate zcomp
zcomp = zbf * zmean
