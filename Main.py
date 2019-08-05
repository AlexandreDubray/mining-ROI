#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pickle

from miner.optimizer import run
from miner.dataset import Dataset

def main():
    # TODO: handle this with command line options
    script_dir = os.path.dirname(os.path.realpath(__file__))
    data_file = os.path.join(script_dir, 'KaggleTaxis.in')
    datasets_directory = os.path.join(script_dir, 'datasets')
    #dataset = Dataset(data_file, datasets_directory, 100, 0.05)
    with open(os.path.join(datasets_directory, 'KaggleTaxis-100-0.05.pkl'), 'rb') as f:
       dataset = pickle.load(f)

    matrix = dataset.get_data()
    mip_sol = run(matrix)
    dataset.solution = mip_sol
    dataset.save_dataset()
    print(dataset.solution)

if __name__ == '__main__':
    main()
