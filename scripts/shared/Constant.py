#! /usr/bin/env python
# -*- coding: utf-8 -*-

# side of the grid
side_size = 100
grid_size = side_size*side_size

# TODO: See if I can delete this
min_latitude = 41.100542
max_latitude = 41.249139
delta_latitude = max_latitude - min_latitude
ratio_latitude = delta_latitude/side_size

min_longitude = -8.7222031
max_longitude = -8.529393
delta_longitude = max_longitude - min_longitude
ratio_longitude = delta_longitude/side_size

ntrajectories = 1674151
percentage_threshold = 5

def get_percentage_threshold():
    return percentage_threshold

def set_percentage_threshold(tr):
    global percentage_threshold
    percentage_threshold = tr

def threshold():
    return float(get_percentage_threshold()/100)*ntrajectories
