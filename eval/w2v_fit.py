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
	parser.add_argument('-corpus', required=True,
						help='an untagged corpus for generating a weightlist')
	parser.add_argument('-corpus_word2vec', required=True,
						help='an large untagged corpus for training the word2vec model')
	parser.add_argument('-o', '--output_directory', required=True,
						help='output directory for weighted dictionaries')
	parser.add_argument('--word2vec_model', help='a pretrained word2vec model')

	args = parser.parse_args()
	input_directory = args.input_directory
	output_directory = args.output_directory
	apertium_bin = args.apertium_bin
	corpus = args.corpus
	corpus_word2vec = args.corpus_word2vec
	word2vec_model = args.word2vec_model
	if not os.path.exists(output_directory):
		os.mkdir(output_directory)

	temp_dir = tempfile.mkdtemp()

	temp_weightlist = Path(temp_dir, 'temp_weightlist')
	default_weightlist = Path(temp_dir, 'temp_default_weightlist')

	# Train a word2vec model and generate the weightlist using the corpus file
	subprocess.run(['./w2v-weightlist',
		corpus, corpus_word2vec, apertium_bin, word2vec_model, temp_weightlist, default_weightlist])

	for input_file in sorted(os.listdir(input_directory)):
		# Generate a bin file
		subprocess.run(['./lt-weight',
						apertium_bin,
						Path(output_directory, '{}.bin'.format(input_file)),
						temp_weightlist,
						default_weightlist])
