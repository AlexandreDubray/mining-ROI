#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from shared.Utils import get_inFlux, map_cell_to_id
from shared.Constant import *


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_data_directory():
    return os.path.join(SCRIPT_DIR, '..', '..', 'data', str(get_percentage_threshold()))

def mip_output_file():
    return os.path.join(get_data_directory(), 'output', 'mip.out')

def mip_gurobi_output_file():
    return os.path.join(get_data_directory(), 'gurobi.out')

def mip_rectangles_file():
    return os.path.join(get_data_directory(), 'mip-rectangles.in')

def mip_circles_file():
    return os.path.join(get_data_directory(), 'mip-circles.in')

def mip_matrix_file():
    return os.path.join(get_data_directory(), 'mip-matrix.tsv')

from mip import mip_column
from mip import select_best

def get_mip_matrix_file():
    try:
        return open(mip_matrix_file(), 'r')
    except FileNotFoundError:
        write_mip_matrix()
        return open(mip_matrix_file(), 'r')

def get_mip_rectangles_file():
    try:
        return open(mip_rectangles_file(), 'r')
    except FileNotFoundError:
        mip_column.create_rectangles()
        return open(mip_rectangles_file(), 'r')

def get_mip_circles_file():
    try:
        return open(mip_circles_file(), 'r')
    except FileNotFoundError:
        mip_column.create_circles()
        return open(mip_circles_file(), 'r')

def get_mip_output_file():
    try:
        return open(mip_output_file(), 'r')
    except FileNotFoundError:
        mip_column.run()
        select_best.run_mdl()
        return open(mip_output_file(), 'r')

def get_gurobi_output_file():
    try:
        return open(mip_gurobi_output_file(), 'r')
    except FileNotFoundError:
        mip_column.run()
        return open(mip_gurobi_output_file(), 'r')

def write_mip_matrix():
    influx = get_inFlux()
    mip_matrix = [ [1 if influx[map_cell_to_id(i,j)] > threshold() else 0 for j in range(side_size)] for i in range(side_size)]
    with open(os.path.join(get_data_directory(), 'mip-matrix.tsv'), 'w') as f:
        for row in range(len(mip_matrix)):
            f.write('{}\n'.format('\t'.join([str(x) for x in mip_matrix[row]])))


def get_mip_output_filenames():
    return [mip_output_file(),
            mip_gurobi_output_file(),
            mip_rectangles_file(),
            mip_circles_file(),
            mip_matrix_file()]


initial_mip_data = None
total_number_dense = 0

def get_initial_mip_data():
    global initial_mip_data, total_number_dense
    if initial_mip_data is None:
        with get_mip_matrix_file() as f:
            initial_mip_data = [[int(x) for x in line.split("\t")] for line in f.read().split("\n") if line != ""]
            maxX = -1
            minX = sys.maxsize
            maxY = -1
            minY = sys.maxsize
            for row in range(len(initial_mip_data)):
                for col in range(len(initial_mip_data[row])):
                    if initial_mip_data[row][col] == 1:
                        maxX = max(maxX,col)
                        minX = min(minX,col)
                        maxY = max(maxY,row)
                        minY = min(minY,row)
                        total_number_dense += 1

        initial_mip_data = initial_mip_data[minY:maxY+1]
        for i,d in enumerate(initial_mip_data):
            initial_mip_data[i] = d[minX:maxX+1]
    return (initial_mip_data, total_number_dense)
