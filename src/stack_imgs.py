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
		' the reference