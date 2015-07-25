# test_scatter_segmentation

from mod_base import *

# goal:
# 1. given the segmentation of zcomp, use each point in the mask as a new marker for segmentation in the brightfield
# 2.

# method:
# 1. import segmentation of zcomp
# 2. use each pixel to make a new primary
# 3. run segmentation again
# 4. import masks and compare

# paths
zcomp_segmented = load(join(t_path, 'base_segmentation', 'results'), 'zcomp.tiff')
test_path = join(t_path, 'scatter_segmentation')
cp_path = join(test_path, 'cp')
img_path = join(test_path, 'img')
primary_path = join(test_path, 'primary')

# analyse or prepare
if exists(img_path) and exists(primary_path): # analyse

  # create cell profiler path
  if not exists(cp_path):
    os.mkdir(cp_path)

  # load all mask images from cellprofiler
  # cp_z = lambda n: int(re.match(r'^bf_z(?P<z>[0-9]+)\.(?P<extension>.+)$', n).group('z'))
  # cp = {cp_z(name):{'img':load(cp_path, name), 'name':name} for name in os.listdir(cp_path) if '.DS' not in name}

else:

  # make paths
  os.mkdir(img_path)
  os.mkdir(primary_path)

  # make primary images from each pixel on zcomp
  w = np.where(zcomp_segmented==1.0)
  pixels = list(zip(w[0], w[1]))

  for r,c in pixels:
    primary = np.zeros(cut(zcomp).shape)

    primary[cut_r-3:cut_r+2,cut_c-2:cut_c+3] = 255
    primary[r-3:r+2,c-2:c+3] = 255

    imsave(join(primary_path, 'primary_r{}_c{}.png'.format(r,c)), primary)

  imsave(join(img_path, 'zcomp.png'), cut(zcomp))
