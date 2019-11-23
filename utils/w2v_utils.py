#!/usr/bin/env python3

import re
import string
from gensim.corpora import WikiCorpus

def clean_line(line):
	for c in string.punctuation:
		line = line.replace(c, ' ')
	return line

class Dataset:
	"""
	Wrap corpus for avoiding complete loading of file into memory
	"""
	def __init__(self, file):
		self.corpus_file = file

	def __iter__(self):
		self.corpus_file.seek(0)
		for line in self.corpus_file:
			line = clean_line(line)
			words = line.split()
			# If the sentence is too long then divide it
			# into segments of 1000 words each until the
			# sentence is completely consumed
			i = 0
			while i < len(words):
				i+=1000
				yield words[i-1000:i]

class WikiDataset:
	"""
	Use a compressed wikipedia dump
	"""
	def __init__(self, file):
		self.corpus = WikiCorpus(file)

	def __iter__(self):
		for doc in self.corpus.get_texts():
			doc = clean_line(' '.join(doc)).split()
			yield doc
