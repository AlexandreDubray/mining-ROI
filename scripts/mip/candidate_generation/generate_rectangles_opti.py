# -*- coding: utf-8 -*-

import sys
from mip.candidate_generation.Utils import *

def compute_lower_bound(row, col, upper_bound, sum_entry_matrix):
    (max_height, max_width) = upper_bound[row][col]
    (min_height, min_width) = (0,0)
    for delta_row in range(max_height+1):
        upper_rect = (row+delta_row, col-max_width, row+delta_row, col+max_width)
        lower_rect = (row-delta_row, col-max_width, row-delta_row, col+max_width)
        if no_dense_cell(upper_rect, sum_entry_matrix) and no_dense_cell(lower_rect, sum_entry_matrix):
            min_height += 1
        else:
            break
    for delta_col in range(max_width+1):
        left_rect = (row-max_height, col-delta_col, row+max_height, col-delta_col)
        right_rect = (row-max_height, col+delta_col, row+max_height, col+delta_col)
        if no_dense_cell(left_rect, sum_entry_matrix) and no_dense_cell(right_rect, sum_entry_matrix):
            min_width += 1
        else:
            break
    return (min_height, min_width)

def min_rect_size(matrix, upper_bound, sum_entry_matrix):
    nRows = len(matrix)
    nCols = len(matrix[0])

    dist_matrix = []
    for row in range(nRows):
        dist_matrix.append([])
        for col in range(nCols):
            dist_matrix[row].append(compute_lower_bound(row, col, upper_bound, sum_entry_matrix))
    return dist_matrix

def max_rect_size(matrix, sum_entry_matrix):
    nRows = len(matrix)
    nCols = len(matrix[0])

    dist_matrix = []
    for row in range(nRows):
        dist_matrix.append([])
        for col in range(nCols):
            dist_matrix[row].append(compute_upper_bound(row, col, nRows, nCols, sum_entry_matrix))
    return dist_matrix

def generate_center_one_cell(matrix, min_dist, max_dist, selected, sum_entry_matrix, map_candidates_to_weight):
    nRow = len(matrix)
    nCol = len(matrix[0])
    
    for row in range(nRow):
        for col in range(nCol):

            (min_height, min_width) = min_dist[row][col]
            (max_height, max_width) = max_dist[row][col]

            for height in range(min_height, max_height+1):
                for width in range(min_width, max_width+1):
                    rect = (row-height, col-width, row+height, col+width)

                    cells_in_col = rect[2]-rect[0]+1

                    first_col = (row-height, col-width, row+height, col-width)
                    ones_first_col = get_dense_cells_rectangle(first_col, sum_entry_matrix)
                    zeros_first_col = cells_in_col - ones_first_col

                    last_col = (row-height, col+width, row+height, col+width)
                    ones_last_col = get_dense_cells_rectangle(last_col, sum_entry_matrix)
                    zeros_last_col = cells_in_col - ones_last_col

                    if 4+2*ones_first_col <= 2*zeros_first_col or 4+2*ones_last_col <= 2*zeros_last_col:
                        break

                    w = weight_rectangle(rect, sum_entry_matrix)
                    if w is not None:
                        selected.append(rect)
                        map_candidates_to_weight[rect] = w

def generate_center_two_cell_horizontal(matrix, min_dist, max_dist, selected, sum_entry_matrix, map_candidates_to_weight):
    nRow = len(matrix)
    nCol = len(matrix[0])
    
    for row in range(nRow):
        for col in range(nCol-1):

            (min_height1, min_width1) = min_dist[row][col]
            (min_height2, min_width2) = min_dist[row][col+1]
            (min_height, min_width) = (min(min_height1, min_height2), min(min_width1, min_width2))

            (max_height1, max_width1) = max_dist[row][col]
            (max_height2, max_width2) = max_dist[row][col+1]
            min_widthToBorder = min(col, nCol - 1 - (col+1))
            (max_height, max_width) = (max(max_height1, max_height2), min(min_widthToBorder,max(max_width1, max_width2)))

            for height in range(min_height, max_height+1):
                for width in range(min_width, max_width+1):
                    rect = (row-height, col-width, row+height, (col+1)+width)

                    cells_in_col = rect[2]-rect[0]+1

                    first_col = (row-height, col-width, row+height, col-width)
                    ones_first_col = get_dense_cells_rectangle(first_col, sum_entry_matrix)
                    zeros_first_col = cells_in_col - ones_first_col

                    last_col = (row-height, (col+1)+width, row+height, (col+1)+width)
                    ones_last_col = get_dense_cells_rectangle(last_col, sum_entry_matrix)
                    zeros_last_col = cells_in_col - ones_last_col

                    if 4+2*ones_first_col <= 2*zeros_first_col or 4+2*ones_last_col <= 2*zeros_last_col:
                        break

                    w = weight_rectangle(rect, sum_entry_matrix)
                    if w is not None:
                        selected.append(rect)
                        map_candidates_to_weight[rect] = w

