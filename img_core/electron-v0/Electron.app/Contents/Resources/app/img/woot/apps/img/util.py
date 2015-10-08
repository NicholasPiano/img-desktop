# apps.img.util

# django

# local
from apps.img.cpmath.threshold import get_threshold
from apps.img.cpmath.cpmorphology import fill_labeled_holes, strel_disk, binary_shrink, relabel, is_local_maximum
from apps.img.cpmath.smooth import smooth_with_function_and_mask
from apps.img.cpmath.propagate import propagate

# util
import scipy
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.morphology import binary_erosion as erode

def cut_to_black(array):
  # coordinates of non-black
  r0 = np.argmax(np.any(array, axis=1))
  r1 = array.shape[0] - np.argmax(np.any(array, axis=1)[::-1])
  c0 = np.argmax(np.any(array, axis=0))
  c1 = array.shape[1] - np.argmax(np.any(array, axis=0)[::-1])

  # return cut
  return array[r0:r1,c0:c1], (r0,c0,(r1-r0),(c1-c0))

def edge_image(array): # assumed to be binary
  return array - erode(array)

# tests
def box_overlaps_marker(mask, marker):
  # box boundaries a0, a1
  # marker coordinate b
  # test a0 < b < a1
  return mask.r < marker.r and mask.r + mask.rs > mask.r and mask.c < marker.c and mask.c + mask.cs > marker.c

def mask_overlaps_marker(loaded_mask, marker):
  # test marker point is true in loaded mask
  return loaded_mask[marker.r, marker.c]

def box_overlaps_box(mask1, mask2):
  # one of the corners of one of the boxes must be within the other box, so test all 8 corners
  edge1 = mask1.r < mask2.r
  edge2 = mask1.r + mask1.rs > mask2.r + mask2.rs
  edge3 = mask1.c < mask2.c
  edge4 = mask1.c + mask1.cs > mask2.c + mask2.cs

  return not edge1 and not edge2 and not edge3 and not edge4

def box_overlaps_mask(mask, loaded_mask):
  overlap = np.any(loaded_mask[mask.r:mask.r+mask.rs, mask.c:mask.c+mask.cs])
  return overlap

def mask_overlaps_mask(loaded_mask1, loaded_mask2):
  s = loaded_mask1.astype(int) + loaded_mask2.astype(int)
  return np.any(s==2) # doubled up areas of overlap

def mask_is_adjacent_to_mask(loaded_mask1, loaded_mask2):
  # test for overlap of dilated masks
  self_dilated_int_array = dilate(loaded_mask1.astype(int))
  mask_dilated_int_array = dilate(loaded_mask2.astype(int))

  s = self_int_array + mask_int_array
  return np.any(s==2) # doubled up areas of overlap

def nonzero_mean(img):
  mask = img<0
  masked = np.ma.array(img, mask=mask)
  return masked.mean()

def nonzero_mean_thresholded_binary(img):
  nzm = nonzero_mean(img)
  return (img>nzm).copy()

def nonzero_mean_thresholded_preserve(img):
  nzm = nonzero_mean(img)
  img[img<nzm] = 0
  return img.copy()

class _Bulk():
  def __init__(self, gon_set, gon_stack, accessor_dict):
    self.gon_set = gon_set
    self.gon_stack = gon_stack
    self.accessor_dict = accessor_dict
    self.rv = {value:key for key, value in accessor_dict.items()}

  def slice(self, z=None, pk=None):
    if z is None:
      return self.gon_stack[:,:,self.accessor_dict[pk]]
    else:
      return self.gon_stack[:,:,self.accessor_dict[self.gon_set.get(z=z).pk]]

def create_bulk_from_image_set(img_set):

  # load entire set of mask gons as 3D box with accessor dictionary
  gon_stack = None
  accessor_dict = {}

  for i, gon in enumerate(img_set):
    m = gon.load()
    accessor_dict[gon.pk] = i
    if gon_stack is None:
      gon_stack = m
    else:
      gon_stack = np.dstack([gon_stack, m])

  return _Bulk(img_set, gon_stack, accessor_dict)

def threshold_image(img):

  local_threshold, global_threshold = get_image_threshold(img)

  # Convert from a scale into a sigma. What I've done here
  # is to structure the Gaussian so that 1/2 of the smoothed
  # intensity is contributed from within the smoothing diameter
  # and 1/2 is contributed from outside.
  sigma = 1.0 / 0.6744 / 2.0

  def fn(img, sigma=sigma):
    return scipy.ndimage.gaussian_filter(img, sigma, mode='constant', cval=0)

  blurred_image = smooth_with_function_and_mask(img, fn, np.ones(img.shape, dtype=bool))
  binary_image = (blurred_image >= local_threshold)

  return binary_image

def get_image_threshold(img):

  # The original behavior
  image_size = np.array(img.shape[:2], dtype=int)
  block_size = image_size / 10
  block_size[block_size<50] = 50

  kwparams = {}
  kwparams['use_weighted_variance'] = True
  kwparams['two_class_otsu'] = False
  kwparams['assign_middle_to_foreground'] = False

  local_threshold, global_threshold = get_threshold('Otsu',
                                                    'Adaptive',
                                                    img,
                                                    mask = None,
                                                    labels = None,
                                                    adaptive_window_size = block_size,
                                                    **kwparams)

  return local_threshold, global_threshold

