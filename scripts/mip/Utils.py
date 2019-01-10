#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from shared.Utils import get_inFlux, map_cell_to_id
from shared.Constant import *

from mip import mip_column

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_data_directory():
    return os.path.join(SCRIPT_DIR, '..', '..', 'data')

mip_output_file = os.path.join(get_data_directory(), 'output', 'mip.out')
mip_rectangles_file = os.path.join(get_data_directory(), 'mip-rectangles.in')

def get_mip_matrix_file():
    try:
        return open(os.path.join(get_data_directory(), 'mip-matrix.tsv'), 'r')
    except FileNotFoundError:
        write_mip_matrix()
        return open(os.path.join(get_data_directory(), 'mip-matrix.tsv'), 'r')

def get_mip_rectangles_file():
    try:
        return open(mip_rectangles_file, 'r')
    except FileNotFoundError:
        mip_column.create_rectangles()
        return open(mip_rectangles_file, 'r')

def get_mip_output_file():
    try:
        return open(mip_output_file, 'r')
    except FileNotFoundError:
        mip_column.run()
        return open(mip_output_file, 'r')

def write_mip_matrix():
    influx = get_inFlux()
    mip_matrix = [ [1 if influx[map_cell_to_id(i,j)] > threshold else 0 for j in range(side_size)] for i in range(side_size)]
    with open(os.path.join(get_data_directory(), 'mip-matrix.tsv'), 'w') as f:
        for row in mip_matrix:
            f.write('{}\n'.format('\t'.join([str(x) for x in row])))

