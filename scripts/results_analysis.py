#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

from mip.select_best import run_mdl
from mip.Utils import get_initial_mip_data, get_gurobi_output_file
from mip.mip_column import run as run_mip

from baseline.Greedy import run as run_baseline

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


def run_analysis():
    #graph_rectangles_error()
    run_algos()
