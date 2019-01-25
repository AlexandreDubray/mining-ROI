#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, math

from mip.select_best import run_mdl
from mip.Utils import get_initial_mip_data, get_gurobi_output_file

from baseline.Greedy import run as run_baseline, get_data

import numpy as np
import matplotlib.pyplot as plt

from shared.Constant import percentage_threshold, side_size, grid_size
from shared.Utils import map_cell_to_id

def safe_mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

def graph_rectangles_error():
    (data, N) = get_initial_mip_data()

    with get_gurobi_output_file() as f:
        all_rectangles = [ [(int(x), int(y), int(z), int(t)) for x,y,z,t in [ss.split(" ") for ss in solution.split('\n')[1:-1]] ] for solution in f.read().split('\n\n') if solution != ""]
        mip_errors = [total_error_rectangles(rectangles,data, N) for rectangles in all_rectangles]

def create_directories_threshold(threshold):
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    data_directory = os.path.join(SCRIPT_DIR, '..', 'data')
    tr_dir = os.path.join(data_directory, str(threshold))
    safe_mkdir(tr_dir)
    safe_mkdir(os.path.join(tr_dir, 'output'))

def run_algos():
    global percentage_threshold
    threshold_range = range(1,31)
    for tr in threshold_range:
        percentage_threshold = tr
        create_directories_threshold(percentage_threshold)
        run_mdl()
        run_baseline()

def get_nb_dense_for_tr(filepath):
    total_number_dense = 0
    with open(filepath, 'r') as f:
        initial_mip_data = [[int(x) for x in line.split("\t")] for line in f.read().split("\n") if line != ""]
        for row in range(len(initial_mip_data)):
            for col in range(len(initial_mip_data[row])):
                if initial_mip_data[row][col] == 1:
                    total_number_dense += 1
    return total_number_dense

def plot_graph_threshold_error():
    threshold_range = range(5,31)
    error_mip = []
    error_baseline = []

    script_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')

    for tr in threshold_range:
        res_dir = os.path.join(data_dir, str(tr))


        nb_dense = get_nb_dense_for_tr(os.path.join(res_dir, 'mip-matrix.tsv'))

        with open(os.path.join(res_dir, 'output', 'mip.out'), 'r') as f:
            total_mip_dense_covered = 0
            total_mip_nondense_covered = 0
            for line in f.readlines():
                split = line.split(' ')
                (dense, nondense) = (int(split[-2]),int(split[-1]))
                total_mip_dense_covered += dense
                total_mip_nondense_covered += nondense

            total_error_mip = (nb_dense - total_mip_dense_covered) + total_mip_nondense_covered
            error_mip.append( ((total_error_mip)*100)/grid_size)

        rect_base = list()
        with open(os.path.join(res_dir, 'output', 'baseline.out'), 'r') as f:
            total_base_dense_covered = 0
            total_base_nondense_covered = 0
            for line in f.readlines():
                split = line.split(' ')
                (dense, nondense) = (int(split[-2]), int(split[-1]))
                total_base_dense_covered += dense
                total_base_nondense_covered += nondense

            total_error_baseline = (nb_dense - total_base_dense_covered) + total_base_nondense_covered
            error_baseline.append( (total_error_baseline*100)/grid_size)
    
    plt.plot(threshold_range, error_mip, label='mip')
    plt.plot(threshold_range, error_baseline, label='baseline')
    plt.xlabel('Minimum support threshold (% of total number of trajectories)')
    plt.ylabel('Percentage of error')
    plt.legend()
    plt.show()

def plot_graph_mdl():
    
    threshold_range = range(5,31)
    length_mip = []
    length_baseline = []

    script_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')

    for tr in threshold_range:
        res_dir = os.path.join(data_dir, str(tr))
        nb_dense = get_nb_dense_for_tr(os.path.join(res_dir, 'mip-matrix.tsv'))

        with open(os.path.join(res_dir, 'output', 'mip.out'), 'r') as f:
            total_mip_dense_covered = 0
            total_mip_nondense_covered = 0
            total_length_mip = 0
            for line in f.readlines():
                split = line.split(' ')
                (type_roi, dense, nondense) = (split[0], int(split[-2]), int(split[-1]))
                if type_roi == 'rectangle':
                    total_length_mip += 4 # Need 4 int to store a rectangle. ATM we do not care about 1 cell rectangles which need 2 int
                elif type_roi == 'circle':
                    total_length_mip += 3 # Need 3 integer to store a circle

                total_mip_dense_covered += dense
                total_mip_nondense_covered += nondense

            total_error_mip = (nb_dense - total_mip_dense_covered) + total_mip_nondense_covered
            # We need to retain (row,cell) for errored cells (2 int)
            length_mip.append(total_error_mip*2 + total_length_mip)

        with open(os.path.join(res_dir, 'output', 'baseline.out'), 'r') as f:
            total_base_dense_covered = 0
            total_base_nondense_covered = 0
            total_length_baseline = 0
            for line in f.readlines():
                split = line.split(' ')
                (dense, nondense) = (int(split[-2]), int(split[-1]))
                total_base_dense_covered += dense
                total_base_nondense_covered += nondense
                total_length_baseline += 4 # They only find rectangular regions

            total_error_baseline = (nb_dense - total_base_dense_covered) + total_base_nondense_covered
            length_baseline.append(total_error_baseline*2 + total_length_baseline)
    
    plt.plot(threshold_range, length_mip, label='mip')
    plt.plot(threshold_range, length_baseline, label='baseline')
    plt.xlabel('Minimum support threshold (% of total number of trajectories)')
    plt.ylabel('Number of integer needed to encode the solution')
    plt.legend()
    plt.show()


def plot_convexity_mdl():
    #threshold_range = range(5,31)
    threshold_range = (10,15,20)

    curves = list()

    script_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')

    for tr in threshold_range:
        res_dir = os.path.join(data_dir, str(tr))
        gurobi_file = os.path.join(res_dir, 'gurobi.out')

        total_nb_dense = get_nb_dense_for_tr(os.path.join(res_dir, 'mip-matrix.tsv'))

        curve = list()
        with open(gurobi_file, 'r') as f:
            solutions = f.read().split('\n\n')[:-1]
            for solution in solutions:
                rois = solution.split('\n')[1:]
                nb_dense = 0
                nb_nondense = 0
                length_model = 0
                for roi in rois:
                    split = roi.split(' ')
                    (type_roi, dense, nondense) = (split[0], int(split[-2]), int(split[-1]))
                    if type_roi == 'rectangle':
                        length_model += 4
                    elif type_roi == 'circle':
                        length_model += 3
                    nb_dense += dense
                    nb_nondense += nondense
                total_length = length_model + ((total_nb_dense - nb_dense)+nb_nondense)*2
                curve.append(total_length)
            curves.append(curve)

    for curve in curves:
        plt.plot(curve)
    plt.xlabel('Number of ROI')
    plt.ylabel('Length of the model')
    plt.show()



def run_analysis():
    #run_algos()
    plot_graph_threshold_error()
    plot_graph_mdl()
    #plot_convexity_mdl()
