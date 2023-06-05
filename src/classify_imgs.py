#!/usr/bin/python3
import argparse

from dl_models import unet as md
import tensorflow as tf
import numpy as np

from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

import time
import gc
import gdal
import dl_utils

def parse_args():
	parser = argparse.ArgumentParser(description='STEP 06/06 - Classify a list of images' + \
		' using a trained model.')
	parser.add_argument("-i", "--images", nargs='+', help='<Required> List of input images' + \
		' that will be classified.', required=True)
	parser.add_argu