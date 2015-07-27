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
marker = load(join(test_path, 'marker.png'))
zcomp_cp = load(join(test_path, 'zcomp_cp.tiff'))
zdiff_cp = load(join(test_path, 'zdiff_cp.tiff'))

# TEST 1: erode zdiff_cp until it touches zcomp_cp
def edges_touching(binary_inside, binary_outside):
  # 1. get edge of outside
  binary_outside_edge = binary_edge(binary_outside).astype(int)

  # 2. add to inside
  binary_sum = binary_outside_edge + binary_inside.astype(int)

  # 3. if any pixel value is 2, then touching
  return np.any(binary_sum==2)

# while not_touching(zdiff_cp, zcomp_cp):
#   erode(zdiff_cp)
print(edges_touching(zcomp_cp, zdiff_cp))

# cut and modify zbf
# cut_zbf = cut(zbf)

# mod = cut_zbf * z_diff

# plt.imshow(mod, cmap='Greys_r')
# plt.show()

# imsave(join(t_path, 'segmented_mask_z', 'zdiff.png'), mod)
