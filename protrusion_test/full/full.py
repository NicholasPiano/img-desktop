
import os
from os.path import join, exists
import numpy as np
from scipy.misc import imread, imsave
import matplotlib.pyplot as plt
from skimage import exposure
from scipy.ndimage.measurements import label
from scipy.ndimage.morphology import distance_transform_edt

def str_value(v, vs):
  v_str_len = len(str(v))
  vs_str_len = len(str(vs))

  diff = vs_str_len - v_str_len
  return '{}{}'.format('0'*diff, v)

input_path = '/Volumes/TRANSPORT/data/puzzle/260714/'
composite_path = join(input_path, 'composite')
cp_path = join(input_path, 'cp')

if not exists(cp_path):
  os.mkdir(cp_path)

# images
t = 0
ts = 120
zmean = exposure.rescale_intensity(imread(join(composite_path, '260714_s15_ch-zmean_t{}_z00.tiff'.format(str_value(t, ts)))) * 1.0)

zmod = exposure.rescale_intensity(imread(join(composite_path, '260714_s15_ch-zmod_t{}_z00.tiff'.format(str_value(t, ts)))) * 1.0)
zmod = (zmod * 75).astype(int)

zbf = exposure.rescale_intensity(imread(join(composite_path, '260714_s15_ch-zbf_t{}_z00.tiff'.format(str_value(t, ts)))) * 1.0)
primary = exposure.rescale_intensity(imread(join(composite_path, '260714_s15_ch-zbf-primary_t{}_z00.tiff'.format(str_value(t, ts)))) * 1.0).astype(int)


# segmentation
zcomp = zbf * zmean

# imsave(join(cp_path, 'zcomp_t{}.png'.format(str_value(t,ts))), zcomp)
# imsave(join(cp_path, 'primary_t{}.png'.format(str_value(t,ts))), primary)


# zhalo mod
zhalo = np.zeros(zbf.shape)
L, n = label(primary)

for i in [u for u in np.unique(L) if u>0]:
  coords = zip(list(np.where(L==i)[0]), list(np.where(L==i)[1]))
  z_i = int(np.mean([zmod[c[0], c[1]] for c in coords]))

  component = 1.0 - np.abs(z_i - zmod) / np.max(zmod)
  component = component * component
  d = distance_transform_edt(1.0 - (L==i).astype(int))
  d = (d.max() - d) / d.max()
  zhalo = np.dstack([component * d, zhalo])

zhalo = np.max(zhalo, axis=2) * zbf
imsave(join(cp_path, 'zhalo_t{}.png'.format(str_value(t,ts))), zhalo)

# plt.imshow(zhalo*zbf, cmap='Greys_r')
# plt.show()
