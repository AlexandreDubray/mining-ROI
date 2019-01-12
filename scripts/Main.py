#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse

from visualization.visu_map import visu_baseline, visu_mip, visu_initial, visu_mip_vs_baseline

from mip.Utils import get_mip_output_filenames
from baseline.Utils import get_baseline_output_filenames

import shared.Constant
    
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
data_directory = os.path.join(SCRIPT_DIR, '..', 'data')
output_directory = os.path.join(data_directory, 'output')
webapp_directory = os.path.join(SCRIPT_DIR, '..', 'webapp')

def safe_mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

def create_env():
    """ Create the necessary folder in order to run the code """
    safe_mkdir(data_directory)
    safe_mkdir(output_directory)
    safe_mkdir(webapp_directory)

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

def main():
    # Run the baseline algorithm and the visualization of the results
    #
    # Mip should not be runned by default since it needs an academic
    # connection to run gurobi
    visu_initial()
    visu_baseline()
    visu_mip()
    visu_mip_vs_baseline()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find ROI using MIP and baseline approach')
    parser.add_argument('--clean', help='Clean all the data file', action='store_true', default=False)
    args = parser.parse_args()
    if args.clean:
        clean()
    create_env()
    main()
