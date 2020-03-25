# -*- coding: utf-8 -*-
from roi_miner.grid_miners.MDL_miner.generate_circles import generate_circles
from roi_miner.grid_miners.MDL_miner.generate_rectangles import generate_rectangles

from roi_miner.optimizer import optimize


def _create_sum_area_matrix(matrix):
    nrows = len(matrix)
    ncols = len(matrix[0])
    sum_area = [[0 for _ in range(ncols)] for _ in range(nrows)]
    for row in range(nrows):
        for col in range(ncols):
            sum_area[row][col] = matrix[row][col] + (sum_area[row - 1][col] if row > 0 else 0) + (sum_area[row][col-1] if col > 0 else 0) - (sum_area[row-1][col-1] if col > 0 and row > 0 else 0)
    return sum_area


def _create_constraints(matrix, candidates):
    constraint_matrix = [[set() for _ in range(len(matrix[0]))] for _ in range(len(matrix))]

    for k, region in enumerate(candidates):
        for row, col in region:
            constraint_matrix[row][col].add(k)

    exclusive_contraints = list()

    for row in range(len(constraint_matrix)):
        for col in range(len(constraint_matrix[0])):
            s = constraint_matrix[row][col]
            if len(s) > 0:
                exclusive_contraints.append(s)
    return exclusive_contraints


def mine_rois(density_grid, density_threshold):
    nrows = len(density_grid)
    ncols = len(density_grid[0])
    binary_matrix = [[1 if density_grid[row][col] >= density_threshold else 0 for col in range(ncols)] for row in range(nrows)]
    sum_area = _create_sum_area_matrix(binary_matrix)

    rectangles = generate_rectangles(binary_matrix, sum_area)
    circles = generate_circles(binary_matrix, sum_area)

    candidates = rectangles + circles
    weights = [x.get_description_length() for x in candidates]
    constraints = _create_constraints(binary_matrix, candidates)

    rois = optimize(candidates, weights, constraints)
    return rois
