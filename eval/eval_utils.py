#!/usr/bin/env python3

import re
import subprocess
from pathlib import Path

def get_apertium_analyses(X, weighted_bin, base_dir, only_one_analysis=True):
    joined_X = ' \n'.join(X)

    base_input_as_file = str(Path(base_dir, 'base_input_as_file'))
    with open(base_input_as_file, 'w') as f:
        f.write(joined_X)

    deformatted_input = str(Path(base_dir, 'deformatted_input'))
    assert(subprocess.run(['apertium-destxt', '-n', base_input_as_file, deformatted_input]).returncode == 0)

    with open(deformatted_input, 'r') as f:
        lines = f.readlines()

    # Separate the tokens using [] to avoid multi-word analysis
    tokenized_input = str(Path(base_dir, 'tokenized_input'))
    with open(tokenized_input, 'w') as f:
        f.write(''.join([re.sub('\[ \n$', ' [] [\n', t) for t in lines]))
        f.write('\n')

    analyzed_output = str(Path(base_dir, 'analyzed_output'))

    processing_command = ['lt-proc', weighted_bin, tokenized_input, analyzed_output]
    if only_one_analysis:
    	processing_command.append('-N 1')

    assert(subprocess.run(processing_command).returncode == 0)

    reformatted_output = str(Path(base_dir, 'reformatted_output'))
    subprocess.run(['apertium-retxt', analyzed_output, reformatted_output])

    with open(reformatted_output, 'r') as f:
        # Just read the lines and let stream parser do the job
        lines = f.readlines()

    analyses = [stream_parser_extract_analyses(l) for l in lines]
    if only_one_analysis:
    	return [a[0] for a in analyses]
    return analyses

def split_X_y(file_lines):
    '^With/with<pr>$'
    splitted_lines = [line.strip()[1:-1].split('/') for line in file_lines if line.strip()]

    tokens = [l[0] for l in splitted_lines]
    targets = [l[1] for l in splitted_lines]

    assert(len(tokens)==len(targets)), 'Token and Target vectors size mismatch ({}!={})'.format(len(tokens), len(targets))

    return tokens, targets

from streamparser import parse, reading_to_string
def stream_parser_split_X_y(file_lines):
    lexical_units = parse('\n'.join(file_lines))
    X = []
    y = []
    for lexical_unit in lexical_units:
        y.append(reading_to_string(lexical_unit.readings[0]))
        X.append(lexical_unit.wordform)
    assert(len(y)==len(X)), 'Token and Target vectors size mismatch ({}!={})'.format(len(y), len(X))
    return X, y

def stream_parser_extract_analyses(line):
    unit = [unit for unit in parse(line)]
	# TODO: Handle cases such as "Empty readings for ///<sent>" in a better way
    if not unit:
    	return ['']
    unit = unit[0]

    # Is the "///<sent>" really handeled?
    analyses = [reading_to_string(reading) for reading in unit.readings]
    return analyses if len(analyses) else ['']
