
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

	chips_info = load_object(mtd_path)

	nsamples = chips_info['n_chips']
	dat_dtype_size = np.dtype(chips_info['dat_dtype']).itemsize
	exp_dtype_size = np.dtype(chips_info['exp_dtype']).itemsize

	nsamples_test = int(nsamples * test_size)
	nsamples_train = nsamples - nsamples_test
	
	_, dat_xsize, dat_ysize, dat_zsize = chips_info['dat_shape']
	_, exp_xsize, exp_ysize, exp_zsize = chips_info['exp_shape']

	shape_train_data = (nsamples_train, dat_xsize, dat_ysize, dat_zsize)
	shape_train_expect = (nsamples_train, exp_xsize, exp_ysize, exp_zsize)

	shape_test_data = (nsamples_test, dat_xsize, dat_ysize, dat_zsize)
	shape_test_expect = (nsamples_test, exp_xsize, exp_ysize, exp_zsize)

	offset_test_data = dat_dtype_size * nsamples_train * dat_xsize * dat_ysize * dat_zsize
	offset_test_expect = exp_dtype_size * nsamples_train * exp_xsize * exp_ysize * exp_zsize

	train_data = np.memmap(dat_path, dtype=chips_info['dat_dtype'], mode='r', shape=shape_train_data)
	train_expect = np.memmap(exp_path, dtype=chips_info['exp_dtype'], mode='r', shape=shape_train_expect)

	test_data = np.memmap(dat_path, dtype=chips_info['dat_dtype'], mode='r', offset=offset_test_data, shape=shape_test_data)
	test_expect = np.memmap(exp_path, dtype=chips_info['exp_dtype'], mode='r', offset=offset_test_expect, shape=shape_test_expect)
		
	return train_data, test_data, train_expect, test_expect, chips_info

def mkdirp(output_dir):
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

def chips_data_files(output_dir):

	mkdirp(output_dir)

	dat_path = os.path.join(output_dir, 'data.dat')
	exp_path = os.path.join(output_dir, 'expected.dat')
	mtd_path = os.path.join(output_dir, 'metadata.dat')
	
	return 	dat_path, exp_path, mtd_path

def get_train_test_data(img_path, nodata_value, ninput_bands, chip_size, pad_size, seed, \
													offset_list=[(0,0)], rotate=False, flip=False, discard_nodata=True):
	
	npz_path = os.path.splitext(img_path)[0] + '.npz'
	data_path = os.path.splitext(img_path)[0] + '_data.dat'
	expect_path = os.path.splitext(img_path)[0] + '_exp.dat'
	metadata_path = os.path.splitext(img_path)[0] + '_data.json'

	if not os.path.isfile(data_path):
		print("Creating chips from image " + img_path + "...")
	
		chip_data_list, chip_expect_list = chip_generation(img_path, nodata_value, chip_size, pad_size, offset_list, rotate, flip, discard_nodata)

		chips_data = create_memmap_np(data_path, chip_data_list)
		chips_expect = create_memmap_np(expect_path, chip_expect_list)

		chip_generation(img_path, nodata_value, chip_size, pad_size, offset_list, rotate, flip, discard_nodata, chips_data, chips_expect)

		chips_mtl = {
			"nsamples": chips_data.shape[0],
			"data_size": chips_data.shape[1],
			"data_nbands": chips_data.shape[3],
			"expe_size": chips_expect.shape[1],
			"expe_nbands": chips_expect.shape[3]
		}

		np.random.seed(seed)
		rand_idxs = np.random.choice(chips_mtl['nsamples'], chips_mtl['nsamples'])
		print("Shuffling chips...")
		for i1 in range(chips_mtl['nsamples']):
			i2 = rand_idxs[i1]
			chips_data[i2,:,:,:], chips_data[i1,:,:,:] = chips_data[i1,:,:,:], chips_data[i2,:,:,:]
			chips_expect[i2,:,:,:], chips_expect[i1,:,:,:] = chips_expect[i1,:,:,:], chips_expect[i2,:,:,:]

		json.dump(chips_mtl, open(metadata_path, 'w'))
		chips_data.flush()
		chips_expect.flush()

		del chips_data
		del chips_expect

	train_data, test_data, train_expect, test_expect = train_test_split(data_path, expect_path, metadata_path)

	print('Train samples: ', len(train_data))
	print('Test samples: ', len(test_data))

	return train_data, test_data, train_expect, test_expect

def get_predict_data(input_img_ds, input_position, pad_size):
	inp_x0 = input_position[0]
	inp_x1 = input_position[1]
	inp_y0 = input_position[2]
	inp_y1 = input_position[3]

	inp_x0pad = 0
	inp_y0pad = 0
	inp_x1pad = 0
	inp_y1pad = 0
	
	inp_xlen = inp_x1 - inp_x0
	inp_ylen = inp_y1 - inp_y0

	out_x0 = inp_x0 + pad_size
	out_y0 = inp_y0 + pad_size
	
	if (inp_x0 == 0):
		inp_x0pad = pad_size
		out_x0 = 0

	if (inp_y0 == 0):
		inp_y0pad = pad_size
		out_y0 = 0

	if inp_x1 > input_img_ds.RasterXSize:
		inp_x1pad = (inp_x1 - input_img_ds.RasterXSize)

		inp_x1 = input_img_ds.RasterXSize
		inp_xlen = inp_xlen - inp_x1pad

	if inp_y1 > input_img_ds.RasterYSize:
		inp_y1pad = (inp_y1 - input_img_ds.RasterYSize)

		inp_y1 = input_img_ds.RasterYSize
		inp_ylen = inp_ylen - inp_y1pad

	chip_data = input_img_ds.ReadAsArray(inp_x0, inp_y0, inp_xlen, inp_ylen)
	chip_data = np.pad(chip_data, [(0,0), (inp_y0pad, inp_y1pad), (inp_x0pad, inp_x1pad)], mode='reflect')
	chip_data = np.transpose(chip_data, [1,2,0])

	return chip_data, [out_x0, out_y0]

def get_predict_positions(x_size, y_size, chip_size = 100, pad_size = 93, x_offset = 0, y_offset = 0):
