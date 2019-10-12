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
	# parser.add_argument('-corpus_bpe', required=True,
	# 					help='an untagged corpus')
	parser.add_argument('-no_of_merges', required=True,
	 					help='an untagged corpus')
	parser.add_argument('-corpus', required=True,
						help='an untagged corpus')
	parser.add_argument('-o', '--output_directory', required=True,
						help='output directory for weighted dictionaries')
	args = parser.parse_args()
	no_of_merges = args.no_of_merges
	input_directory = args.input_directory
	output_directory = args.output_directory
	apertium_bin = args.apertium_bin
	corpus = args.corpus
	# corpus_bpe = args.corpus_bpe
	if not os.path.exists(output_directory):
		os.mkdir(output_directory)

	temp_dir = tempfile.mkdtemp()

	temp_weightlist = Path(temp_dir, 'temp_weightlist')
	default_weightlist = Path(temp_dir, 'temp_default_weightlist')

	temp_input_file = Path(temp_dir, 'temp_input')
	for input_file in sorted(os.listdir(input_directory)):
		temp_input_files = [Path(input_directory, input_file)
			for file in sorted(os.listdir(input_directory)) if file!=input_file]

		with open(temp_input_file, 'w') as f:
			for file in temp_input_files:
				with open(file, 'r') as fold_file:
					# EXTRACT SURFACE FORM ONLY
					lines = ['\n'.join(line.split()) for line in fold_file.readlines()]
					f.write('\n'.join(lines))

		subprocess.run(['./bpe-weightlist',
			temp_input_file, apertium_bin, no_of_merges, temp_weightlist, default_weightlist])

		# Generate a bin file
		subprocess.run(['./lt-weight',
						apertium_bin,
						Path(output_directory, '{}.bin'.format(input_file)),
						temp_weightlist,
						default_weightlist])
