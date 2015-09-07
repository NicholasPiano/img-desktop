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
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# methods
def scan_point(img, rs, cs, r, c, size=0):
  r0 = r - size if r - size >= 0 else 0
  r1 = r + size + 1 if r + size + 1 <= rs else rs
  c0 = c - size if c - size >= 0 else 0
  c1 = c + size + 1 if c + size + 1 <= cs else cs

  column = img[r0:r1,c0:c1,:]
  column_1D = np.sum(np.sum(column, axis=0), axis=0)

  return column_1D

def mask_edge_image(mask_img):
  full_edge_img = np.zeros(mask_img.shape)
  for unique in [u for u in np.unique(mask_img) if u>0]:
    full_edge_img += edge_image(mask_img==unique)

  return full_edge_img>0

# algorithms
def mod_zmod(composite, mod_id, algorithm, **kwargs):
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


    max_gfp_z = np.argmax(np.sum(np.sum(gfp, axis=0), axis=0))

    Zbf = bf[:,:,max_gfp_z].copy()

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

def mod_tile(composite, mod_id, algorithm, **kwargs):

  tile_path = os.path.join(composite.experiment.video_path, 'tile', composite.series.name)
  if not os.path.exists(tile_path):
    os.makedirs(tile_path)

  for t in range(composite.series.ts):
    zbf_gon = composite.gons.get(t=t, channel__name='-zbf')
    zcomp_gon = composite.gons.get(t=t, channel__name='-zcomp')
    zmean_gon = composite.gons.get(t=t, channel__name='-zmean')
    mask_mask = composite.masks.get(t=t, channel__name__contains=kwargs['channel_unique_override'])

    zbf = zbf_gon.load()
    zcomp = zcomp_gon.load()
    zmean = zmean_gon.load()
    mask = mask_mask.load()

    mask_outline = mask_edge_image(mask)

    zbf_mask_r = zbf.copy()
    zbf_mask_g = zbf.copy()
    zbf_mask_b = zbf.copy()

    zcomp_mask_r = zcomp.copy()
    zcomp_mask_g = zcomp.copy()
    zcomp_mask_b = zcomp.copy()

    # drawing
    # 1. draw outlines in red channel
    zbf_mask_r[mask_outline>0] = 255
    zbf_mask_g[mask_outline>0] = 0
    zbf_mask_b[mask_outline>0] = 0
    zcomp_mask_r[mask_outline>0] = 255
    zcomp_mask_g[mask_outline>0] = 0
    zcomp_mask_b[mask_outline>0] = 0

    markers = composite.markers.filter(track_instance__t=t, track__cell__isnull=False)
    for marker in markers:

      # 2. draw markers in blue channel
      zbf_mask_r[marker.r-2:marker.r+3,marker.c-2:marker.c+3] = 0
      zbf_mask_g[marker.r-2:marker.r+3,marker.c-2:marker.c+3] = 0
      zbf_mask_b[marker.r-2:marker.r+3,marker.c-2:marker.c+3] = 255
      zcomp_mask_r[marker.r-2:marker.r+3,marker.c-2:marker.c+3] = 0
      zcomp_mask_g[marker.r-2:marker.r+3,marker.c-2:marker.c+3] = 0
      zcomp_mask_b[marker.r-2:marker.r+3,marker.c-2:marker.c+3] = 255

      # 3. draw text in green channel
      blank_slate = np.zeros(zbf.shape)
      blank_slate_img = Image.fromarray(blank_slate)
      draw = ImageDraw.Draw(blank_slate_img)
      draw.text((marker.c+5, marker.r+5), '{}'.format(marker.track.cell.pk), font=ImageFont.load_default(), fill='rgb(0,0,255)')
      blank_slate = np.array(blank_slate_img)

      zbf_mask_r[blank_slate>0] = 0
      zbf_mask_g[blank_slate>0] = 255
      zbf_mask_b[blank_slate>0] = 0
      zcomp_mask_r[blank_slate>0] = 0
      zcomp_mask_g[blank_slate>0] = 255
      zcomp_mask_b[blank_slate>0] = 0

    # regions
    region_mask = composite.masks.get(t=t, channel__name__contains=composite.current_region_unique).load()
    region_mask_edges = mask_edge_image(region_mask)

    zbf_mask_r[region_mask_edges>0] = 100
    zbf_mask_g[region_mask_edges>0] = 100
    zbf_mask_b[region_mask_edges>0] = 100

    zcomp_mask_r[region_mask_edges>0] = 100
    zcomp_mask_g[region_mask_edges>0] = 100
    zcomp_mask_b[region_mask_edges>0] = 100

    # region labels
    # prepare drawing
    blank_slate = np.zeros(zbf.shape)
    blank_slate_img = Image.fromarray(blank_slate)
    draw = ImageDraw.Draw(blank_slate_img)
    for unique in [u for u in np.unique(region_mask) if u>0]:
      if composite.series.region_instances.filter(region_track_instance__t=t, mode_gray_value_id=unique).count()>0:
        region = composite.series.region_instances.get(region_track_instance__t=t, mode_gray_value_id=unique).region

        # get coords (isolate mask, cut to black, use r/c)
        isolated_mask = region_mask==unique
        cut, (r0,c0,rs,cs) = cut_to_black(isolated_mask)

        draw.text((c0+30, r0+30), '{}'.format(region.name), font=ImageFont.load_default(), fill='rgb(0,0,255)')

    blank_slate = np.array(blank_slate_img)

    zbf_mask_r[blank_slate>0] = 0
    zbf_mask_g[blank_slate>0] = 0
    zbf_mask_b[blank_slate>0] = 255

    zcomp_mask_r[blank_slate>0] = 0
    zcomp_mask_g[blank_slate>0] = 0
    zcomp_mask_b[blank_slate>0] = 255

    # tile zbf, zbf_mask, zcomp, zcomp_mask
    top_half = np.concatenate((np.dstack([zbf, zbf, zbf]), np.dstack([zbf_mask_r, zbf_mask_g, zbf_mask_b])), axis=0)
    bottom_half = np.concatenate((np.dstack([zmean, zmean, zmean]), np.dstack([zcomp_mask_r, zcomp_mask_g, zcomp_mask_b])), axis=0)

    whole = np.concatenate((top_half, bottom_half), axis=1)

    imsave(join(tile_path, 'tile_{}_s{}_t{}.tiff'.format(composite.experiment.name, composite.series.name, str_value(t, composite.series.ts))), whole)

