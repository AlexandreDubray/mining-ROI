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
threshold = 0.05*ntrajectories

def map_cell_to_id(row,col):
    return row*side_size + col

def map_id_to_cell(cell_id):
    return (cell_id/width, cell_id % width)


def map_rectangles_to_pos(minRow, maxRow, minCol, maxCol):
    """ /!\ minRow give the higher latitude /!\ """
    minLat = min_latitude + minRow*ratio_latitude
    maxLat = min_latitude + (maxRow+1)*ratio_latitude
    maxLong = min_longitude + minCol*ratio_longitude
    minLong = min_longitude +(maxCol+1)*ratio_longitude
    return (minLat, maxLat, minLong, maxLong)
