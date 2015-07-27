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
