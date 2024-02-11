#!/usr/bin/python3

import os
import ntpath
import gdal
import argparse
import dl_utils

import subprocess

def parse_args():
	parser = argparse.ArgumentParser(description='STEP 02/06 - ' + \
		'Stack multiple images into a sigle Virtual Dataset-VRT image. If informed,' + \
		' the reference image will the last band.')
	parser.add_argument("-i", "--images", nargs='+', help='<Required> List of input images.', required=True)
	parser.add_argument("-b", "--bands", nargs='+', type=int, help='The bands that should be stacked. [DEFAULT=All]', default=None)
	parser.add_argument("-r", "--reference", help=' Image with reference data, that should have only these pixel values:' + \
		' 0=without information, 1=object of interest, 2=not an object of interest.')
	parser.add_argument("-o", "--output", help='<Required> The name of VRT output image', required=True)
	return parser.parse_args()

def reference_params(img_path):
	image_ds = gdal.Open(img_path, gdal.GA_ReadOnly)
	
	xmin, pixel_width, _, ymax, _, pixel_height = image_ds.GetGeoTransform()
	xmax = xmin + pixel_width * image_ds.RasterXSize
	ymin = ymax + pixel_height * image_ds.RasterYSize
	
	return [str(xmin), str(ymin), str(xmax), str(ymax)], [str(pixel_width), str(pixel_width)]

def create_vrt_bands(img_path, output_vrt, bands):
	
	image_ds = gdal.Open(img_path, gdal.GA_ReadOnly)

	vrt_bands = []
	if bands is None:
		bands = range(1, (image_ds.RasterCount+1) )

	for band in bands:
		vrt_filepath = dl_utils.new_filepath(img_path, suffix = str(band), ext='vrt', 
			directory=dl_utils.basedir(output_vr