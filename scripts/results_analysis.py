#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, math

from mip.select_best import run_mdl
from mip.Utils import get_initial_mip_data, get_gurobi_output_file
from mip.mip_column import run as run_mip

from baseline.Greedy import run as run_baseline, get_data

import numpy as np
import matplotlib.pyplot as plt

from shared.Constant import get_percentage_threshold, set_percentage_threshold , set_side_size, side_size
from shared.Utils import parse_data

def safe_mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

def graph_rectangles_error():
    (data, N) = get_initial_mip_data()

    with get_gurobi_output_file() as f:
        all_rectangles = [ [(int(x), int(y), int(z), int(t)) for x,y,z,t in [ss.split(" ") for ss in solution.split('\n')[1:-1]] ] for solution in f.read().split('\n\n') if solution != ""]
        #mip_errors = [total_error_rectangles(rectangles,data, N) for rectangles in all_rectangles]

def create_directories_threshold(threshold):
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    data_directory = os.path.join(SCRIPT_DIR, '..', 'data')
    tr_dir = os.path.join(data_directory, str(threshold))
    safe_mkdir(tr_dir)
    safe_mkdir(os.path.join(tr_dir, 'output'))

def create_directories_time(size):
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    data_directory = os.path.join(SCRIPT_DIR, '..', 'data')
    d = os.path.join(data_directory, 'time')
    safe_mkdir(d)
    safe_mkdir(os.path.join(d, str(size)))

def run_algos():
    threshold_range = range(5,31)
    for tr in threshold_range:
        print("Threshold percentage : {}".format(str(tr)))
        set_percentage_threshold(tr)
        create_directories_threshold(get_percentage_threshold())
        run_mip()
        run_mip(use_circle=True)
        run_baseline()

def time_analysis():
    for size in [100, 150, 200]:
        for tr in [5,2]:
            create_directories_time(size)
            create_directories_threshold(tr)
            set_side_size(size)
            set_percentage_threshold(tr)
            parse_data()
            run_mip(use_circle=True)
            run_baseline()

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

def run_analysis():
    #run_algos()
    plot_graph_threshold_error()
    plot_graph_mdl()
    #plot_convexity_mdl()
