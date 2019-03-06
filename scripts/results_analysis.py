#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, math

from mip.select_best import run_mdl
from mip.Utils import get_initial_mip_data, get_gurobi_output_file
from mip.mip_column import run as run_mip

from baseline.Greedy import run as run_baseline, get_data

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mlp

# matplotlib settings
params = {
   'axes.labelsize': 12,
   'font.size': 12,
   'legend.fontsize': 12,
   'xtick.labelsize': 12,
   'ytick.labelsize': 12,
   'text.usetex': False,
   'figure.figsize': [6.5, 4.5]
   }
mlp.rcParams.update(params)

from shared.Constant import get_percentage_threshold, set_percentage_threshold , set_side_size, side_size
from shared.Utils import parse_data

script_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(script_dir, '..', 'data')

def safe_mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

def create_directories_threshold(threshold):
    tr_dir = os.path.join(data_dir, str(threshold))
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
    error_mip_full = []
    error_mip_rectangles = []
    error_baseline = []

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
            error_mip_full.append( ((total_error_mip)*100)/grid_size)

        with open(os.path.join(res_dir, 'output', 'mip-no-circle.out'), 'r') as f:
            total_mip_dense_covered = 0
            total_mip_nondense_covered = 0
            for line in f.readlines():
                split = line.split(' ')
                (dense, nondense) = (int(split[-2]),int(split[-1]))
                total_mip_dense_covered += dense
                total_mip_nondense_covered += nondense

            total_error_mip = (nb_dense - total_mip_dense_covered) + total_mip_nondense_covered
            error_mip_rectangles.append( ((total_error_mip)*100)/grid_size)

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
    
    plt.plot(threshold_range, error_mip_full, linestyle=':', linewidth=2, label='MIP')
    plt.plot(threshold_range, error_mip_rectangles, linestyle='--', linewidth=2, label='MIP-rectangles')
    plt.plot(threshold_range, error_baseline, linewidth=2, label='PopularRegion')
    plt.xlabel('Minimum density threshold (% of total number of trajectories)')
    plt.ylabel('Percentage of error')
    plt.legend()
    plt.savefig(os.path.join(data_dir, 'plots', 'error-rate.pdf'))
    plt.close()

def plot_graph_mdl():
    
    threshold_range = range(5,31)
    length_mip_full = []
    length_mip_rect = []
    length_baseline = []

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
            length_mip_full.append((total_error_mip*2, total_length_mip))

        with open(os.path.join(res_dir, 'output', 'mip-no-circle.out'), 'r') as f:
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
            length_mip_rect.append((total_error_mip*2, total_length_mip))

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
            length_baseline.append((total_error_baseline*2, total_length_baseline))


    error_mip_full = [x for x,_ in length_mip_full]
    error_mip_rect = [x for x,_ in length_mip_rect]
    error_baseline = [x for x,_ in length_baseline]
    print(error_mip_full)
    print(error_mip_rect)

    modlength_mip_full = [x for _,x in length_mip_full]
    modlength_mip_rect = [x for _,x in length_mip_rect]
    modlength_baseline = [x for _,x in length_baseline]
    print(modlength_mip_full)
    print(modlength_mip_rect)

    print([x+y for x,y in zip(error_mip_full, modlength_mip_full)])
    print([x+y for x,y in zip(error_mip_rect, modlength_mip_rect)])
    
    #print([x+y for x,y in zip(error_mip, modlength_mip)])

    #plt.plot(threshold_range, error_mip_full, linestyle=':', linewidth=2, label='Length error MIP')
    #plt.plot(threshold_range, error_mip_rect, linestyle=':', linewidth=2, label='Length error MIP rectangles')
    #plt.plot(threshold_range, error_baseline, linestyle=':', linewidth=2, label='Length error PopularRegion')

    plt.plot(threshold_range, modlength_mip_full, linestyle='--', linewidth=2, label='Length model MIP') 
    plt.plot(threshold_range, modlength_mip_rect, linestyle='--', linewidth=2, label='Length model MIP-rectangles') 
    plt.plot(threshold_range, modlength_baseline, linestyle='--', linewidth=2, label='Length model PopularRegion') 

    plt.xlabel('Minimum density threshold (% of total number of trajectories)')
    plt.ylabel('Number of integers')
    plt.legend(prop={'size': 12})

    plt.savefig(os.path.join(data_dir, 'plots', 'MDL.pdf'))
    plt.close()

def plot_runtime():
    global data_dir
    size_range = range(100,200)

    mip_ct = list()
    mip_rt = list()
    baseline_rt = list()

    base_dir = os.path.join(data_dir, 'time')

    for size in size_range:
        time_dir = os.path.join(base_dir, str(size))

        with open(os.path.join(time_dir, 'mip.out'), 'r') as f:
            lines = f.readlines()
            ct = 0.0
            rt = 0.0
            for i in range(0,40,2):
                print(float(lines[i]))
                ct += float(lines[i])
                rt += float(lines[i+1])
            mip_ct.append(ct/20.0)
            mip_rt.append(rt/20.0)

        with open(os.path.join(time_dir, 'baseline.out'), 'r') as f:
            lines = f.readlines()
            rt = 0.0
            for i in range(20):
                rt += float(lines[i])
            baseline_rt.append(rt/20.0)

    #plt.plot(size_range, mip_ct, label='MIP candidates creation')
    plt.plot(size_range, mip_rt, label='MIP solve optimization')
    plt.plot(size_range, baseline_rt, linestyle='--', label='PopularRegion')
    plt.xlabel('Size of the side of the grid')
    plt.ylabel('Runtime (in seconds)')
    plt.legend()
    plt.savefig(os.path.join(data_dir, 'plots', 'runtime.pdf'))
    plt.close()

def run_analysis():
    #run_algos()
    plot_graph_threshold_error()
    plot_graph_mdl()
    plot_runtime()
