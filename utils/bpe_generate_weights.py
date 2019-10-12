#!/usr/bin/env python3

import sys
import math
import argparse
from collections import Counter
from utils import extract_tag_from_analysis, generate_regex

# TODO: HANDLE THIS BETTER
import sys
sys.path.append("./eval")
from eval_utils import get_apertium_analyses

# TODO: MOVE TO UTILS
import re
def get_lemma(analysis):
    return re.sub('<.*>$', '', analysis)

def get_lemmas(analyses):
    return [get_lemma(a) for a in analyses]

def get_no_of_tags(analysis):
    return sum([c=='<' for c in analysis])

def get_no_of_affixes(bpe_segment):
    return len(re.findall('@@', bpe_segment))

def get_first_seg(bpe_segment):
    return re.sub(r'@@.*', '', bpe_segment)

import editdistance
def bpe_disambiguate_1(word_a, bpe_segmentation):
    """Compare the first segment from bpe segmentation to apertium's lemma"""
    segments = get_lemmas(word_a)
    first_segment = get_first_seg(bpe_segmentation)
    lev_distance = [editdistance.eval(s, first_segment) for s in segments]
    min_dis = min(lev_distance)
    return [generate_regex(a) for a, d in zip(word_a, lev_distance) if d == min_dis][0]

def bpe_disambiguate(word_a, bpe_segmentation):
    # TODO: Compare the word_a and the bpe_segmentation
    segments = get_lemmas(word_a)
    first_segment = get_first_seg(bpe_segmentation)
    lev_distance = [editdistance.eval(s, first_segment) + abs(get_no_of_tags(a) - get_no_of_affixes(s))
        for s, a in zip(segments, word_a)]
    
    min_dis = min(lev_distance)
    
    return [generate_regex(a) for a, d in zip(word_a, lev_distance) if d == min_dis][0]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a weightlist using a set of segmented words')
    parser.add_argument('--words_file',
                        type=argparse.FileType('r'),
                        required=True,
                        help='words file')
    parser.add_argument('--segmented_file',
                        type=argparse.FileType('r'),
                        required=True,
                        help='segmented words')
    parser.add_argument('--compiled_dict',
                        required=True,
                        help='compiled dict')
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
    segmented_file = args.segmented_file
    compiled_dict = args.compiled_dict
    output_weightlist = args.output_weightlist
    default_weightlist = args.default_weightlist

    words = [[l.strip()] for l in words_file.readlines() if l.strip()]
    words = sum(words, [])
    segments = [l.strip().split() for l in segmented_file.readlines() if l.strip()]
    segments = sum(segments, [])

    # TODO: ASSERT LENGTH OF SEGMENTS AND WORDS
    analyses = get_apertium_analyses(words, compiled_dict, 'temp_delete', only_one_analysis=False)
    # print(analyses[:2])
    # print(segments[:2])
    # exit()
    weights = [bpe_disambiguate(a, s) for a, s in zip(analyses, segments)]
    weights = [w for w in weights if w]
    counts = Counter(weights)
    sum_counts = sum(counts.values()) + len(counts) + 1

    # with open(output_weightlist, 'w') as f:
    for t in counts:
        output_weightlist.write('{}::{}\n'.format(t, -math.log((1 + counts[t]) / sum_counts )))
        # print('{}::{}\n'.format(t, -math.log((1 + counts[t]) / sum_counts )))
        # break

    # with open(default_weightlist, 'w') as f:
    default_weightlist.write('[?*]::{}'.format(-math.log(1 / sum_counts)))
