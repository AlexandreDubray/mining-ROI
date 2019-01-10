#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from shared.Utils import print_flush, get_inFlux

from baseline import Greedy

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_data_directory():
    return os.path.join(SCRIPT_DIR, '..', '..', 'data')

baseline_output_file = os.path.join(get_data_directory(), 'output', 'baseline.out')

def get_matrix_file():
    try:
        return open(os.path.join(get_data_directory(), 'baseline-matrix.tsv'), 'r')
    except FileNotFoundError:
        write_baseline_matrix()
        return open(os.path.join(get_data_directory(), 'baseline-matrix.tsv'), 'r')


def get_output_file():
    print_flush('Getting the output of the baseline algorithm')
    try:
        return open(baseline_output_file, 'r')
    except FileNotFoundError:
        print_flush('Output of baseline algorithm not found. Running the algorithm')
        Greedy.run()
        print_flush('Baseline runned.')
        return open(baseline_output_file, 'r')

def write_baseline_matrix():
    influx = get_inFlux()
    with open(os.path.join(get_data_directory(), 'baseline-matrix.tsv'), 'w') as f:
        f.write('{}\n'.format('\t'.join([str(x) for x in get_inFlux()])))
