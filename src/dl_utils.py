
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

			chip_data, chip_expect = split_data(chip_data, pad_size)
			xsize, ysize, _ = chip_expect.shape

			if (chip_size == xsize and chip_size == ysize) and (not discard_nodata or float(np.max(chip_expect)) != float(nodata_value)):
				total_nchips += 1
	
	if rotate:
		total_nchips *= 4
	if flip:
		total_nchips *= 2
		
	sample_input_position = input_positions[0]
	chip_data, _ = get_predict_data(input_img_ds, sample_input_position, pad_size)

	chip_data, chip_expect = split_data(chip_data, pad_size)

	dat_width, dat_height, dat_nbands = chip_data.shape
	exp_width, exp_height, exp_nbands = chip_expect.shape

	return {
		'dat_shape': (total_nchips, dat_width, dat_height, dat_nbands),
		'exp_shape': (total_nchips, exp_width, exp_height, exp_nbands),
		'dat_dtype': chip_data.dtype,
		'exp_dtype': chip_expect.dtype,
		'n_chips': total_nchips
	}

def generate_chips(img_path, dat_ndarray, exp_ndarray, nodata_value, chip_size, pad_size, \
							offset_list=[(0,0)], rotate=False, flip=False, discard_nodata=True, simulate=False):
	
	index = 0
	input_img_ds = gdal.Open(img_path)

	for x_offset_percent, y_offset_percent in offset_list:
		x_offset = int(chip_size * (x_offset_percent / 100.0))
		y_offset = int(chip_size * (y_offset_percent / 100.0))

		input_positions = get_predict_positions(input_img_ds.RasterXSize, input_img_ds.RasterYSize, \
																						chip_size, pad_size, x_offset, y_offset)

		for input_position in input_positions:
			chip_data, _ = get_predict_data(input_img_ds, input_position, pad_size)

			chip_data, chip_expect = split_data(chip_data, pad_size)
			xsize, ysize, _ = chip_expect.shape
			
			if (chip_size == xsize and chip_size == ysize) and (not discard_nodata or float(np.max(chip_expect)) != float(nodata_value)):
				chip_expect[ chip_expect != 1] = 0 # convert all other class to pixel == 0
				chip_data_aux = chip_augmentation(chip_data, rotate, flip)
				chip_expect_aux = chip_augmentation(chip_expect, rotate, flip)
				nchips = len(chip_data_aux)

				dat_ndarray[index:index+nchips,:,:,:] = np.stack(chip_data_aux)
				exp_ndarray[index:index+nchips,:,:,:] = np.stack(chip_expect_aux)

				index = index + nchips

def train_test_split(dat_path, exp_path, mtd_path, test_size=0.2):
