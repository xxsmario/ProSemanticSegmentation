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
		' If a chip has only pixel value