#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from shared.Utils import print_flush, get_inFlux
from shared.Constant import get_percentage_threshold, side_size

from baseline import Greedy

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_data_directory():
    return os.path.join(SCRIPT_DIR, '..', '..', 'data', str(get_percentage_threshold()))

def baseline_output_file():
    return os.path.join(get_data_directory(), 'output', 'baseline.out')

def baseline_matrix_file():
    return os.path.join(get_data_directory(), 'baseline-matrix.tsv')

def baseline_time_file():
    return os.path.join(get_data_directory(), '..', 'time', str(side_size()), 'baseline.out')

def get_matrix_file():
    try:
        # TODO: delete after
        write_baseline_matrix()
        return open(baseline_matrix_file(), 'r')
    except FileNotFoundError:
        write_baseline_matrix()
        return open(baseline_matrix_file(), 'r')


def get_output_file():
    try:
        return open(baseline_output_file(), 'r')
    except FileNotFoundError:
        Greedy.run()
        return open(baseline_output_file(), 'r')

def get_baseline_time_file():
    try:
        return open(baseline_time_file(), 'r')
    except FileNotFoundError:
        Greedy.run()
        return open(baseline_time_file(), 'r')

def write_baseline_matrix():
    influx = get_inFlux()
    with open(baseline_matrix_file(), 'w') as f:
        f.write('{}\n'.format('\t'.join([str(x) for x in get_inFlux()])))

def get_baseline_output_filenames():
    return [baseline_output_file(), baseline_matrix_file()]
