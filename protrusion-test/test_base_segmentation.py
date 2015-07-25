# test_base_segmentation

from mod_base import *
from scipy.ndimage.morphology import binary_erosion as erode
from scipy.ndimage.morphology import binary_dilation as dilate
from scipy.signal import find_peaks_cwt
from scipy.ndimage import distance_transform_edt

# goal:
# 1. simple segmentation of the brightfield levels, zbf, and zcomp
# 2. make no attempt to improve segmentation of the protrusions using either zcomp or cell profiler
# 3. measure protrusion length using signal analysis of edge as before

# method:
# 1. using bounding box defined in mod_base, cut images to size and export to directories for segmentation
# 2. run cell profiler
# 3. import images and categorize objects by protrusion length
# 4. plot results

# results:
# No failure here. Just testing how the segmentation changes with Z. When the interior of the cell comes closer to the background and
# the edges become less defined, the recognition extends to the boundaries. I need some good way of testing whether this
# has happened. Right now, I use the box_edges_on method, which tests for "on" edges of the chosen bounding box. This is
# unreliable since I will not have a bounding box in practical operation.
#
# I need to know what the best level for segmenting the protrusions is. I think I will combine any information from here to
# a method based on difference in z level from points inside the mask. This will be my third test.

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
  # 1. get edge
  # 2. for each point, get distance and angle from point with highest distance transform
  # 3. trace along edge and copy into sorted array
  # 4. roll array to position minimum on edge. This ensures that no peaks lie on the edge and can be segmented properly
  # 5. return peaks with peak detection

  # for cpz, cp_img in cp.items():
  #   if cpz not in [27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 52]:
  #   # if cpz in [25]:
  #     img = cp_img['img']
  #
  #     img = erode(dilate(img, iterations=3), iterations=3)
  #
  #     (max_r, max_c), sorted_edge = get_sorted_edge(img)
  #     print(max_r, max_c)
  #
  #     y = np.array([np.sqrt((e[0]-max_r)**2 + (e[1]-max_c)**2) for e in sorted_edge])
  #     x = np.array(list(range(len(sorted_edge))))
  #     x = x - np.argmax(y)
  #
  #     x = x / len(x)
  #     # y = y / y.max()
  #
  #     plt.plot(x, y)
  #
  # plt.show()

  ##### PROTRUSIONS

  ##### SUM

  cp_sum = np.zeros(cp[0]['img'].shape)
  for cpz, cp_img in cp.items():
    img = cp_img['img'].astype(int)
    if not box_edges_on(img):
      cp_sum += img

  m = exposure.rescale_intensity(cp_sum * 1.0) + cut(zmean)

  plt.imshow(m, cmap='Greys_r')
  plt.show()

  ##### SUM

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
