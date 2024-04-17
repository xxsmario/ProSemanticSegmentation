
#!/usr/bin/python3

import argparse

from dl_models import unet as md
import tensorflow as tf

import dl_utils

def parse_args():
	parser = argparse.ArgumentParser(description='STEP 04/06 - U-Net Training approach' + \
		' using several chips.')
	parser.add_argument("-i", "--chips-dir", help='<Required> Input directory of chips' + \
		' that will be used by training process.', required=True)
	
	parser.add_argument("-s", "--seed", help='Seed that will be used to split the chips in train ' + \
		' and evaluation groups. [DEFAULT=1989]', type=int, default=1989)
	parser.add_argument("-t", "--eval-size", help='Percentage size of the evaluation group.' + \
		' [DEFAULT=0.2]', type=float, default=0.2)
	parser.add_argument("-f", "--scale-factor", help='Scale factor that will multiply the input chips ' + \
		' before training process. If the data type of input chips is integer you should considerer ' + \
		' use this argument. [DEFAULT=1.0]', type=float, default=1.0)

	parser.add_argument("-e", "--epochs", help='Number of epochs of the training process. [DEFAULT=100]', type=int, default=100)
	parser.add_argument("-b", "--batch-size", help='Batch size of training process. ' + \
		' In case of memory error you should decrease this argument. [DEFAULT=32]', type=int, default=32)
	parser.add_argument("-l", "--learning-rate", help='Learning rate of training process. [DEFAULT=0.00005]', \