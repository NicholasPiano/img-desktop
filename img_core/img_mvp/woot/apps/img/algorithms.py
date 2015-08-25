# apps.img.algorithms

# local
from apps.img.util import cut_to_black, create_bulk_from_image_set, nonzero_mean, edge_image
from apps.expt.util import generate_id_token, str_value

# util
import os
from os.path import exists, join
from scipy.misc import imsave
from scipy.ndimage.filters import gaussian_filter as gf
from scipy.ndimage.measurements import center_of_mass as com
from skimage import exposure
import numpy as np
from scipy.ndimage.measurements import label
import matplotlib.pyplot as plt
from scipy.ndimage.morphology import binary_erosion as erode
from scipy.ndimage.morphology import binary_dilation as dilate
from scipy.ndimage import distance_transform_edt

# methods
def scan_point(img, rs, cs, r, c, size=0):
  r0 = r - size if r - size >= 0 else 0
  r1 = r + size + 1 if r + size + 1 <= rs else rs
  c0 = c - size if c - size >= 0 else 0
  c1 = c + size + 1 if c + size + 1 <= cs else cs

  column = img[r0:r1,c0:c1,:]
  column_1D = np.sum(np.sum(column, axis=0), axis=0)

  return column_1D

# algorithms
def mod_zmod(composite, mod_id, algorithm):
  # template
  template = composite.templates.get(name='source') # SOURCE TEMPLATE

  # channels
  zmod_channel, zmod_channel_created = composite.channels.get_or_create(name='-zmod')
  zmean_channel, zmean_channel_created = composite.channels.get_or_create(name='-zmean')
  zbf_channel, zbf_channel_created = composite.channels.get_or_create(name='-zbf')
  zcomp_channel, zcomp_channel_created = composite.channels.get_or_create(name='-zcomp')

  # constants
  delta_z = -8
  size = 5
  sigma = 5
  template = composite.templates.get(name='source')

  # iterate over frames
  for t in range(composite.series.ts):
    print('step01 | processing mod_zmod t{}/{}...'.format(t+1, composite.series.ts), end='\r')

    # load gfp
    gfp_gon = composite.gons.get(t=t, channel__name='0')
    gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)
    gfp = gf(gfp, sigma=sigma) # <<< SMOOTHING

    # load bf
    bf_gon = composite.gons.get(t=t, channel__name='1')
    bf = exposure.rescale_intensity(bf_gon.load() * 1.0)

    # initialise images
    Z = np.zeros(composite.series.shape(d=2), dtype=int)
    Zmean = np.zeros(composite.series.shape(d=2))
    Zbf = np.zeros(composite.series.shape(d=2))
    Zcomp = np.zeros(composite.series.shape(d=2))

    # loop over image
    for r in range(composite.series.rs):
      for c in range(composite.series.cs):

        # scan
        data = scan_point(gfp, composite.series.rs, composite.series.cs, r, c, size=size)
        normalised_data = np.array(data) / np.max(data)

        # data
        z = int(np.argmax(normalised_data))
        cz = z + delta_z #corrected z
        mean = 1.0 - np.mean(normalised_data) # 1 - mean
        bfz = bf[r,c,cz]

        Z[r,c] = cz
        Zmean[r,c] = mean
        Zbf[r,c] = bfz
        Zcomp[r,c] = bfz * mean

    # images to channel gons
    zmod_gon, zmod_gon_created = composite.gons.get_or_create(experiment=composite.experiment, series=composite.series, channel=zmod_channel, t=t)
    zmod_gon.set_origin(0,0,0,t)
    zmod_gon.set_extent(composite.series.rs, composite.series.cs, 1)

    zmod_gon.array = Z
    zmod_gon.save_array(composite.series.experiment.composite_path, template)
    zmod_gon.save()

    zmean_gon, zmean_gon_created = composite.gons.get_or_create(experiment=composite.experiment, series=composite.series, channel=zmean_channel, t=t)
    zmean_gon.set_origin(0,0,0,t)
    zmean_gon.set_extent(composite.series.rs, composite.series.cs, 1)

    zmean_gon.array = exposure.rescale_intensity(Zmean * 1.0)
    zmean_gon.save_array(composite.series.experiment.composite_path, template)
    zmean_gon.save()

    zbf_gon, zbf_gon_created = composite.gons.get_or_create(experiment=composite.experiment, series=composite.series, channel=zbf_channel, t=t)
    zbf_gon.set_origin(0,0,0,t)
    zbf_gon.set_extent(composite.series.rs, composite.series.cs, 1)

    zbf_gon.array = Zbf
    zbf_gon.save_array(composite.series.experiment.composite_path, template)
    zbf_gon.save()

    zcomp_gon, zcomp_gon_created = composite.gons.get_or_create(experiment=composite.experiment, series=composite.series, channel=zcomp_channel, t=t)
    zcomp_gon.set_origin(0,0,0,t)
    zcomp_gon.set_extent(composite.series.rs, composite.series.cs, 1)

    zcomp_gon.array = Zcomp
    zcomp_gon.save_array(composite.series.experiment.composite_path, template)
    zcomp_gon.save()

