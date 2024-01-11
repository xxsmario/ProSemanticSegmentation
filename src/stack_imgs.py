#!/usr/bin/python3

import os
import ntpath
import gdal
import argparse
import dl_utils

import subprocess

def parse_args():
	parser = argparse.ArgumentPar