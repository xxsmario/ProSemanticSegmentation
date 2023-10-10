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
	parser.add_argument("-p", "--pad-size", he