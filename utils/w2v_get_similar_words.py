#!/usr/bin/env python3

import os
import sys
import tqdm
import gensim
import string
import argparse
from w2v_utils import Dataset

def get_naive_similar(word, word2vec):
	if not word in word2vec.wv.vocab:
		return []
	return [t[0] for t in word2vec.most_similar(word)]

def get_similar_tokens(context, word2vec):
	""" Find the most probable words given bag of context words

	context: A list of context words
	word2vec: A fitted word2vec model
	"""
	similar_words = word2vec.predict_output_word(context)
	if not similar_words:
		return []

	return  [w for w, _ in similar_words]

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Generate the set of words and similar words using a raw corpus file')
	parser.add_argument('--corpus',
						type=argparse.FileType('r'),
						required=True,
						help='large raw corpus file')
	parser.add_argument('--output_words_file',
						type=argparse.FileType('w'),
						required=True,
						help='The words of the corpus, one word per line')
	parser.add_argument('--output_similar_words_file',
						type=argparse.FileType('w'),
						required=True,
						help='The set of similar words for the words of the corpus, tab-delimited')
	parser.add_argument('--word2vec_model', help='a pretrained word2vec model')
	parser.add_argument('--is_c_format_bin', action='store_true', help='use a wiki dump to train the model')

	args = parser.parse_args()
	corpus_file = args.corpus
	output_words_file = args.output_words_file
	output_similar_words_file = args.output_similar_words_file
	word2vec_model = args.word2vec_model
	is_c_format_bin = args.is_c_format_bin

	if is_c_format_bin:
		word2vec = gensim.models.KeyedVectors.load_word2vec_format(word2vec_model, binary=True)
	else:
		word2vec = gensim.models.word2vec.Word2Vec.load(word2vec_model)

	window_size = 2
	for line in tqdm.tqdm(Dataset(corpus_file)):
		words = line
		for i in range(window_size, len(words)-window_size):
			gram = words[i-window_size:i+window_size+1]
			center_word = gram.pop(len(gram) // 2)
			if not center_word or not all(gram):
				continue

			similar_words = get_naive_similar(center_word, word2vec)
			if not similar_words:
				continue
			output_words_file.write(center_word + '\n')
			output_similar_words_file.write('\t'.join(similar_words) + '\n')
