#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pickle
import argparse

from miner.optimizer import optimize
from miner.dataset import Dataset

def safe_mkdir(dirpath):
    try:
        os.makedirs(dirpath)
    except FileExistsError:
        pass

def check_instance_exists(dataset, side_size, density_threshold):
    influx = None
    for (side,threshold) in dataset.instances:
        instance = dataset.instances[(side,threshold)]
        if side == side_size and threshold == density_threshold:
            # If an instance already exists, ask if we must re-run the optimization
            answer = input('An instance for these parameters already exists. Re-run the optimization? [y/n] (default yes)').lower()
            if answer == '\n' or answer == 'y':
                matrix = instance['binary_matrix']
                solution = optimize(matrix)
            sys.exit(0)
        if side == side_size:
            # If there is an instance with the same size for the side, we do not need to
            # parse again the data set
            influx = dataset.instances[(side, threshold)]['influx']
    if influx is not None:
        dataset.create_instance(side_size, density_threshold, influx=influx)
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', help='Path to the data set file')
    parser.add_argument('size', help='Size of the side of the grid')
    parser.add_argument('threshold', help='Density threshold (percentage)')
    args = parser.parse_args()
    density_threshold = float(args.threshold)
    side_size = int(args.size)
    try:
        dataset_name = os.path.splitext(os.path.basename(args.dataset))[0]
        real_dataset_path = os.path.realpath(args.dataset)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        datasets_dir = os.path.join(script_dir, 'datasets')
        safe_mkdir(datasets_dir)
        with open(os.path.join(datasets_dir, dataset_name + '.pkl'), 'rb') as f:
            dataset = pickle.load(f)
    except FileNotFoundError:
        dataset = Dataset(real_dataset_path)
    if not check_instance_exists(dataset, side_size, density_threshold):
        dataset.create_instance(side_size, density_threshold)

    instance = dataset.instances[(side_size, density_threshold)]
    ROIs = optimize(instance['binary_matrix'])
    dataset.set_solution(side_size, density_threshold, ROIs)

