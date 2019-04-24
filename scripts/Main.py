#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import shutil

from visualization.visu_map import generate_all_visu

from mip.Utils import get_mip_output_filenames, get_mip_data
from mip.mip_column import run
from mip.RandomSample import run_comparison as run_random_sample

from mip.candidate_generation.rectangles_comparaison import run_comparaison, run_generation
from mip.candidate_generation.dense_cell_analysis import run_analysis
from mip.candidate_generation.MonteCarlo import run

from baseline.Utils import get_baseline_output_filenames

import shared.Constant
from shared.Constant import set_percentage_threshold, set_side_size
from shared.Utils import parse_data

from synthetic_exp import run_synthetic_experiment, matrix_fifteen, runtime_mip, runtime_baseline

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
data_directory = os.path.join(SCRIPT_DIR, '..', 'data')
output_directory = os.path.join(data_directory, 'output')
webapp_directory = os.path.join(SCRIPT_DIR, '..', 'webapp')
html_directory = os.path.join(data_directory, 'html')

def safe_mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

def create_env():
    """ Create the necessary folder in order to run the code """
    safe_mkdir(data_directory)
    safe_mkdir(os.path.join(data_directory, '5'))
    safe_mkdir(output_directory)
    safe_mkdir(webapp_directory)
    safe_mkdir(html_directory)
    parse_data()

def clean():
    # Cleaning file from MIP program
    for fpath in get_mip_output_filenames():
        try:
            os.remove(fpath)
        except FileNotFoundError:
            pass

    # Cleaning file from baseline
    for fpath in get_baseline_output_filenames():
        try:
            os.remove(fpath)
        except FileNotFoundError:
            pass

    for i in range(1,31):
        try:
            shutil.rmtree(os.path.join(data_directory, str(i)))
        except FileNotFoundError:
            pass

def main():
    #run_generation()
    #run_comparaison()
    #run_analysis()
    #run()
    data = get_mip_data()
    run_random_sample(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find ROI using MIP and baseline approach')
    parser.add_argument('--clean', help='Clean all the data file', action='store_true', default=False)
    args = parser.parse_args()
    if args.clean:
        clean()
    #create_env()
    main()
