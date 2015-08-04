# test_segmented_mask_z

from mod_base import *

# goal:
# 1. given the segmentation of zcomp, find z at each point and generate a z difference image.
# 2. use this image to modify zbf and redo the segmentation

# method:
# 1. import segmentation of zcomp
# 2. make into mask to cover zmod
# 3. generate zdiff.

# results:

# paths
zcomp_segmented = load(join(t_path, 'base_segmentation', 'results'), 'zcomp.tiff')

# cut and rescale zmod to size of environment
cut_zmod = (cut(zmod) * 98).astype(int)
masked_zmod = np.ma.array(cut_zmod, mask=(zcomp_segmented!=1.0), fill_value=0)

# get levels inside mask
levels = [l for l in np.unique(masked_zmod.filled()) if l!=0]
z_diff = np.zeros(cut_zmod.shape)

for level in levels:
  level_z_diff = np.abs(np.ones(cut_zmod.shape) * level - cut_zmod)
  level_z_diff = 1.0 - exposure.rescale_intensity(level_z_diff * 1.0)
  level_z_diff = gf(level_z_diff, sigma=5)

  z_diff += level_z_diff.copy()

# cut and modify zbf
cut_zbf = cut(zbf)

mod = cut_zbf * z_diff

# plt.imshow(mod, cmap='Greys_r')
# plt.show()

imsave(join(t_path, 'segmented_mask_z', 'zdiff.png'), mod)
