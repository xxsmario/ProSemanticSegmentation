
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
		type=float, default=0.00005)
	parser.add_argument("-d", "--dropout-rate", help='Dropout rate of model.' + \
		' Small values here may help prevent overfitting. [DEFAULT=0.5]', type=float, default=0.5)
	parser.add_argument("-r", "--l2-regularizer", help='Dropout rate of model.' + \
		' Small values here may help prevent overfitting. [DEFAULT=0.5]', type=float, default=0.5)
	
	parser.add_argument("-o", "--output-dir", help='<Required> The output directory that' + \
		' will have the trained model and the tensorboard logs.', required=True)
	parser.add_argument("-m", "--tensorboard-maxoutput", help='The number of chips that' + \
		' will presented by tensorboard during the training process. [DEFAULT=2]', default=2)
	
	return parser.parse_args()

if __name__ == "__main__":
	args = parse_args()

	chips_dir = args.chips_dir
	output_dir = args.output_dir
	eval_size = args.eval_size
	batch_size = args.batch_size
	epochs = args.epochs
	seed = args.seed
	params = vars(args)

	tf.set_random_seed(seed)
	tf.logging.set_verbosity(tf.logging.INFO)

	dat_path, exp_path, mtd_path = dl_utils.chips_data_files(chips_dir)
	train_data, test_data, train_expect, test_expect, chips_info = dl_utils.train_test_split(dat_path, exp_path, mtd_path, eval_size)
