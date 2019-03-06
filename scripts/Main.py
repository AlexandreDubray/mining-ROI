#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import shutil

from visualization.visu_map import generate_all_visu

from mip.Utils import get_mip_output_filenames
from mip.mip_column import run
from baseline.Utils import get_baseline_output_filenames

import shared.Constant
from shared.Utils import parse_data

from results_analysis import run_analysis, time_analysis
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find ROI using MIP and baseline approach')
    parser.add_argument('--clean', help='Clean all the data file', action='store_true', default=False)
    args = parser.parse_args()
    if args.clean:
        clean()
    create_env()
    main()
