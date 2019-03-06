#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import random

from baseline import Utils
from shared import Constant
from shared import Utils as sh_utils

def get_data(use_synt_data, synt_data):
    if use_synt_data:
        if synt_data is None:
            print("Error: You forced the use of synthetic data but do not provide them.")
            sys.exit(1)
        # Here we assume a minimum sup of 0.05

        data = [[random.randint(5,30) if synt_data[row][col] == 1 else random.randint(0,4) for col in range(len(synt_data[0]))] for row in range(len(synt_data))]
        return data
    else:
        with Utils.get_matrix_file() as f:
            inFlux = [int(x) for x in f.readlines()[0].split('\t') if x != '']
            data = [[inFlux[sh_utils.map_cell_to_id(row,col)] for col in range(Constant.side_size())] for row in range(Constant.side_size())]
        return data

def area(minRow, maxRow, minCol, maxCol):
    return (maxRow - minRow + 1)*(maxCol - minCol + 1)

def extend_left(minRow, maxRow, minCol, maxCol, meanDensity, used, data, use_synt_data):
    if minCol == 0:
        return None
    current_density = meanDensity*area(minRow, maxRow, minCol, maxCol)
    extension_contains_dense = False
    extension_density = 0
    for row in range(minRow, maxRow + 1):
        if used[row][minCol-1]:
            return None
        if data[row][minCol-1] >= (Constant.threshold() if not use_synt_data else 5):
            extension_contains_dense = True
        extension_density += data[row][minCol-1]
    new_mean_density = (extension_density +  current_density) / area(minRow, maxRow, minCol-1, maxCol)  
    if new_mean_density < (Constant.threshold() if not use_synt_data else 5) or not extension_contains_dense:
        return None
    return (minRow, maxRow, minCol-1, maxCol, new_mean_density)

def extend_right(minRow, maxRow, minCol, maxCol, meanDensity, used, data, use_synt_data):
    if maxCol == len(data[0])-1:
        return None
    current_density = meanDensity*area(minRow, maxRow, minCol, maxCol)
    extension_contains_dense = False
    extension_density = 0
    for row in range(minRow, maxRow + 1):
        if used[row][maxCol+1]:
            return None
        if data[row][maxCol+1] >= (Constant.threshold() if not use_synt_data else 5):
            extension_contains_dense = True
        extension_density += data[row][maxCol+1]
    new_mean_density = (extension_density +  current_density) / area(minRow, maxRow, minCol, maxCol+1)  
    if new_mean_density < (Constant.threshold() if not use_synt_data else 5) or not extension_contains_dense:
        return None
    return (minRow, maxRow, minCol, maxCol+1, new_mean_density)

def extend_up(minRow, maxRow, minCol, maxCol, mean_density, used, data, use_synt_data):
    if minRow == 0:
        return None
    current_density = mean_density*area(minRow, maxRow, minCol, maxCol)
    extension_contains_dense = False
    extension_density = 0
    for col in range(minCol, maxCol+1):
        if used[minRow-1][col]:
            return None
        if data[minRow-1][col] >= (Constant.threshold() if not use_synt_data else 5):
            extension_contains_dense = True
        extension_density += data[minRow-1][col]

    new_mean_density = (extension_density + current_density) / area(minRow-1, maxRow, minCol, maxCol)
    if new_mean_density < (Constant.threshold() if not use_synt_data else 5) or not extension_contains_dense:
        return None
    return (minRow-1, maxRow, minCol, maxCol, new_mean_density)

def extend_down(minRow, maxRow, minCol, maxCol, mean_density, used, data, use_synt_data):
    if maxRow == len(data)-1:
        return None
    current_density = mean_density*area(minRow, maxRow, minCol, maxCol)
    extension_contains_dense = False
    extension_density = 0
    for col in range(minCol, maxCol+1):
        if used[maxRow + 1][col]:
            return None
        if data[maxRow + 1][col] >= (Constant.threshold() if not use_synt_data else 5):
            extension_contains_dense = True
        extension_density += data[maxRow+1][col]

    new_mean_density = (extension_density + current_density) / area(minRow, maxRow+1, minCol, maxCol)
    if new_mean_density < (Constant.threshold() if not use_synt_data else 5) or not extension_contains_dense:
        return None
    return (minRow, maxRow+1, minCol, maxCol, new_mean_density)

def find_roi(threshold, use_synt_data, synt_data):
    data = get_data(use_synt_data, synt_data)
    used = [[False for _ in range(len(data))] for _ in range(len(data[0]))]
    dense_cell = list()
    for row in range(len(data)):
        for col in range(len(data[0])):
            # for synt data: assuming min sup of 0.05
            if data[row][col] >= (Constant.threshold() if not use_synt_data else 5):
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
                    res = ext(minRow, maxRow, minCol, maxCol, mean_density, used, data, use_synt_data)
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
            
            dense = 0
            nondense = 0
            for r in range(minRow, maxRow + 1):
                for c in range(minCol, maxCol + 1):
                    used[r][c] = True
                    if data[r][c] >= (Constant.threshold() if not use_synt_data else 5):
                        dense += 1
                    else:
                        nondense += 1
            rois.append((minRow, maxRow, minCol, maxCol, dense, nondense))
    return rois

def run(use_synt_data=False, synt_data=None):
    start_time = time.time()
    rois = find_roi(Constant.threshold(), use_synt_data, synt_data)
    end_time = time.time()
    if use_synt_data:
        return rois
    else:
        with open(Utils.baseline_time_file(), 'a') as f:
            f.write('{}\n'.format(end_time - start_time))
        #with open(Utils.baseline_output_file(), 'w') as f:
            #for roi in rois:
                #f.write('{}\n'.format(' '.join([str(x) for x in roi])))

