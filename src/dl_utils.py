
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