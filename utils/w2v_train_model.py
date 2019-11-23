#!/usr/bin/env python3

import os
import tqdm
import gensim
import logging  # Setting up the loggings to monitor gensim
import argparse
from w2v_utils import Dataset

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Train a word2vec model')
	parser.add_argument('--corpus_word2vec',
						type=argparse.FileType('r'),
						required=True,
						help='large raw corpus file')
	parser.add_argument('--word2vec_model', help='a pretrained word2vec model')

	args = parser.parse_args()
	corpus_file_word2vec = args.corpus_word2vec
	word2vec_model = args.word2vec_model

	logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)

	word2vec = gensim.models.word2vec.Word2Vec(min_count=20,
		window=2,
		size=300,
		sample=6e-5,
		alpha=0.03,
		seed=42,
		min_alpha=0.0007,
		negative=20,
		workers=1)

	word2vec.build_vocab(Dataset(corpus_file_word2vec), progress_per=500000)
	word2vec.train(Dataset(corpus_file_word2vec), total_examples=word2vec.corpus_count, epochs=50, report_delay=10)
	word2vec.save(word2vec_model)
