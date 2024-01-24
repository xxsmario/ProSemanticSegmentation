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
	image_ds = gdal.Open(img_