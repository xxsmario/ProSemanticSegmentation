
#!/usr/bin/python3

import argparse

from dl_models import unet as md
import tensorflow as tf
import numpy as np

from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

import time
import gc
import gdal
import dl_utils

def do_evaluation(estimator, input_data, input_expected, category, params):
	predict_input_fn = tf.estimator.inputs.numpy_input_fn(x={"data": input_data}, batch_size=params['batch_size'], shuffle=False)
	predict_results = estimator.predict(input_fn=predict_input_fn)

	pred_flat_list = []
	ref_flat_list = []

	for predict, expect in zip(predict_results, input_expected):
		
		predict_out = dl_utils.discretize_values(predict, 1, 0)

		pre_flat = predict_out.reshape(-1)
		exp_flat = expect.reshape(-1)

		pred_flat_list.append(pre_flat)
		ref_flat_list.append(exp_flat)

		print("Evaluating process " + str( len(ref_flat_list)/len(input_expected) * 100 ) + "%")

	pred_flat_arr = np.concatenate(pred_flat_list)
	ref_flat_arr = np.concatenate(ref_flat_list)

	print(pred_flat_arr.shape)

	accuracy = accuracy_score(ref_flat_arr, pred_flat_arr)
	print(category + ' accurancy:', accuracy)
	print('\n--------------------------------------------------')