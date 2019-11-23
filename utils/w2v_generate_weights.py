#!/usr/bin/env python3

import sys
import math
import argparse
from collections import Counter
from utils import extract_tag_from_analysis, generate_regex

def get_weight(word_a, similar_a):
	"""
	Return the count of times the word had analyses tags
	similar to those of an un-ambiguous similar word

	word_a: The word analyses
	similar_a: The similar word analyses (list of strings)
	"""

	# TODO: Use streamparser?
	# A list of the word's analyses
	word_a = word_a.strip('$').split('/')[1:]

	# A list of lists for the similar words' analyses
	similar_a = [analysis.strip('$').split('/')[1:]
		for analysis in similar_a]

	# TODO: Can word_a be None?
	# Ignore the token if it doesn't have an analysis *token
	if not word_a or word_a[0].startswith('*'):
		return None

	# The word isn't ambiguous
	if len(word_a) == 1:
		return Counter({generate_regex(word_a[0]):1})

	# TODO: Use all the analyses??
	unambig_analyses = sum(similar_a, [])

	unambig_analyses = [a[0] for a in similar_a if len(a)==1 and not a[0].startswith('*')]
	tags = [extract_tag_from_analysis(word_analysis) for word_analysis in unambig_analyses]
	
	# Update this formula for having some weighting effect
	tags_count = Counter(tags)
	return Counter({generate_regex(analysis): tags_count[extract_tag_from_analysis(analysis)] for analysis in word_a})

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Generate a weightlist using a set of words and their similar words given the context')
	parser.add_argument('--words_file',
						type=argparse.FileType('r'),
						required=True,
						help='analyzed words file')
	parser.add_argument('--similar_file',
						type=argparse.FileType('r'),
						required=True,
						help='analyzed similar words file (each line in tab-separated)')
	parser.add_argument('--output_weightlist',
						type=argparse.FileType('w'),
						required=True,
						help='The output weightlist using the similar words analysis')
	parser.add_argument('--default_weightlist',
						type=argparse.FileType('w'),
						required=True,
						help='The weightlist containing a laplace smoothed weight')
	args = parser.parse_args()
	words_file = args.words_file
	similar_words_file = args.similar_file
	output_weightlist = args.output_weightlist
	default_weightlist = args.default_weightlist

	words_analyses = [l.strip() for l in words_file.readlines() if l.strip()]

	# Split the similar words analyses
	similar_words_analyses = [l.strip().split('\t') for l in similar_words_file.readlines() if l.strip()]

	# Find the list of Counters for each word
	weights = [get_weight(w, s) for w, s in zip(words_analyses, similar_words_analyses)]
	weights = [w for w in weights if w]

	# Merge the list of Counters
	words_weights = sum(weights, Counter())
	
	# Compute the value of the denominator
	denominator = sum(words_weights.values()) + len(words_weights) + 1
	for t in words_weights:
		output_weightlist.write('{}::{}\n'.format(t, -math.log((1 + words_weights[t]) / denominator)))

	default_weightlist.write('[?*]::{}'.format(-math.log(1 / denominator)))
