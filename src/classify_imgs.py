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
	parser.add_argument("-m", "--model-dir", help='<Required> Input directory with' + \
		' the trained model and the tensorboard logs.', required=True)
	parser.add_argument("-o", "--output-dir", help='<Required> The output directory that will ' + \
		' that will have the classification output.', required=True)
	parser.add_argument("-p", "--memory-percentage", help='Reading the input image until' + \
		' memory percentage reach the value defined by this argument. After that, the classification' + \
		' will execute for readed data. [DEFAULT=40.0]', default=40.0, type=float)

	return parser.parse_args()

def exec(images, model_dir, output_dir, memory_percentage = 40):
	tf.logging.set_verbosity(tf.logging.INFO)

	dl_utils.mkdirp(output_dir)

	param_path = dl_utils.new_filepath('train_params.dat', directory=model_dir)
	params = dl_utils.load_object(param_path)

	chips_info_path 