# -*- coding: utf-8 -*-
from roi_miner.grid_miners.MDL_miner.MDL_optimizer import mine_rois
from roi_miner.grid_miners.constraints import *

nb_trajectories = 1680000  # Roughly the number of trajectories we used in the Kaggle dataset
threshold = 0.05*nb_trajectories

# We load the density matrix
print("loading grid")
with open('./grids/KaggleTaxis-100.in', 'r') as f:
    density_grid = [[int(x) for x in line.rstrip().split(' ')] for line in f.readlines()]

# We add some constraints on the regions.
register_circle_constraint(circle_diameter_constraint, (0, 5,))
register_rectangle_constraint(rectangle_diameter_constraint, (0, 5,))
register_rectangle_constraint(rectangle_max_ratio_constraint, (2,))

rois = mine_rois(density_grid, threshold, min_distance_rois=2)

for roi in rois:
    print(roi)
