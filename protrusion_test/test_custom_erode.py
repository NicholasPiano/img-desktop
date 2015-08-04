# test_custom_erode

from mod_base import *

# goal:
# 1. given the segmentation of zcomp, and the segmentation of zdiff, find a way to erode between them.
# 2. This will be the final segmentation

# method:
# 1. import segmentation of zcomp and zdiff
# 2. find distributions between edges

# results:

# paths
test_path = join(t_path, 'custom_dilate')
marker = load(test_path, 'marker.png')
zcomp_cp = load(test_path, 'zcomp_cp.tiff')
zdiff_cp = load(test_path, 'zdiff_cp.tiff')

# TEST 1: erode zdiff_cp until it touches zcomp_cp
while not edges_touching(zcomp_cp, zdiff_cp):
  zdiff_cp = erode(zdiff_cp)

# cut and modify zbf
cut_zbf = cut(zbf)

# mod = cut_zbf * z_diff

plt.imshow((zdiff_cp + load(test_path, 'zdiff_cp.tiff') + zcomp_cp) * cut_zbf, cmap='Greys_r')
plt.show()

# imsave(join(t_path, 'segmented_mask_z', 'zdiff.png'), mod)
