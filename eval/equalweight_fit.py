#!/usr/bin/env python3

import os
import sys
import argparse
import tempfile
import subprocess
from pathlib import Path

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='fit n models using n folds')
	parser.add_argument('-i', '--input_directory', required=True,
						help='input directory of the n folds')
	parser.add_argument('-b', '--apertium_bin', required=True,
						help='a compiled dictionary')
	parser.add_argument('-o', '--output_directory', required=True,
						help='output directory for weighted dictionaries')
	args = parser.parse_args()
	input_directory = args.input_directory
	output_directory = args.output_directory
	apertium_bin = args.apertium_bin
	if not os.path.exists(output_directory):
		os.mkdir(output_directory)

	temp_dir = tempfile.mkdtemp()

	temp_weightlist = Path(temp_dir, 'temp_weightlist')
	subprocess.run(['./equal-weightlist', temp_weightlist])
	
	# Generate a single bin and just copy it since
	# the weighted bin doesn't depend on the training data
	temp_weighted_bin = Path(temp_dir, 'temp_weighted_bin')
	
	subprocess.run(['./lt-weight',
					apertium_bin,
					temp_weighted_bin,
					temp_weightlist])

	for input_file in sorted(os.listdir(input_directory)):
		# Just copy the weighted binary
		subprocess.run(['cp',
						temp_weighted_bin,
						Path(output_directory, '{}.bin'.format(input_file))])
