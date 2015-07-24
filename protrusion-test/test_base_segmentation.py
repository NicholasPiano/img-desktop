# test_base_segmentation

from mod_base import *

# goal:
# 1. simple segmentation of the brightfield levels, zbf, and zcomp
# 2. make no attempt to improve segmentation of the protrusions using either zcomp or cell profiler
# 3. measure protrusion length using signal analysis of edge as before

# method:
# 1. using bounding box defined in mod_base, cut images to size and export to directories for segmentation
# 2. run cell profiler
# 3. import images and categorize objects by protrusion length
# 4. plot results

# paths
test_path = join(t_path, 'base_segmentation')
cp_path = join(test_path, 'cp')
img_path = join(test_path, 'img')
bf_path = join(test_path, 'bf')

for path in [cp_path, img_path, bf_path]:
  if not exists(path):
    os.mkdir(path)

# analyse or prepare
if exists(img_path) and exists(bf_path): # analyse

  # create cell profiler path
  if not exists(cp_path):
    os.mkdir(cp_path)

  # load all mask images from cellprofiler
  cp_z = lambda n: int(re.match(r'^bf_z(?P<z>[0-9]+)\.(?P<extension>.+)$', n).group('z'))
  cp = {cp_z(name):{'img':load(cp_path, name), 'name':name} for name in os.listdir(cp_path) if '.DS' not in name}

  ##### AREA
  # Z = []
  # A = []
  # for cpz, cp_img in cp.items():
  #   img = cp_img['img']
  #   a = np.sum(img==1.0)
  #   aa = img.shape[0] * img.shape[1]
  #   if a/aa < 0.07 and a > 50:
  #     print(cpz, a)
  #     Z.append(cpz)
  #     A.append(a)
  #
  # plt.plot(Z,A)
  # plt.show()
  ##### AREA

  ##### PROTRUSIONS
  

  ##### PROTRUSIONS

else:
  # create paths
  os.mkdir(img_path)
  os.mkdir(bf_path)

  # prepare images for segmentation
  save = lambda img, name: imsave(join(bf_path if 'bf_' in name else img_path, name), img)

  for img_z, img_dict in bf.items():
    save(cut(img_dict['img']), 'bf_z{}.png'.format(img_z))

  save(cut(zmod), 'zmod.png')
  save(cut(zmean), 'zmean.png')
  save(cut(zbf), 'zbf.png')
  save(cut(marker), 'marker.png')
  save(cut(zcomp), 'zcomp.png')
