#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pickle

from .Constant import *

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

inFlux = None

def get_data_directory():
    return os.path.join(SCRIPT_DIR, '..', '..', 'data', str(get_percentage_threshold()))

def get_data_file():
    return os.path.join(SCRIPT_DIR, '..', '..', 'data', 'parsed', 'KaggleTaxis.pkl')

def get_data():
    with open(get_data_file(), 'rb') as f:
        return pickle.load(f)

def print_flush(message):
    print(message)
    sys.stdout.flush()

# Fluxs matrices representing the data

def map_cell_to_id(row,col):
    i = row*side_size() + col
    return i

def map_id_to_cell(cell_id):
    return (cell_id/width, cell_id % width)

def map_pos_to_node(pos):
    (row,col) = map_pos_to_cell(pos)
    return map_cell_to_id(row, col)

def map_pos_to_cell(pos):
    latitude = pos[0]
    longitude = pos[1]
    col = int((longitude-min_longitude)/ratio_longitude()) if longitude != max_longitude else side_size() - 1
    row = int((latitude-min_latitude)/ratio_latitude()) if latitude != max_latitude else side_size() - 1
    return (row,col)

def get_long_lat_from_str(string_rep):
    if string_rep[-1] == '\n':
        string_rep = string_rep[:-1]
    s = string_rep[1:-1].split(',')
    return [float(x) for x in s]

def parse_data():
    """Parse the file and populate the flux matrix and inFlux vector"""
    global inFlux
    inFlux = [0 for i in range(grid_size())] # Influx of each cells of the grid
    data_file = os.path.join(SCRIPT_DIR, '..', '..', 'data', 'parsed', 'KaggleTaxis.pkl')
    with open(data_file, 'rb') as f:
        data = pickle.load(f)
        for trajectory_id in data:
            posotions = data[trajectory_id]['POLYLINE']
            for i in range(len(positions)-1):
                node1 = map_pos_to_node(positions[i])
                node2 = map_pos_to_node(positions[i+1])
                inFlux[node2] += 1
                # If source of the trajectory
                if i == 0:
                    inFlux[node1] += 1

def get_inFlux():
    # TODO: delete this
    #parse_data()
    if inFlux is None:
        parse_data()
    return inFlux

def reset_influx():
    global inFlux
    inFlux = None

def get_initial_matrix():
    if inFlux is None:
        parse_data()
    return [[inFlux[map_cell_to_id(row, col)] for col in range(side_size())] for row in range(side_size())]
