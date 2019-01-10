#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from .Constant import *

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

inFlux = None

def print_flush(message):
    print(message)
    sys.stdout.flush()

# Fluxs matrices representing the data

def map_cell_to_id(row,col):
    return row*side_size + col

def map_id_to_cell(cell_id):
    return (cell_id/width, cell_id % width)

def map_pos_to_node(pos):
    longitude = pos[0]
    latitude = pos[1]
    col = int((longitude-min_longitude)/ratio_longitude) if longitude != max_longitude else side_size - 1
    row = int((latitude-min_latitude)/ratio_latitude) if latitude != max_latitude else side_size - 1
    return map_cell_to_id(row, col)

def get_long_lat_from_str(string_rep):
    if string_rep[-1] == '\n':
        string_rep = string_rep[:-1]
    s = string_rep[1:-1].split(',')
    return [float(x) for x in s]

def parse_data():
    """Parse the file and populate the flux matrix and inFlux vector"""
    global inFlux
    inFlux = [0 for i in range(grid_size)] # Influx of each cells of the grid
    with open(os.path.join(SCRIPT_DIR, '..', '..', 'data', 'parsed', 'KaggleTaxis.in'), 'r') as f:
        for trajectory in f.readlines():
            positions = [get_long_lat_from_str(x) for x in trajectory.split(' ') if x != '\n']
            for i in range(len(positions)-1):
                node1 = map_pos_to_node(positions[i])
                node2 = map_pos_to_node(positions[i+1])
                #print("{} {}".format(node1, node2))
                inFlux[node2] += 1
                # If source of the trajectory
                if i == 0:
                    inFlux[node1] += 1

def get_inFlux():
    if inFlux is None:
        parse_data()
    return inFlux

def get_initial_matrix():
    if inFlux is None:
        parse_data()
    return [[inFlux[map_cell_to_id(row, col)] for col in range(side_size)] for row in range(side_size)]

# Utilities for the webapp
def map_rectangles_to_pos(minRow, maxRow, minCol, maxCol):
    """ /!\ minRow give the higher latitude /!\ """
    minLat = min_latitude + minRow*ratio_latitude
    maxLat = min_latitude + (maxRow+1)*ratio_latitude
    maxLong = min_longitude + minCol*ratio_longitude
    minLong = min_longitude +(maxCol+1)*ratio_longitude
    return (minLat, maxLat, minLong, maxLong)

def get_mip_shift():
    with get_mip_matrix_file() as f:
        data = [[int(x) for x in line.split("\t")] for line in f.read().split("\n") if line != ""]
        maxCol = -1
        minCol = sys.maxsize
        maxRow = -1
        minRow = sys.maxsize
        for col in range(len(data)):
            for row in range(len(data[0])):
                if data[row][col] == 1:
                    maxCol = max(maxCol,col)
                    minCol = min(minCol,col)
                    maxRow = max(maxRow,row)
                    minRow = min(minRow,row)
        return (minRow, minCol)

