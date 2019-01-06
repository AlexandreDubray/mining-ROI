#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

from Constant import *

SCRIPT_DIR = os.getcwd()


flux = [ [0 for i in range(grid_size)] for j in range(grid_size)] # Flux matrix between cells of the grid
inFlux = [0 for i in range(grid_size)] # Influx of each cells of the grid

def get_long_lat_from_str(string_rep):
    if string_rep[-1] == '\n':
        string_rep = string_rep[:-1]
    s = string_rep[1:-1].split(',')
    return [float(x) for x in s]

def map_pos_to_node(pos):
    longitude = pos[0]
    latitude = pos[1]
    col = int((longitude-min_longitude)/ratio_longitude) if longitude != max_longitude else side_size - 1
    row = int((latitude-min_latitude)/ratio_latitude) if latitude != max_latitude else side_size - 1
    #print("{} {}".format(row, col))
    return row*side_size + col

def parse_file(data_file):
    """Parse the file and populate the flux matrix and inFlux vector"""
    with open(data_file, 'r') as f:
        for trajectory in f.readlines():
            positions = [get_long_lat_from_str(x) for x in trajectory.split(' ') if x != '\n']
            for i in range(len(positions)-1):
                node1 = map_pos_to_node(positions[i])
                node2 = map_pos_to_node(positions[i+1])
                #print("{} {}".format(node1, node2))
                flux[node1][node2] += 1
                inFlux[node2] += 1

def write_mip_matrix():
    mip_matrix = [ [1 if inFlux[map_cell_to_id(i,j)] > threshold else 0 for j in range(side_size)] for i in range(side_size)]
    with open(os.path.join(SCRIPT_DIR, '..', 'data', 'mip-matrix.tsv'), 'w') as f:
        for row in mip_matrix:
            f.write('{}\n'.format('\t'.join([str(x) for x in row])))

def write_baseline_matrix():
    with open(os.path.join(SCRIPT_DIR, '..', 'data', 'baseline-matrix.tsv'), 'w') as f:
        f.write('{}\n'.format('\t'.join([str(x) for x in inFlux])))

if __name__ == '__main__':
    data_file = sys.argv[1]
    parse_file(data_file)
    write_mip_matrix()
    write_baseline_matrix()