def mod_region_test(composite, mod_id, algorithm, **kwargs):

  region_test_path = os.path.join(composite.experiment.video_path, 'regions', composite.series.name)
  if not os.path.exists(region_test_path):
    os.makedirs(region_test_path)

  for t in range(composite.series.ts):
    zbf = composite.gons.get(t=t, channel__name='-zbf').load()
    region_mask = composite.masks.get(t=t, channel__name__contains=kwargs['channel_unique_override']).load()

    mask_edges = mask_edge_image(region_mask)

    zbf_mask_r = zbf.copy()
    zbf_mask_g = zbf.copy()
    zbf_mask_b = zbf.copy()

    # edges
    zbf_mask_r[mask_edges>0] = 100
    zbf_mask_g[mask_edges>0] = 100
    zbf_mask_b[mask_edges>0] = 100

    # region labels
    # prepare drawing
    blank_slate = np.zeros(zbf.shape)
    blank_slate_img = Image.fromarray(blank_slate)
    draw = ImageDraw.Draw(blank_slate_img)
    for unique in [u for u in np.unique(region_mask) if u>0]:
      if composite.series.region_instances.filter(region_track_instance__t=t, mode_gray_value_id=unique).count()>0:
        region = composite.series.region_instances.get(region_track_instance__t=t, mode_gray_value_id=unique).region

        # get coords (isolate mask, cut to black, use r/c)
        isolated_mask = region_mask==unique
        cut, (r0,c0,rs,cs) = cut_to_black(isolated_mask)

        draw.text((c0+30, r0+30), '{}'.format(region.name), font=ImageFont.load_default(), fill='rgb(0,0,255)')

    blank_slate = np.array(blank_slate_img)
    zbf_mask_r[blank_slate>0] = 0
    zbf_mask_g[blank_slate>0] = 0
    zbf_mask_b[blank_slate>0] = 255

    whole = np.dstack([zbf_mask_r, zbf_mask_g, zbf_mask_b])

    imsave(join(region_test_path, 'regions_{}_s{}_t{}.tiff'.format(composite.experiment.name, composite.series.name, str_value(t, composite.series.ts))), whole)

def mod_zdiff(composite, mod_id, algorithm, **kwargs):

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

def mod_zedge(composite, mod_id, algorithm, **kwargs):

  zedge_channel, zedge_channel_created = composite.channels.get_or_create(name='-zedge')

  for t in range(composite.series.ts):
    print('step02 | processing mod_zedge t{}/{}...'.format(t+1, composite.series.ts), end='\r')

    zdiff_mask = composite.masks.get(channel__name__contains=kwargs['channel_unique_override'], t=t).load()
    zbf = exposure.rescale_intensity(composite.gons.get(channel__name='-zbf', t=t).load() * 1.0)
    zedge = zbf.copy()

    binary_mask = zdiff_mask>0
    outside_edge = distance_transform_edt(dilate(edge_image(binary_mask), iterations=4))
    outside_edge = 1.0 - exposure.rescale_intensity(outside_edge * 1.0)
    zedge *= outside_edge * outside_edge

    zedge_gon, zedge_gon_created = composite.gons.get_or_create(experiment=composite.experiment, series=composite.series, channel=zedge_channel, t=t)
    zedge_gon.set_origin(0,0,0,t)
    zedge_gon.set_extent(composite.series.rs, composite.series.cs, 1)

    zedge_gon.array = zedge.copy()
    zedge_gon.save_array(composite.series.experiment.composite_path, composite.templates.get(name='source'))
    zedge_gon.save()
