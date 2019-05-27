# -*- coding: utf8 -*-

from mip.candidate_generation.Utils import *

def compute_weight_circle(row, col, radius, sum_entry_matrix):
    dense = 0
    non_dense = 0

    central_rect = (row,col-radius, row, col+radius)
    nb_cell = 2*radius + 1
    central_dense = get_dense_cells_rectangle(central_rect, sum_entry_matrix)
    dense += central_dense
    non_dense += nb_cell-central_dense

    for r in range(1, radius+1):
        upper_rect = (row+r, col-(radius-r), row+r, col+(radius-r))
        lower_rect = (row-r, col-(radius-r), row-r, col+(radius-r))

        nb_cell = upper_rect[3]-upper_rect[1]+1
        upper_dense = get_dense_cells_rectangle(upper_rect, sum_entry_matrix)
        lower_dense = get_dense_cells_rectangle(lower_rect, sum_entry_matrix)
        dense += upper_dense + lower_dense
        non_dense += (nb_cell-upper_dense) + (nb_cell-lower_dense)
    if 3 + 2*dense <= 2*non_dense or dense <= non_dense:
        return None
    return (dense,non_dense)

def generate_circles(matrix, sum_entry_matrix, map_candidates_to_weight):
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
                w = compute_weight_circle(row,col,r, sum_entry_matrix)
                if w is not None:
                    candidates.append((row,col,r))
                    map_candidates_to_weight[(row,col,r)] = w
    return candidates
