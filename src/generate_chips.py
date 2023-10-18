#!/usr/bin/python3

import os
import gdal
import argparse
import dl_utils
import pickle
import time
import numpy as np

def parse_args():
	parser = argparse.ArgumentParser(description='STEP 03/06 - ' + \
		' Generate a several chips (i.e. a set of pixels with regular squared size) ' + \
		' considerering the input image. The last band will be used' + \
		' as expected output result, and should have only these pixel values:' + \
		' 0=without information, 1=object of interest, 2=not an object of interest.' + \
		' If a chip has only pixel values equal to 0, into reference band, the chip will discarded.')
	parser.add_argument("-i", "--image", help='<Required> Input image' + \
		' that will be used by chip generation process.', required=True)
	parser.add_argument("-o", "--output-dir", help='<Required> The output directory that' + \
		' will have the generated chips.', required=True)
	parser.add_argument("-n", "--nodata", help='Nodata value of input image. [DEFAULT=-50]', type=int, default=-50)
	parser.add_argument("-s", "--chip-size", help='Size of the chip with output result.' + \
		' A chip always will be a square. [DEFAULT=100]', type=int, default=100)
	parser.add_argument("-p", "--pad-size", help='Padding size that will establish the size of input chip, with spectral data.' + \
		 ' A padding size of 93px and a chip size of 100px will result in a input chip of 286px. [DEFAULT=93]', type=int, default=93)
	parser.add_argument("-f", "--offset", help='As a data augmentation option, ' + \
		' offset argument will be used to produce chips with a percentage of overlap.' + \
		' An offset 0,50 will generate chips with 50 percent of overlap in the axis y. [DEFAULT=0,0]', nargs='+', default=['0,0'])
