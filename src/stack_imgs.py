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
	parser.add_argument(