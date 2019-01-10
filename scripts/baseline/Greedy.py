#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from baseline import Utils
from shared import Constant
from shared import Utils as sh_utils

def get_data():
    with Utils.get_matrix_file() as f:
        inFlux = [int(x) for x in f.readlines()[0].split('\t') if x != '']
        data = [[inFlux[sh_utils.map_cell_to_id(row,col)] for col in range(Constant.side_size)] for row in range(Constant.side_size)]
    return data

def area(minRow, maxRow, minCol, maxCol):
    return (maxRow - minRow + 1)*(maxCol - minCol + 1)

def extend_left(minRow, maxRow, minCol, maxCol, meanDensity, used, data):
    if minCol == 0:
        return None
    current_density = meanDensity*area(minRow, maxRow, minCol, maxCol)
    extension_contains_dense = False
    extension_density = 0
    for row in range(minRow, maxRow + 1):
        if used[row][minCol-1]:
            return None
        if data[row][minCol-1] > Constant.threshold:
            extension_contains_dense = True
        extension_density += data[row][minCol-1]
    new_mean_density = (extension_density +  current_density) / area(minRow, maxRow, minCol-1, maxCol)  
    if new_mean_density < Constant.threshold or not extension_contains_dense:
        return None
    return (minRow, maxRow, minCol-1, maxCol, new_mean_density)

def extend_right(minRow, maxRow, minCol, maxCol, meanDensity, used, data):
    if maxCol == Constant.side_size-1:
        return None
    current_density = meanDensity*area(minRow, maxRow, minCol, maxCol)
    extension_contains_dense = False
    extension_density = 0
    for row in range(minRow, maxRow + 1):
        if used[row][maxCol+1]:
            return None
        if data[row][maxCol+1] > Constant.threshold:
            extension_contains_dense = True
        extension_density += data[row][maxCol+1]
    new_mean_density = (extension_density +  current_density) / area(minRow, maxRow, minCol, maxCol+1)  
    if new_mean_density < Constant.threshold or not extension_contains_dense:
        return None
    return (minRow, maxRow, minCol, maxCol+1, new_mean_density)

def extend_up(minRow, maxRow, minCol, maxCol, mean_density, used, data):
    if minRow == 0:
        return None
    current_density = mean_density*area(minRow, maxRow, minCol, maxCol)
    extension_contains_dense = False
    extension_density = 0
    for col in range(minCol, maxCol+1):
        if used[minRow-1][col]:
            return None
        if data[minRow-1][col] > Constant.threshold:
            extension_constains_dense = True
        extension_density += data[minRow-1][col]

    new_mean_density = (extension_density + current_density) / area(minRow-1, maxRow, minCol, maxCol)
    if new_mean_density < Constant.threshold or not extension_contains_dense:
        return None
    return (minRow-1, maxRow, minCol, maxCol, new_mean_density)

def extend_down(minRow, maxRow, minCol, maxCol, mean_density, used, data):
    if maxRow == Constant.side_size-1:
        return None
    current_density = mean_density*area(minRow, maxRow, minCol, maxCol)
    extension_contains_dense = False
    extension_density = 0
    for col in range(minCol, maxCol+1):
        if used[maxRow + 1][col]:
            return None
        if data[maxRow + 1][col] > Constant.threshold:
            extension_constains_dense = True
        extension_density += data[maxRow+1][col]

    new_mean_density = (extension_density + current_density) / area(minRow, maxRow+1, minCol, maxCol)
    if new_mean_density < Constant.threshold or not extension_contains_dense:
        return None
    return (minRow, maxRow+1, minCol, maxCol, new_mean_density)

def find_roi(threshold):
    data = get_data()
    used = [[False for col in range(Constant.side_size)] for row in range(Constant.side_size)]
    dense_cell = list()
    for row in range(Constant.side_size):
        for col in range(Constant.side_size):
            if data[row][col] >= Constant.threshold:
                dense_cell.append((data[row][col],row, col))
    dense_cell = sorted(dense_cell, reverse=True)

    rois = []
    extensions = [extend_up, extend_down, extend_left, extend_right]
    for (_,row, col) in dense_cell:
        # if used[row][col] : already in ROI
        if not used[row][col]:
            # ROI identify by the 4 corner
            minRow = row
            maxRow = row
            minCol = col
            maxCol = col
            mean_density = data[row][col]

            ext_possible = True
            while ext_possible:

                new_minRow = None
                new_maxRow = None
                new_minCol = None
                new_maxCol = None
                new_meanDensity = None

                for ext in extensions:
                    res = ext(minRow, maxRow, minCol, maxCol, mean_density, used, data)
                    if res is not None:
                        if new_meanDensity is None:
                            new_minRow = res[0]
                            new_maxRow = res[1]
                            new_minCol = res[2]
                            new_maxCol = res[3]
                            new_meanDensity = res[4]
                        elif new_meanDensity < res[4]:
                            new_minRow = res[0]
                            new_maxRow = res[1]
                            new_minCol = res[2]
                            new_maxCol = res[3]
                            new_meanDensity = res[4]
                if new_meanDensity is None:
                    ext_possible = False
                else:
                    minRow = new_minRow
                    maxRow = new_maxRow
                    minCol = new_minCol
                    maxCol = new_maxCol
                    mean_density = new_meanDensity
            
            for r in range(minRow, maxRow + 1):
                for c in range(minCol, maxCol + 1):
                    used[r][c] = True
            rois.append((minRow, maxRow, minCol, maxCol))
    return rois

def run():
    rois = find_roi(Constant.threshold)
    with open(Utils.baseline_output_file, 'w') as f:
        for roi in rois:
            f.write('{}\n'.format(' '.join([str(x) for x in roi])))

