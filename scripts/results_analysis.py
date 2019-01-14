#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

from mip.select_best import total_error_rectangles, run_mdl
from mip.Utils import get_initial_mip_data, get_gurobi_output_file

from baseline.Greedy import run as run_baseline

import numpy as np
import matplotlib.pyplot as plt

from shared.Constant import percentage_threshold

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
        #run_mdl()
        run_baseline()

def run_analysis():
    #graph_rectangles_error()
    run_algos()