def mod_tile(composite, mod_id, algorithm):

  tile_path = os.path.join(composite.experiment.video_path, 'tile', composite.series.name)
  if not os.path.exists(tile_path):
    os.makedirs(tile_path)

  for t in range(composite.series.ts):
    zbf_gon = composite.gons.get(t=t, channel__name='-zbf')
    zcomp_gon = composite.gons.get(t=t, channel__name='-zcomp')
    mask_mask = composite.masks.get(t=t, channel__name='-zcomp')

    zbf = zbf_gon.load()
    zcomp = zcomp_gon.load()
    mask = mask_mask.load()

    mask_outline = edge_image(mask>0)

    zbf_mask_r = zbf.copy()
    zbf_mask_g = zbf.copy()
    zbf_mask_b = zbf.copy()
    zbf_mask_r[mask_outline>0] = 255

    zcomp_mask_r = zcomp.copy()
    zcomp_mask_g = zcomp.copy()
    zcomp_mask_b = zcomp.copy()
    zcomp_mask_r[mask_outline>0] = 255

    # tile zbf, zbf_mask, zcomp, zcomp_mask
    top_half = np.concatenate((np.dstack([zbf, zbf, zbf]), np.dstack([zbf_mask_r, zbf_mask_g, zbf_mask_b])), axis=0)
    bottom_half = np.concatenate((np.dstack([zcomp, zcomp, zcomp]), np.dstack([zcomp_mask_r, zcomp_mask_g, zcomp_mask_b])), axis=0)

    whole = np.concatenate((top_half, bottom_half), axis=1)

    imsave(join(tile_path, 'tile_{}_s{}_t{}.tiff'.format(composite.experiment.name, composite.series.name, str_value(t, composite.series.ts))), whole)

def mod_label(composite, mod_id, algorithm):

  label_path = os.path.join(composite.experiment.video_path, 'labels', composite.series.name)
  if not os.path.exists(label_path):
    os.makedirs(label_path)

  for t in range(composite.series.ts):
    zbf_gon = composite.gons.get(t=t, channel__name='-zbf')
    zbf = zbf_gon.load()

    cell_instances = composite.series.cell_instances.filter(t=t)

    plt.imshow(zbf, cmap='Greys_r')
    for cell_instance in cell_instances:
      plt.scatter(cell_instance.c, cell_instance.r, color='red', s=5)
      plt.text(cell_instance.c+5, cell_instance.r+5, '{}'.format(cell_instance.cell.pk), fontsize=8, color='white')

    plt.text(-50, -50, 'expt={} series={} t={}'.format(composite.experiment.name, composite.series.name, t), fontsize=15, color='black')

    plt.savefig(join(label_path, 'labels_{}_s{}_t{}.png'.format(composite.experiment.name, composite.series.name, str_value(t, composite.series.ts))), dpi=100)
    plt.cla()

def mod_zdiff(composite, mod_id, algorithm):

  zdiff_channel, zdiff_channel_created = composite.channels.get_or_create(name='-zdiff')

  for t in range(composite.series.ts):
    print('step02 | processing mod_zdiff t{}/{}...'.format(t+1, composite.series.ts), end='\r')

    # get zmod
    zmod_gon = composite.gons.get(channel__name='-zmod', t=t)
    zmod = (exposure.rescale_intensity(zmod_gon.load() * 1.0) * composite.series.zs).astype(int)

    zbf = exposure.rescale_intensity(composite.gons.get(channel__name='-zbf', t=t).load() * 1.0)
    zmean = exposure.rescale_intensity(composite.gons.get(channel__name='-zmean', t=t).load() * 1.0)

    # get markers
    markers = composite.markers.filter(track_instance__t=t)

    zdiff = np.zeros(zmod.shape)

    for marker in markers:
      marker_z = zmod[marker.r, marker.c]

      diff = np.abs(zmod - marker_z)
      diff_thresh = diff.copy()
      diff_thresh = gf(diff_thresh, sigma=5)
      diff_thresh[diff>1] = diff.max()
      marker_diff = 1.0 - exposure.rescale_intensity(diff_thresh * 1.0)
      zdiff = np.max(np.dstack([zdiff, marker_diff]), axis=2)

    zdiff_gon, zdiff_gon_created = composite.gons.get_or_create(experiment=composite.experiment, series=composite.series, channel=zdiff_channel, t=t)
    zdiff_gon.set_origin(0,0,0,t)
    zdiff_gon.set_extent(composite.series.rs, composite.series.cs, 1)

    zdiff_gon.array = (zdiff.copy() + zmean.copy()) * zmean.copy()
    zdiff_gon.save_array(composite.series.experiment.composite_path, composite.templates.get(name='source'))
    zdiff_gon.save()

def mod_zedge(composite, mod_id, algorithm):

  zedge_channel, zedge_channel_created = composite.channels.get_or_create(name='-zedge')

  for t in range(composite.series.ts):
    print('step02 | processing mod_zedge t{}/{}...'.format(t+1, composite.series.ts), end='\r')

    zdiff_masks = composite.mask_channels.get(name__contains='-zdiff').cell_masks.filter(t=t)
    zbf = exposure.rescale_intensity(composite.gons.get(channel__name='-zbf', t=t).load() * 1.0)
    zedge = zbf.copy()

    for mask in zdiff_masks:
      # draw edge on zbf image
      # 1. load zdiff mask and cut to black
      mask_mask, (r0, c0, rs, cs) = cut_to_black(dilate(erode(mask.load()))
      # 2. using coordinates, cut zbf image
      cut_zedge = zedge[r0:r0+rs,c0:c0+cs]
      # 3. draw edge
      outside_edge = distance_transform_edt(dilate(binary_edge(outside), iterations=3))
      outside_edge = 1.0 - exposure.rescale_intensity(outside_edge * 1.0)
      cut_zedge *= outside_edge * outside_edge

      zedge[r0:r0+rs,c0:c0+cs] = cut_zedge.copy()

    zedge_gon, zedge_gon_created = composite.gons.get_or_create(experiment=composite.experiment, series=composite.series, channel=zedge_channel, t=t)
    zedge_gon.set_origin(0,0,0,t)
    zedge_gon.set_extent(composite.series.rs, composite.series.cs, 1)

    zedge_gon.array = zedge.zopy()
    zedge_gon.save_array(composite.series.experiment.composite_path, composite.templates.get(name='source'))
    zedge_gon.save()
