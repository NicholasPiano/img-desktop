# test_custom_erode

from mod_base import *
from scipy.ndimage.interpolation import map_coordinates

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

# TEST 1: osciallating dilation and erosion
'''
cycle_method_inside = [erode, dilate, dilate]
cycle_method_outside = [erode, dilate, erode]
cycle = 0
count = 0
while not edges_touching(zcomp_cp, zdiff_cp):
  # inside
  zcomp_cp = cycle_method_inside[cycle](zcomp_cp)

  # outside
  zdiff_cp = cycle_method_outside[cycle](zdiff_cp)

  # cycle
  count += 1
  cycle = count % 3
  print(count)
'''

# TEST 2: peak matching: FAILED
'''
inside = dilate(erode(zcomp_cp.copy()))
outside = dilate(erode(zdiff_cp.copy()))

(inside_r, inside_c), inside_edge = get_sorted_edge(inside)
(outside_r, outside_c), outside_edge = get_sorted_edge(outside)

# 1. for each point on the inner edge, need to pick a point on the outer edge.
# 2. pick three points. inside, outside, and a point equidistant from both
# 3. get angles for all three

v = np.matrix(((outside_r - inside_r), (outside_c - inside_c)))
r = np.matrix(((math.cos(math.pi/3), -math.sin(math.pi/3)),(math.sin(math.pi/3), math.cos(math.pi/3))))

third = np.array(v * r + np.matrix((inside_r, inside_c)))
third_r, third_c = tuple(third[0].astype(int).tolist())
print(third_r, third_c)

# pairs = []
# for r,c in inside_edge:
  # find corresponding point in outer edge
  # 1. find angle
  # angle = math.atan2(r-inside_r,c-inside_c)
  # a.append(angle)

  # print(inside_r,inside_c,r,c,angle)

# cut and modify zbf
# cut_zbf = cut(zbf)

img = binary_edge(inside) + binary_edge(outside)
img[inside_r,inside_c] = 255
img[outside_r,outside_c] = 255
img[third_r,third_c] = 255
'''

# TEST 3: scatter approach. I want to see those distributions
'''
inside = dilate(erode(zcomp_cp.copy()))
outside = dilate(erode(zdiff_cp.copy()))
outside_d = distance_transform_edt(1 - inside)
edges = dilate(binary_edge(inside) + binary_edge(outside))
lines = edges.copy()
cut_zbf = cut(zbf)

(inside_r, inside_c), inside_edge = get_sorted_edge(inside)
(outside_r, outside_c), outside_edge = get_sorted_edge(outside)

count = 0
# for iR, iC in [inside_edge[0]]:
for iR, iC in inside_edge:
  for oR, oC in outside_edge:
    D = np.sqrt((oR-iR)**2 + (oC-iC)**2)
    line = [np.linspace(iR, oR, D).astype(int), np.linspace(iC, oC, D).astype(int)]

    if np.sum(edges[line]) <= 3:
      plt.plot(outside_d[line], cut_zbf[line])
'''

# TEST 4: dilate inner mask minimise distance transforms
inside = dilate(erode(zcomp_cp.copy()))
outside = dilate(erode(zdiff_cp.copy()))

cut_zbf = cut(zbf)

outside_edge = distance_transform_edt(dilate(binary_edge(outside), iterations=3))
outside_edge = 1.0 - exposure.rescale_intensity(outside_edge * 1.0)
cut_zbf *= outside_edge * outside_edge

imsave(join(t_path, 'custom_dilate', 'bounded.png'), cut_zbf)

# plt.imshow(cut_zbf, cmap='Greys_r')
# plt.show()
