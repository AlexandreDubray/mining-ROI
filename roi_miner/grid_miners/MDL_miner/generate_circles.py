# -*- coding: utf8 -*-
from roi_miner.grid_miners.shapes.circle import Circle


def generate_circles(matrix, sum_entry_matrix):
    nRows = len(matrix)
    nCols = len(matrix[0])
    candidates = list()

    for row in range(nRows):
        for col in range(nCols):
            min_dist_row = min(row, nRows-1-row)
            min_dist_col = min(col, nCols-1-col)
            radius = min(min_dist_row, min_dist_col)
            # Circle of radius 0 will never be selected, since they
            # can cover at most 1 dense cells, and cos 3 integers
            for r in range(1, radius+1):
                circle = Circle(row, col, r, sum_entry_matrix)
                if circle.respect_constraints():
                    candidates.append(circle)
    return candidates
