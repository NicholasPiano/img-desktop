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
test_path = join(t_path, 'custom_erode')
marker = load(test_path, 'marker.png')
zcomp_cp = load(test_path, 'zcomp_cp.tiff')
zdiff_cp = load(test_path, 'zdiff_cp.tiff')

while not edges_touching(zcomp_cp, zdiff_cp):
  zcomp_cp = erode(dilate(dilate(zcomp_cp)))
  zdiff_cp = erode(erode(dilate(zdiff_cp)))

# cut and modify zbf
cut_zbf = cut(zbf)

# mod = cut_zbf * z_diff

plt.imshow((zcomp_cp) * cut_zbf, cmap='Greys_r')
plt.show()

# imsave(join(t_path, 'segmented_mask_z', 'zdiff.png'), mod)
