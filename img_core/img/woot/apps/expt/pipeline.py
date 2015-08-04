# apps.expt.pipeline

'''
Text representation of a cell profiler pipeline that can be used to modify data processing.
'''

def marker_pipeline(experiment_prefix, unique_key, primary_channel_name, secondary_channel_name):
  text = 'CellProfiler Pipeline: http://www.cellprofiler.org\n\
Version:3\n\
DateRevision:20140723173957\n\
GitHash:6c2d896\n\
ModuleCount:6\n\
HasImagePlaneDetails:False\n\
\n\
LoadImages:[module_num:1|svn_version:\'Unknown\'|variable_revision_number:11|show_window:True|notes:\x5B\x5D|batch_state:array(\x5B\x5D, dtype=uint8)|enabled:True|wants_pause:False]\n\
    File type to be loaded:individual images\n\
    File selection method:Text-Regular expressions\n\
    Number of images in each group?:3\n\
    Type the text that the excluded images have in common:Do not use\n\
    Analyze all subfolders within the selected folder?:None\n\
    Input image file location:Default Input Folder\x7C\n\
    Check image sets for unmatched or duplicate files?:Yes\n\
    Group images by metadata?:No\n\
    Exclude certain files?:No\n\
    Specify metadata fields to group by:\n\
    Select subfolders to analyze:\n\
    Image count:2\n\
    Text that these images have in common (case-sensitive):{secondary_channel_name}_\n\
    Position of this image in each group:1\n\
    Extract metadata from where?:None\n\
    Regular expression that finds metadata in the file name:\n\
    Type the regular expression that finds metadata in the subfolder path:\n\
    Channel count:1\n\
    Group the movie frames?:No\n\
    Grouping method:Interleaved\n\
    Number of channels per group:3\n\
    Load the input as images or objects?:Images\n\
    Name this loaded image:Secondary\n\
    Name this loaded object:Nuclei\n\
    Retain outlines of loaded objects?:No\n\
    Name the outline image:LoadedImageOutlines\n\
    Channel number:1\n\
    Rescale intensities?:Yes\n\
    Text that these images have in common (case-sensitive):{primary_channel_name}_\n\
    Position of this image in each group:2\n\
    Extract metadata from where?:None\n\
    Regular expression that finds metadata in the file name:\n\
    Type the regular expression that finds metadata in the subfolder path:\n\
    Channel count:1\n\
    Group the movie frames?:No\n\
    Grouping method:Interleaved\n\
    Number of channels per group:3\n\
    Load the input as images or objects?:Images\n\
    Name this loaded image:Primary\n\
    Name this loaded object:Nuclei\n\
    Retain outlines of loaded objects?:No\n\
    Name the outline image:LoadedImageOutlines\n\
    Channel number:1\n\
    Rescale intensities?:Yes\n\
\n\
IdentifyPrimaryObjects:[module_num:2|svn_version:\'Unknown\'|variable_revision_number:10|show_window:True|notes:\x5B\x5D|batch_state:array(\x5B\x5D, dtype=uint8)|enabled:True|wants_pause:False]\n\
    Select the input image:Primary\n\
    Name the primary objects to be identified:Markers\n\
    Typical diameter of objects, in pixel units (Min,Max):3,13\n\
    Discard objects outside the diameter range?:Yes\n\
    Try to merge too small objects with nearby larger objects?:No\n\
    Discard objects touching the border of the image?:Yes\n\
    Method to distinguish clumped objects:Intensity\n\
    Method to draw dividing lines between clumped objects:Intensity\n\
    Size of smoothing filter:10\n\
    Suppress local maxima that are closer than this minimum allowed distance:7.0\n\
    Speed up by using lower-resolution image to find local maxima?:Yes\n\
    Name the outline image:PrimaryOutlines\n\
    Fill holes in identified objects?:After both thresholding and declumping\n\
    Automatically calculate size of smoothing filter for declumping?:Yes\n\
    Automatically calculate minimum allowed distance between local maxima?:Yes\n\
    Retain outlines of the identified objects?:No\n\
    Automatically calculate the threshold using the Otsu method?:Yes\n\
    Enter Laplacian of Gaussian threshold:0.5\n\
    Automatically calculate the size of objects for the Laplacian of Gaussian filter?:Yes\n\
    Enter LoG filter diameter:5.0\n\
    Handling of objects if excessive number of objects identified:Continue\n\
    Maximum number of objects:500\n\
    Threshold setting version:1\n\
    Threshold strategy:Adaptive\n\
    Thresholding method:Otsu\n\
    Select the smoothing method for thresholding:Automatic\n\
    Threshold smoothing scale:1.0\n\
    Threshold correction factor:1.0\n\
    Lower and upper bounds on threshold:0.0,1.0\n\
    Approximate fraction of image covered by objects?:0.01\n\
    Manual threshold:0.0\n\
    Select the measurement to threshold with:None\n\
    Select binary image:None\n\
    Masking objects:None\n\
    Two-class or three-class thresholding?:Two classes\n\
    Minimize the weighted variance or the entropy?:Weighted variance\n\
    Assign pixels in the middle intensity class to the foreground or the background?:Foreground\n\
    Method to calculate adaptive window size:Image size\n\
    Size of adaptive window:10\n\
\n\
IdentifySecondaryObjects:[module_num:3|svn_version:\'Unknown\'|variable_revision_number:9|show_window:True|notes:\x5B\x5D|batch_state:array(\x5B\x5D, dtype=uint8)|enabled:True|wants_pause:False]\n\
    Select the input objects:Markers\n\
    Name the objects to be identified:Cells\n\
    Select the method to identify the secondary objects:Propagation\n\
    Select the input image:Secondary\n\
    Number of pixels by which to expand the primary objects:10\n\
    Regularization factor:0.05\n\
    Name the outline image:SecondaryOutlines\n\
    Retain outlines of the identified secondary objects?:No\n\
    Discard secondary objects touching the border of the image?:No\n\
    Discard the associated primary objects?:No\n\
    Name the new primary objects:FilteredNuclei\n\
    Retain outlines of the new primary objects?:No\n\
    Name the new primary object outlines:FilteredNucleiOutlines\n\
    Fill holes in identified objects?:Yes\n\
    Threshold setting version:1\n\
    Threshold strategy:Automatic\n\
    Thresholding method:Otsu\n\
    Select the smoothing method for thresholding:No smoothing\n\
    Threshold smoothing scale:1.0\n\
    Threshold correction factor:1.8\n\
    Lower and upper bounds on threshold:0.0,1.0\n\
    Approximate fraction of image covered by objects?:0.01\n\
    Manual threshold:0.0\n\
    Select the measurement to threshold with:None\n\
    Select binary image:None\n\
    Masking objects:None\n\
    Two-class or three-class thresholding?:Two classes\n\
    Minimize the weighted variance or the entropy?:Weighted variance\n\
    Assign pixels in the middle intensity class to the foreground or the background?:Foreground\n\
    Method to calculate adaptive window size:Image size\n\
    Size of adaptive window:10\n\
\n\
MeasureObjectSizeShape:[module_num:4|svn_version:\'Unknown\'|variable_revision_number:1|show_window:True|notes:\x5B\x5D|batch_state:array(\x5B\x5D, dtype=uint8)|enabled:True|wants_pause:False]\n\
    Select objects to measure:Cells\n\
    Calculate the Zernike features?:No\n\
\n\
SaveImages:[module_num:5|svn_version:\'Unknown\'|variable_revision_number:11|show_window:True|notes:\x5B\x5D|batch_state:array(\x5B\x5D, dtype=uint8)|enabled:True|wants_pause:False]\n\
    Select the type of image to save:Objects\n\
    Select the image to save:None\n\
    Select the objects to save:Cells\n\
    Select the module display window to save:None\n\
    Select method for constructing file names:From image filename\n\
    Select image name for file prefix:Secondary\n\
    Enter single file name:OrigBlue\n\
    Number of digits:4\n\
    Append a suffix to the image file name?:Yes\n\
    Text to append to the image name:_cp{unique_key}\n\
    Saved file format:tiff\n\
    Output file location:Default Output Folder\x7C\n\
    Image bit depth:8\n\
    Overwrite existing files without warning?:Yes\n\
    When to save:Every cycle\n\
    Rescale the images? :No\n\
    Save as grayscale or color image?:Grayscale\n\
    Select colormap:gray\n\
    Record the file and path information to the saved image?:No\n\
    Create subfolders in the output folder?:No\n\
    Base image folder:Elsewhere...\x7C\n\
    Saved movie format:avi\n\
\n\
ExportToSpreadsheet:[module_num:6|svn_version:\'Unknown\'|variable_revision_number:11|show_window:True|notes:\x5B\x5D|batch_state:array(\x5B\x5D, dtype=uint8)|enabled:True|wants_pause:False]\n\
    Select the column delimiter:Comma (",")\n\
    Add image metadata columns to your object data file?:No\n\
    Limit output to a size that is allowed in Excel?:No\n\
    Select the measurements to export:No\n\
    Calculate the per-image mean values for object measurements?:No\n\
    Calculate the per-image median values for object measurements?:No\n\
    Calculate the per-image standard deviation values for object measurements?:No\n\
    Output file location:Default Output Folder\x7C\n\
    Create a GenePattern GCT file?:No\n\
    Select source of sample row name:Metadata\n\
    Select the image to use as the identifier:None\n\
    Select the metadata to use as the identifier:None\n\
    Export all measurement types?:Yes\n\
    Press button to select measurements to export:\n\
    Representation of Nan/Inf:NaN\n\
    Add a prefix to file names?:Yes\n\
    Filename prefix\x3A{experiment_prefix}\n\
    Overwrite without warning?:Yes\n\
    Data to export:Do not use\n\
    Combine these object measurements with those of the previous object?:No\n\
    File name:DATA.csv\n\
    Use the object name for the file name?:Yes'.format(experiment_prefix=experiment_prefix, unique_key=unique_key, primary_channel_name=primary_channel_name, secondary_channel_name=secondary_channel_name)

  return text

def region_pipeline():
  pass
