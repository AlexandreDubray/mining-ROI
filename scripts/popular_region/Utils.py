#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from shared.Utils import get_data_directory, get_inFlux, map_cell_to_id
from shared import Constant

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def popular_region_matrix_file():
    return os.path.join(get_data_directory(), 'popular_region-matrix-{}-{}.tsv'.format(str(Constant.get_percentage_threshold()), str(Constant.side_size())))

def get_popular_region_matrix_file():
    try:
        return open(popular_region_matrix_file(), 'r')
    except FileNotFoundError:
        write_popular_region_matrix()
        return open(popular_region_matrix_file(), 'r')

def write_popular_region_matrix():
    influx = get_inFlux()
    with open(popular_region_matrix_file(), 'w') as f:
        f.write('{}\n'.format('\t'.join([str(x) for x in influx])))

def get_popular_region_data():
    with get_popular_region_matrix_file() as f:
        inFlux = [int(x) for x in f.readlines()[0].split('\t') if x != '']
        data = [[inFlux[map_cell_to_id(row,col)] for col in range(Constant.side_size())] for row in range(Constant.side_size())]
        return data
