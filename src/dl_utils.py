
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