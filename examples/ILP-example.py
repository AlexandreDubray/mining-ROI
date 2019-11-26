#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from roi_miner.miner.grid_miner.MDL_optimizer import mine_rois

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

dataset = 'KaggleTaxis'
#dataset = 'MicrosoftTaxis'
grid_size = 100
density_threshold = 0.05


filename = dataset + '-' + str(grid_size) + '.in'
with open(os.path.join(SCRIPT_DIR, 'grids', filename),'r') as f:
    grid = list()
    for row in f.readlines():
        grid.append([int(x) for x in row.split(' ')])

if dataset == 'KaggleTaxis':
    threshold = 1667079*density_threshold #Number of traj in the dataset
else:
    # In the microsoft data set there are no trajectory
    threshold = max([max(x) for x in grid]) #Maximum density of the grid

rois = mine_rois(grid, threshold)
print(rois)