def separate_neighboring_objects(image, labeled_image, object_count, min_size, max_size):

  mask = np.ones(image.shape)

  reported_LoG_filter_diameter = 5
  reported_LoG_threshold = 0.5
  blurred_image = smooth_image(image, min_size, max_size)
  if min_size > 10:
    image_resize_factor = 10.0 / float(min_size)
    maxima_suppression_size = 7
  else:
    image_resize_factor = 1.0
    maxima_suppression_size = min_size/1.5
  reported_maxima_suppression_size = maxima_suppression_size

  maxima_mask = strel_disk(max(1, maxima_suppression_size-.5))
  distance_transformed_image = None

  # Declumping
  # Remove dim maxima
  maxima_image = get_maxima(image, blurred_image, labeled_image, maxima_mask, image_resize_factor)

  #
  # Create a marker array where the unlabeled image has a label of
  # -(nobjects+1)
  # and every local maximum has a unique label which will become
  # the object's label. The labels are negative because that
  # makes the watershed algorithm use FIFO for the pixels which
  # yields fair boundaries when markers compete for pixels.
  #
  labeled_maxima, object_count = scipy.ndimage.label(maxima_image, np.ones((3,3), bool))
  watershed_boundaries, distance = propagate(np.zeros(labeled_maxima.shape), labeled_maxima, labeled_image != 0, 1.0)

  return watershed_boundaries, object_count, reported_maxima_suppression_size, reported_LoG_threshold, reported_LoG_filter_diameter

def smooth_image(image, min_size, max_size):

  filter_size = 2.35*min_size/3.5
  if filter_size == 0:
    return image

  sigma = filter_size / 2.35
  #
  # We not only want to smooth using a Gaussian, but we want to limit
  # the spread of the smoothing to 2 SD, partly to make things happen
  # locally, partly to make things run faster, partly to try to match
  # the Matlab behavior.
  #
  filter_size = max(int(float(filter_size) / 2.0),1)
  f = (1/np.sqrt(2.0 * np.pi) / sigma * np.exp(-0.5 * np.arange(-filter_size, filter_size+1)**2 / sigma ** 2))

  def fgaussian(image):
    output = scipy.ndimage.convolve1d(image, f, axis = 0, mode='constant')
    return scipy.ndimage.convolve1d(output, f, axis = 1, mode='constant')
  #
  # Use the trick where you similarly convolve an array of ones to find
  # out the edge effects, then divide to correct the edge effects
  #

  # edge_array = fgaussian(mask.astype(float))
  # masked_image = image.copy()
  # masked_image[~mask] = 0
  # smoothed_image = fgaussian(masked_image)
  # masked_image[mask] = smoothed_image[mask] / edge_array[mask]
  # return masked_image

  return fgaussian(image)

def get_maxima(image, blurred_image, labeled_image, maxima_mask, image_resize_factor):

  if image_resize_factor < 1.0:
    shape = np.array(image.shape) * image_resize_factor
    i_j = (np.mgrid[0:shape[0],0:shape[1]].astype(float) / image_resize_factor)
    resized_image = scipy.ndimage.map_coordinates(image, i_j)
    resized_labels = scipy.ndimage.map_coordinates(labeled_image, i_j, order=0).astype(labeled_image.dtype)

  else:
    resized_image = image
    resized_labels = labeled_image

  #
  # find local maxima
  #
  if maxima_mask is not None:
    binary_maxima_image = is_local_maximum(resized_image, resized_labels, maxima_mask)
    binary_maxima_image[resized_image <= 0] = 0
  else:
    binary_maxima_image = (resized_image > 0) & (labeled_image > 0)

  if image_resize_factor < 1.0:
    inverse_resize_factor = (float(image.shape[0]) / float(binary_maxima_image.shape[0]))
    i_j = (np.mgrid[0:image.shape[0], 0:image.shape[1]].astype(float) / inverse_resize_factor)
    binary_maxima_image = scipy.ndimage.map_coordinates(binary_maxima_image.astype(float), i_j) > .5
    assert(binary_maxima_image.shape[0] == image.shape[0])
    assert(binary_maxima_image.shape[1] == image.shape[1])

  # Erode blobs of touching maxima to a single point

  shrunk_image = binary_shrink(binary_maxima_image)
  return shrunk_image

def filter_labels(labels_out, objects_segmented):
  segmented_labels = objects_segmented.copy()
  max_out = np.max(labels_out)
  # if max_out > 0:
  #   segmented_labels, m1 = cpo.size_similarly(labels_out, segmented_labels)
  #   segmented_labels[~m1] = 0
  #   lookup = scind.maximum(segmented_labels, labels_out, range(max_out+1))
  #   lookup = np.array(lookup, int)
  #   lookup[0] = 0
  #   segmented_labels_out = lookup[labels_out]
  # else:
  segmented_labels_out = labels_out.copy()

  return segmented_labels_out

def scan_point(img, rs, cs, r, c, size=0):
  r0 = r - size if r - size >= 0 else 0
  r1 = r + size + 1 if r + size + 1 <= rs else rs
  c0 = c - size if c - size >= 0 else 0
  c1 = c + size + 1 if c + size + 1 <= cs else cs

  column = img[r0:r1,c0:c1,:]
  column_1D = np.sum(np.sum(column, axis=0), axis=0)

  return column_1D
