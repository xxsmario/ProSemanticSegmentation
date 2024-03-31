
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