def generate_center_two_cell_vertical(matrix, min_dist, max_dist, selected, sum_entry_matrix, map_candidates_to_weight):
    nRow = len(matrix)
    nCol = len(matrix[0])
    
    for row in range(nRow-1):
        for col in range(nCol):

            (min_height1, min_width1) = min_dist[row][col]
            (min_height2, min_width2) = min_dist[row+1][col]
            (min_height, min_width) = (min(min_height1, min_height2), min(min_width1, min_width2))

            (max_height1, max_width1) = max_dist[row][col]
            (max_height2, max_width2) = max_dist[row+1][col]
            min_heightToBorder = min(row, nRow-1-(row+1))
            (max_height, max_width) = (min(min_heightToBorder, max(max_height1, max_height2)), max(max_width1, max_width2))


            for height in range(min_height, max_height+1):
                for width in range(min_width, max_width+1):
                    rect = (row-height, col-width, (row+1)+height, col+width)

                    cells_in_col = rect[2]-rect[0]+1

                    first_col = (row-height, col-width, (row+1)+height, col-width)
                    ones_first_col = get_dense_cells_rectangle(first_col, sum_entry_matrix)
                    zeros_first_col = cells_in_col - ones_first_col

                    last_col = (row-height, col+width, (row+1)+height, col+width)
                    ones_last_col = get_dense_cells_rectangle(last_col, sum_entry_matrix)
                    zeros_last_col = cells_in_col - ones_last_col

                    if 4+2*ones_first_col <= 2*zeros_first_col or 4+2*ones_last_col <= 2*zeros_last_col:
                        break

                    w = weight_rectangle(rect, sum_entry_matrix)
                    if w is not None:
                        selected.append(rect)
                        map_candidates_to_weight[rect] = w

def generate_center_four_cell(matrix, min_dist, max_dist, selected, sum_entry_matrix, map_candidates_to_weight):
    nRow = len(matrix)
    nCol = len(matrix[0])
    
    for row in range(nRow-1):
        for col in range(nCol-1):

            (min_height1, min_width1) = min_dist[row][col]
            (min_height2, min_width2) = min_dist[row][col+1]
            (min_height3, min_width3) = min_dist[row+1][col]
            (min_height4, min_width4) = min_dist[row+1][col+1]
            (min_height, min_width) = (min(min_height1, min_height3), min(min_width1, min_width2))

            (max_height1, max_width1) = max_dist[row][col]
            (max_height2, max_width2) = max_dist[row][col+1]
            (max_height3, max_width3) = max_dist[row+1][col]
            (max_height4, max_width4) = max_dist[row+1][col+1]
            min_widthToBorder = min(col, nCol-1-(col+1))
            min_heightToBorder = min(row, nRow-1-(row+1))
            max_height = max(min(min_heightToBorder, max(max_height1, max_height2)), min(min_heightToBorder, max(max_height3, max_height4)))
            max_width = max(min(min_widthToBorder, max(max_width1, max_width3)), min(min_widthToBorder, max(max_width2, max_width4)))

            for height in range(min_height, max_height+1):
                for width in range(min_width, max_width+1):
                    rect = (row-height, col-width, (row+1)+height, (col+1)+width)

                    cells_in_col = rect[2]-rect[0]+1

                    first_col = (row-height, col-width, (row+1)+height, col-width)
                    ones_first_col = get_dense_cells_rectangle(first_col, sum_entry_matrix)
                    zeros_first_col = cells_in_col - ones_first_col

                    last_col = (row-height, (col+1)+width, (row+1)+height, (col+1)+width)
                    ones_last_col = get_dense_cells_rectangle(last_col, sum_entry_matrix)
                    zeros_last_col = cells_in_col - ones_last_col

                    if 4+2*ones_first_col <= 2*zeros_first_col or 4+2*ones_last_col <= 2*zeros_last_col:
                        break

                    w = weight_rectangle(rect, sum_entry_matrix)
                    if w is not None:
                        selected.append(rect)
                        map_candidates_to_weight[rect] = w

def generate_rectangles_opti(matrix, sum_entry_matrix, map_candidates_to_weight):
    rect = list()
    max_dist = max_rect_size(matrix, sum_entry_matrix)
    min_dist = min_rect_size(matrix, max_dist, sum_entry_matrix)
    generate_center_one_cell(matrix, min_dist, max_dist, rect, sum_entry_matrix, map_candidates_to_weight)
    generate_center_two_cell_horizontal(matrix, min_dist, max_dist, rect, sum_entry_matrix, map_candidates_to_weight)
    generate_center_two_cell_vertical(matrix, min_dist, max_dist, rect, sum_entry_matrix, map_candidates_to_weight)
    generate_center_four_cell(matrix, min_dist, max_dist, rect, sum_entry_matrix, map_candidates_to_weight)
    return rect
