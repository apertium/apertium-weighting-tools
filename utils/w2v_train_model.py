#!/usr/bin/env python3

import os
import tqdm
import gensim
import logging  # Setting up the loggings to monitor gensim
import argparse
from w2v_utils import Dataset, WikiDataset

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Train a word2vec model')
	parser.add_argument('--corpus_word2vec',
						required=True,
						help='large raw corpus file')
	parser.add_argument('--word2vec_model', help='a pretrained word2vec model')
	parser.add_argument('-window', type=int, default=2)
	parser.add_argument('-size', type=int, default=100)
	parser.add_argument('-s', '--seed', type=int, default=42, help='seed value')
	parser.add_argument('--epochs', type=int, default=5)
	parser.add_argument('--is_wiki_dump', action='store_true', help='use a wiki dump to train the model')

	args = parser.parse_args()
	corpus_file_word2vec = args.corpus_word2vec
	word2vec_model = args.word2vec_model
	window = args.window
	size = args.size
	seed = args.seed
	epochs = args.epochs
	is_wiki_dump = args.is_wiki_dump

	logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)

	word2vec = gensim.models.word2vec.Word2Vec(min_count=5,
		window=window,
		size=size,
		seed=seed,
		sg=1,
		sample=1e-5,
		alpha=0.025,
		min_alpha=0.0001,
		negative=20,
		workers=1)
	if is_wiki_dump:
		dataset = WikiDataset(corpus_file_word2vec)
	else:
		#TODO: test this feature
		with open(corpus_file_word2vec, 'r') as f:
			dataset = Dataset(f)
	word2vec.build_vocab(dataset, progress_per=500000)
	word2vec.train(dataset, total_examples=word2vec.corpus_count, epochs=epochs, report_delay=10)
	word2vec.save(word2vec_model)
