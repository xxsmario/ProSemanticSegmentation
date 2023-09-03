
import os
import gdal
import osr
import numpy as np
import psutil
import gc
import pickle
import ntpath

import math

def load_object(filepath):
	with open(filepath, 'rb') as file:
		return pickle.load(file)

def save_object(filepath, obj):
	with open(filepath, 'wb') as file:
		pickle.dump(obj, file, protocol=pickle.HIGHEST_PROTOCOL)

def basedir(filepath):
	return os.path.dirname(filepath)

def new_filepath(filepath, suffix=None, ext=None, directory='.'):
	
	filename = ntpath.basename(filepath)

	filename_splited = filename.split(os.extsep)
	filename_noext = filename_splited[0]
	
	if (ext is None):
		ext = filename_splited[1]
	
	if (suffix is None):
		suffix = ''
	else:
		suffix = '_' + suffix

	filename = filename_noext + suffix + '.' + ext

	return os.path.join(directory, filename)

def pad_index(index, dim_size, chip_size, pad_size):

	i0 = (index - pad_size)
	i1 = (index + chip_size + pad_size)

	if (i0 < 0):
		i0 = 0
		i1 = i0 + chip_size + pad_size

	return i0, i1

def split_data(data, pad_size):
	xsize, ysize, nbands = data.shape

	last_band = (nbands-1)
	
	x0 = pad_size
	x1 = xsize-pad_size

	y0 = pad_size
	y1 = ysize-pad_size

	chip_expect = data[x0:x1, y0:y1, last_band:nbands]
	chip_data = data[:, :, 0:last_band]

	return chip_data, chip_expect

def chip_augmentation(data, rotate = True, flip = True):
	result = [ data ]

	if rotate:
		result = result + [ np.rot90(data, k=k, axes=(0,1)) for k in [1,2,3] ]

	if flip:
		#result = result + [np.flip(result, axis=k) for k in [0,1] ]
		result = result + [np.fliplr(r_data) for r_data in result] 

	return result

def chips_info(img_path, nodata_value, chip_size, pad_size, offset_list=[(0,0)], \
							rotate=False, flip=False, discard_nodata=True):

	total_nchips = 0
	input_img_ds = gdal.Open(img_path)

	for x_offset_percent, y_offset_percent in offset_list:
		x_offset = int(chip_size * (x_offset_percent / 100.0))
		y_offset = int(chip_size * (y_offset_percent / 100.0))

		input_positions = get_predict_positions(input_img_ds.RasterXSize, input_img_ds.RasterYSize, \
																						chip_size, pad_size, x_offset, y_offset)
		
		for input_position in input_positions:
			chip_data, _ = get_predict_data(input_img_ds, input_position, pad_size)
