#! /usr/bin/env python
# -*- coding: utf-8 -*-

import random
random.seed(11781400)

from mip import mip_column
from popular_region import PopularRegion
from shared.Constant import set_threshold
from experiment.Utils import get_figures_directory

import matplotlib.pyplot as plt
import matplotlib as mpl

import os

params = {
    'axes.labelsize': 12,
    'font.size': 12,
    'legend.fontsize': 11,
    'legend.loc': 'right',
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'text.usetex': False,
    'figure.figsize': [6.5, 4.5]
    }
mpl.rcParams.update(params)


size = 20
# rect = (min_row, min_col, max_row, max_col)
rectangles = [
        (0,9,1,12),
        (3,2,3,10),
        (2,16,8,18),
        (8,6,11,9),
        (7,1,13,2),
        (10,16,12,17),
        (16,1,18,4),
        (14,6,19,8),
        (16,11,18,14),
        (15,15,16,16)]

def create_initial_matrix():
    initial = [[0 for _ in range(size)] for _ in range(size)]
    for (min_row, min_col, max_row, max_col) in rectangles:
        for row in range(min_row, max_row+1):
            for col in range(min_col, max_col+1):
                initial[row][col] = 1
    return initial

def create_input_matrix(initial, p):
    matrix = [[x for x in row] for row in initial]
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            # We inverse the entry in the matrix with a probability p
            if random.uniform(0.0, 1.0) < p:
                matrix[row][col] = 1 - matrix[row][col]
    return matrix

def compute_true_positive(rois, initial):
    true_positive = 0
    all_positive = 0
    for (min_row, min_col, max_row, max_col) in rois:
        true_positive += sum([sum(x[min_col:(max_col+1)]) for x in initial[min_row:(max_row+1)]])
        all_positive += (max_row-min_row+1)*(max_col-min_col+1)
    return (true_positive, all_positive)

def prepare_popular_region_matrix(mip_matrix):
    nCols = len(mip_matrix[0])
    nRows = len(mip_matrix)
    # We assume a minimum support threshold of 0.05. We do not go beyond 30 for dense cells since
    # it is not likely and gives cell with a too high impact
    return [[random.randint(5,30) if mip_matrix[row][col] == 1 else random.randint(0,4) for col in range(nCols)] for row in range(nRows)]

def metrics_on_noise():
    initial = create_initial_matrix()
    total_dense = sum([sum(x) for x in initial])
    p_values = [x/100.0 for x in range(0,51)]

    recall_mip = list()
    precision_mip = list()

    recall_popular_region = list()
    precision_popular_region = list()

    nruns = 20
    for prob in p_values:
        rc_mip = 0
        pr_mip = 0
        rc_base = 0
        pr_base = 0
        for _ in range(nruns):
            input_matrix = create_input_matrix(initial, prob)
            # For this experiment we try to recover only rectangular regions
            mip_rois = mip_column.run(input_matrix, use_circle=False)['rois'][0]
            (true_positive, all_positive) = compute_true_positive(mip_rois, initial) 
            rc_mip += float(true_positive/total_dense)
            pr_mip += float(true_positive/all_positive)

        
            set_threshold(5)
            popular_region_matrix = prepare_popular_region_matrix(input_matrix)
            popular_region_rois = PopularRegion.run(popular_region_matrix)['rois']

            (true_positive, all_positive) = compute_true_positive(popular_region_rois, initial)
            rc_base += float(true_positive/total_dense)
            pr_base += float(true_positive/all_positive)

        recall_mip.append(rc_mip/nruns)
        precision_mip.append(pr_mip/nruns)

        recall_popular_region.append(rc_base/nruns)
        precision_popular_region.append(pr_base/nruns)
    
    plt.plot(p_values, recall_mip, linestyle=':', label='recall MIP')
    plt.plot(p_values, recall_popular_region, linestyle='--', label='recall PopularRegion')

    plt.plot(p_values, precision_mip, linestyle='-.', label='precision MIP')
    plt.plot(p_values, precision_popular_region, linestyle='-', label='precision PopularRegion')

    plt.xlabel('percentage of noise')
    plt.legend(bbox_to_anchor=(1.0,0.75))
    plt.savefig(os.path.join(get_figures_directory(), 'metrics-synthetic-exp.pdf'), bbox_inches='tight')
    plt.close()

