
#!/usr/bin/python3

import math
import gdal
import numpy as np
import multiprocessing
import os
import csv
import time
import osr
from pathlib import Path
import dl_utils

import argparse

def parse_args():
	parser = argparse.ArgumentParser(description='STEP 01/06 - ' + \
		'Standardize multiple images using the formula: (value - median) / std_dev.' + \
		' The median and std_dev will be calculate by band (e.g. blue, red) considering all images.')
	parser.add_argument("-i", "--images", nargs='+', help='<Required> List of input images.', \
		required=True)
	parser.add_argument("-b", "--bands", nargs='+', type=int, help='<Required> The image bands' + \
		' that will be standardized.', required=True)
	parser.add_argument("-n", "--in-nodata", help='<Required> Nodata value of input images.' \
		, type=float, required=True)
	parser.add_argument("-d", "--out-nodata", help='Nodata value of standardized images.' + \
		' It will be ignored when convert-int16 is enabled. [DEFAULT=-50]', type=float, default=-50)
	parser.add_argument("-t", "--convert-int16", help='Convert the standardized images to ' + \
		' int16, multiply its pixel values by scale factor 10000. It will reduce the size of' + \
		' the output files and use -32767 as nodata value. [DEFAULT=false]', action='store_true')
	parser.add_argument("-o", "--output-dir", help='<Required> Output directory that' + \
		' will have the standardized images.', required=True)
	parser.add_argument("-c", "--chunk-size", help='The amount of data that will be processed,' + \
		' per time, by standardization process. In case of memory error you should decrease this ' + \
		' argument. [DEFAULT=1000]', type=int, default=1000)
	return parser.parse_args()

def merge_unique_values(result, uniq_vals, count_vals):
	for i in range(0, len(uniq_vals)):
		uniq_val = uniq_vals[i]
		if uniq_val not in result:
			result[uniq_val] = 0
		result[uniq_val] = result[uniq_val] + count_vals[i]

def unique_values(chunk):

	result = {}
	
	image_ds = gdal.Open(chunk['image_file'], gdal.GA_ReadOnly)

	band_ds = image_ds.GetRasterBand(chunk['band'])
	band_data = band_ds.ReadAsArray(chunk['xoff'], chunk['yoff'], chunk['win_xsize'], chunk['win_ysize']);

	validPixels = (band_data != chunk['nodata'])

	uniq_vals, count_vals = np.unique(band_data[validPixels], return_counts=True)
	merge_unique_values(result, uniq_vals, count_vals)
	
	print('Processing ' + chunk['id'])

	return result
		
def prepare_chunks(image_file, band, chunk_x_size, in_nodata):
	image_ds = gdal.Open(image_file, gdal.GA_ReadOnly)
	
	x_size = image_ds.RasterXSize
	y_Size = image_ds.RasterYSize

	indexes = []

	for xoff in range(0,x_size,chunk_x_size):
		if (xoff+chunk_x_size) > x_size:
			chunk_x_size = x_size - xoff

		suffix = 'b'+str(band) +'_' +'x'+str(xoff)
		chunk_id = dl_utils.new_filepath(image_file, suffix = suffix, ext='', directory='')
		indexes.append({
			'id':chunk_id, 
			'image_file':image_file, 
			'band':band, 
			'xoff': xoff, 
			'yoff': 0, 
			'win_xsize': chunk_x_size, 
			'win_ysize': y_Size,
			'nodata': in_nodata
		})

	return indexes

def export_csv(csv_path, orig_image_name, freq_data):
	with open(csv_path, 'a') as csv_file: 
		for uniq_val in freq_data.keys():
			csv_file.write(str(uniq_val) + ';' + str(freq_data[uniq_val]) + ';' + str(orig_image_name) + '\n')

def calc_stats(freq_data, in_nodata):
	
	values = np.array(list(freq_data.keys()))
	frequencies = np.array(list(freq_data.values()))
	
	total = np.sum(frequencies)
	
	max = np.max(values)
	min = np.min(values)
	mean = np.sum(values * frequencies) / total
	
	val_distance = (values - mean)
	val_distance_weighted = val_distance * val_distance * frequencies
	variance = np.sum(val_distance_weighted) / total
	std = np.sqrt(variance)

	median_pos = math.ceil((total + 1) / 2)