#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time

from popular_region import Utils
from shared import Constant
from shared import Utils as sh_utils

def area(min_row, max_row, min_col, max_col):
    return (max_row - min_row + 1)*(max_col - min_col + 1)

def extend_left(min_row, max_row, min_col, max_col, meanDensity, used, data):
    if min_col == 0:
        return None
    current_density = meanDensity*area(min_row, max_row, min_col, max_col)
    extension_contains_dense = False
    extension_density = 0
    for row in range(min_row, max_row + 1):
        if used[row][min_col-1]:
            return None
        if data[row][min_col-1] >= Constant.threshold():
            extension_contains_dense = True
        extension_density += data[row][min_col-1]
    new_mean_density = (extension_density +  current_density) / area(min_row, max_row, min_col-1, max_col)  
    if new_mean_density < Constant.threshold() or not extension_contains_dense:
        return None
    return (min_row, min_col-1, max_row, max_col, new_mean_density)

def extend_right(min_row, max_row, min_col, max_col, meanDensity, used, data):
    if max_col == len(data[0])-1:
        return None
    current_density = meanDensity*area(min_row, max_row, min_col, max_col)
    extension_contains_dense = False
    extension_density = 0
    for row in range(min_row, max_row + 1):
        if used[row][max_col+1]:
            return None
        if data[row][max_col+1] >= Constant.threshold():
            extension_contains_dense = True
        extension_density += data[row][max_col+1]
    new_mean_density = (extension_density +  current_density) / area(min_row, max_row, min_col, max_col+1)  
    if new_mean_density < Constant.threshold() or not extension_contains_dense:
        return None
    return (min_row, min_col, max_row, max_col+1, new_mean_density)

def extend_up(min_row, max_row, min_col, max_col, mean_density, used, data):
    if min_row == 0:
        return None
    current_density = mean_density*area(min_row, max_row, min_col, max_col)
    extension_contains_dense = False
    extension_density = 0
    for col in range(min_col, max_col+1):
        if used[min_row-1][col]:
            return None
        if data[min_row-1][col] >= Constant.threshold():
            extension_contains_dense = True
        extension_density += data[min_row-1][col]

    new_mean_density = (extension_density + current_density) / area(min_row-1, max_row, min_col, max_col)
    if new_mean_density < Constant.threshold() or not extension_contains_dense:
        return None
    return (min_row-1, min_col, max_row, max_col, new_mean_density)

def extend_down(min_row, max_row, min_col, max_col, mean_density, used, data):
    if max_row == len(data)-1:
        return None
    current_density = mean_density*area(min_row, max_row, min_col, max_col)
    extension_contains_dense = False
    extension_density = 0
    for col in range(min_col, max_col+1):
        if used[max_row + 1][col]:
            return None
        if data[max_row + 1][col] >= Constant.threshold():
            extension_contains_dense = True
        extension_density += data[max_row+1][col]

    new_mean_density = (extension_density + current_density) / area(min_row, max_row+1, min_col, max_col)
    if new_mean_density < Constant.threshold() or not extension_contains_dense:
        return None
    return (min_row, min_col, max_row+1, max_col, new_mean_density)

def find_roi(data):
    used = [[False for _ in range(len(data))] for _ in range(len(data[0]))]
    dense_cell = list()
    for row in range(len(data)):
        for col in range(len(data[0])):
            if data[row][col] >= Constant.threshold():
                dense_cell.append((data[row][col],row, col))
    dense_cell = sorted(dense_cell, reverse=True)

    rois = set()
    
    # Array of functions for the extension process
    extensions = [extend_up, extend_down, extend_left, extend_right]
    for (_,row, col) in dense_cell:
        # if used[row][col] : already in ROI
        if not used[row][col]:
            # ROI identify by the 4 corner
            (min_row, min_col,max_row, max_col) = (row,col,row,col)
            # In the beginning, only one cell
            mean_density = data[row][col]
            ext_possible = True
            while ext_possible:

                (new_min_row, new_min_col, new_max_row, new_max_col) = (None,None,None,None)
                new_mean_density = None

                for ext in extensions:
                    res = ext(min_row, max_row, min_col, max_col, mean_density, used, data)
                    # res is None => region would overlap/be outside the grid or new region has mean_density < threshold
                    if res is not None:
                        if new_mean_density is None:
                            (new_min_row, new_min_col, new_max_row, new_max_col) = (res[0], res[1], res[2], res[3])
                            new_mean_density = res[4]
                        elif new_mean_density < res[4]:
                            (new_min_row, new_min_col, new_max_row, new_max_col) = (res[0], res[1], res[2], res[3])
                            new_mean_density = res[4]
                if new_mean_density is None:
                    ext_possible = False
                else:
                    (min_row, min_col, max_row, max_col) = (new_min_row, new_min_col, new_max_row, new_max_col)
                    mean_density = new_mean_density
            
            rois.add((min_row, min_col, max_row, max_col))
    return rois

def run(data):
    start_time = time.time()
    rois = find_roi(data)
    end_time = time.time()
    return {'rois': rois, 'time': end_time - start_time}
