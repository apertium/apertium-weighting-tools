#!/usr/bin/env python3

import os
import re
import sys
import tqdm
import gensim
import string
import argparse

def clean_word(word):
	return re.sub('[^a-z \u0400-\u04FF]', ' ', word)
	# return re.sub(r'[0-9]', ' ', word)

class Dataset:
	"""
	Wrap corpus for avoiding complete loading of file into memory
	"""
	def __init__(self, file):
		self.corpus_file = file

	def __iter__(self):
		self.corpus_file.seek(0)
		for line in self.corpus_file:
			words = line.split()
			# If the sentence is too long then divide it
			# into segments of 1000 words each until the
			# sentence is completely consumed
			i = 0
			while i < len(words):
				i+=1000
				yield words[i-1000:i]

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
	parser.add_argument('--corpus_w2v',
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
	args = parser.parse_args()
	corpus_file = args.corpus
	corpus_file_w2v = args.corpus_w2v
	output_words_file = args.output_words_file
	output_similar_words_file = args.output_similar_words_file

	import logging  # Setting up the loggings to monitor gensim
	logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)

	word2vec_file = 'word2vec.model'
	if word2vec_file in os.listdir('.'):
		word2vec = Word2Vec.load(word2vec_file)
	else:
		word2vec = gensim.models.word2vec.Word2Vec(min_count=20,
			window=2,
			size=300,
			sample=6e-5,
			alpha=0.03,
			min_alpha=0.0007,
			negative=20,
			workers=4)

		word2vec.build_vocab(Dataset(corpus_file_w2v), progress_per=50000)
		word2vec.train(Dataset(corpus_file_w2v), total_examples=word2vec.corpus_count, epochs=50, report_delay=1)
		word2vec.save(word2vec_file)
	window_size = 2
	for line in tqdm.tqdm(Dataset(corpus_file)):
		words = line
		for i in range(window_size, len(words)-window_size):
			gram = words[i-window_size:i+window_size+1]
			center_word = gram.pop(len(gram) // 2)
			if not center_word or not all(gram):
				continue

			similar_words = get_similar_tokens(gram, word2vec)
			if not similar_words:
				continue
			output_words_file.write(center_word + '\n')
			output_similar_words_file.write('\t'.join(similar_words) + '\n')
