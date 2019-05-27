#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from shared.Utils import get_inFlux, map_cell_to_id, get_data_directory
from shared.Constant import *

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def mip_matrix_file():
    return os.path.join(get_data_directory(), 'mip-matrix-{}-{}.tsv'.format(str(get_percentage_threshold()), str(side_size())))

def get_mip_matrix_file():
    try:
        return open(mip_matrix_file(), 'r')
    except FileNotFoundError:
        write_mip_matrix()
        return open(mip_matrix_file(), 'r')

def write_mip_matrix():
    influx = get_inFlux()
    mip_matrix = [ [1 if influx[map_cell_to_id(i,j)] > threshold() else 0 for j in range(side_size())] for i in range(side_size())]
    with open(os.path.join(get_data_directory(), 'mip-matrix-{}-{}.tsv'.format(get_percentage_threshold(), side_size())), 'w') as f:
        for row in range(len(mip_matrix)):
            f.write('{}\n'.format('\t'.join([str(x) for x in mip_matrix[row]])))

def get_mip_data():
    with get_mip_matrix_file() as f:
        mip_data = [[int(x) for x in line.split('\t')] for line in f.read().split('\n') if line != '']
        maxX = -1
        minX = sys.maxsize
        maxY = -1
        minY = sys.maxsize
        for row in range(len(mip_data)):
            for col in range(len(mip_data[0])):
                if mip_data[row][col] == 1:
                    maxX = max(maxX,col)
                    minX = min(minX,col)
                    maxY = max(maxY,row)
                    minY = min(minY,row)

    mip_data = mip_data[minY:maxY+1]
    for i,d in enumerate(mip_data):
        mip_data[i] = d[minX:maxX+1]
    return mip_data

def create_sum_entry_matrix(mip_data):
    sum_entry_matrix = [[0 for _ in range(len(mip_data[0]))] for _ in range(len(mip_data))]
    for row in range(len(mip_data)):
        for col in range(len(mip_data[row])):
            if row == 0:
                if col == 0:
                    sum_entry_matrix[row][col] = mip_data[row][col]
                else:
                    sum_entry_matrix[row][col] = mip_data[row][col] + sum_entry_matrix[row][col-1]
            else:
                if col == 0:
                    sum_entry_matrix[row][col] = mip_data[row][col] + sum_entry_matrix[row-1][col]
                else:
                    sum_entry_matrix[row][col] = mip_data[row][col] + sum_entry_matrix[row-1][col] + sum_entry_matrix[row][col-1] - sum_entry_matrix[row-1][col-1]
    return sum_entry_matrix
