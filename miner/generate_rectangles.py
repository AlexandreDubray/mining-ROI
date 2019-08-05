# -*- coding: utf-8 -*-
from miner.candidate_gen_utils import *

def get_upper_bound_or_update(row, col, nRows, nCols, maps, sum_entry_matrix):
    if (row,col) not in maps:
        maps[(row, col)] = compute_upper_bound(row, col, nRows, nCols, sum_entry_matrix)
    return maps[(row,col)]

def max_rect_size_dense(matrix, dense_cell, sum_entry_matrix):
    nRows = len(matrix)
    nCols = len(matrix[0])

    cells_to_consider = set()

    map_cell_to_bound = {}
    min_size = {}

    for (row, col) in dense_cell:
        cells_to_consider.add((row, col))
        (max_height, max_width) = get_upper_bound_or_update(row, col, nRows, nCols, map_cell_to_bound, sum_entry_matrix)
        map_cell_to_bound[(row, col)] = (max_height, max_width)

        for next_row in range(row-max_height, row+max_height+1):
            for next_col in range(col-max_width, col+max_width+1):
                dist = (abs(row-next_row), abs(col-next_col))
                if (next_row, next_col) not in min_size:
                    min_size[(next_row, next_col)] = dist
                else:
                    old_dist = min_size[(next_row, next_col)]
                    if dist[0] + dist[1] < old_dist[0] + old_dist[1]:
                    #elif dist[0] <= min_size[(next_row, next_col)][0] and dist[1] <= min_size[(next_row, next_col)][1]:
                        min_size[(next_row, next_col)] = dist
                    elif dist[0] + dist[1] == old_dist[0] + old_dist[1]:
                        min_size[(next_row, next_col)] = (min(dist[0], old_dist[0]), min(dist[1], old_dist[1]))
                cells_to_consider.add((next_row, next_col))
    return (cells_to_consider, map_cell_to_bound, min_size)

def generate_center_one_cell_dense(matrix, min_size, cell_to_consider, map_cell_to_upbound, selected, sum_entry_matrix, map_candidates_to_weight):
    nRows = len(matrix)
    nCols = len(matrix[0])
    for (row, col) in cell_to_consider:

        (min_height, min_width) = min_size[(row,col)]
        (max_height, max_width) = get_upper_bound_or_update(row, col, nRows, nCols, map_cell_to_upbound, sum_entry_matrix)

        for height in range(min_height, max_height + 1):
            for width in range(min_width, max_width + 1):
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

def generate_center_two_cell_horizontal_dense(matrix, min_size, cell_to_consider, map_cell_to_upbound, selected, sum_entry_matrix, map_candidates_to_weight):
    nRows = len(matrix)
    nCols = len(matrix[0])
    for (row, col) in cell_to_consider:

        if (row, col+1) in cell_to_consider:

            (min_height1, min_width1) = min_size[(row,col)]
            (min_height2, min_width2) = min_size[(row, col+1)]
            (min_height, min_width) = (min(min_height1, min_height2), min(min_width1, min_width2))


            (max_height1, max_width1) = get_upper_bound_or_update(row, col, nRows, nCols, map_cell_to_upbound, sum_entry_matrix)
            (max_height2, max_width2) = get_upper_bound_or_update(row, col+1, nRows, nCols, map_cell_to_upbound, sum_entry_matrix)
            min_widthToBorder = min(col, nCols - 1 - (col+1))
            (max_height, max_width) = (max(max_height1, max_height2), min(min_widthToBorder, max(max_width1, max_width2)))

            for height in range(min_height, max_height + 1):
                for width in range(min_width, max_width + 1):
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


def generate_center_two_cell_vertical_dense(matrix, min_size, cell_to_consider, map_cell_to_upbound, selected, sum_entry_matrix, map_candidates_to_weight):
    nRows = len(matrix)
    nCols = len(matrix[0])
    for (row, col) in cell_to_consider:

        if (row+1, col) in cell_to_consider:

            (min_height1, min_width1) = min_size[(row,col)]
            (min_height2, min_width2) = min_size[(row+1, col)]
            (min_height, min_width) = (min(min_height1,min_height2), min(min_width1,min_width2))

            (max_height1, max_width1) = get_upper_bound_or_update(row, col, nRows, nCols, map_cell_to_upbound, sum_entry_matrix)
            (max_height2, max_width2) = get_upper_bound_or_update(row + 1, col, nRows, nCols, map_cell_to_upbound, sum_entry_matrix)
            min_heightToBorder = min(row, nRows-1-(row+1))
            (max_height, max_width) = (min(min_heightToBorder, max(max_height1, max_height2)), max(max_width1, max_width2))

            for height in range(min_height, max_height + 1):
                for width in range(min_width, max_width + 1):
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

def generate_center_four_cell_dense(matrix, min_size, cell_to_consider, map_cell_to_upbound, selected, sum_entry_matrix, map_candidates_to_weight):
    nRows = len(matrix)
    nCols = len(matrix[0])
    for (row, col) in cell_to_consider:

        if (row+1,col) in cell_to_consider and (row, col+1) in cell_to_consider and (row+1,col+1) in cell_to_consider:
            (min_height1, min_width1) = min_size[(row,col)]
            (min_height2, min_width2) = min_size[(row+1,col)]
            (min_height3, min_width3) = min_size[(row,col+1)]
            (min_height4, min_width4) = min_size[(row+1,col+1)]
            (min_height, min_width) = (min(min_height1,min_height2,min_height3,min_height4), min(min_width1,min_width2,min_width3,min_width4))

            (max_height1, max_width1) = get_upper_bound_or_update(row, col, nRows, nCols, map_cell_to_upbound, sum_entry_matrix)
            (max_height2, max_width2) = get_upper_bound_or_update(row +1, col , nRows, nCols, map_cell_to_upbound, sum_entry_matrix)
            (max_height3, max_width3) = get_upper_bound_or_update(row, col+1, nRows, nCols, map_cell_to_upbound, sum_entry_matrix)
            (max_height4, max_width4) = get_upper_bound_or_update(row + 1, col + 1, nRows, nCols, map_cell_to_upbound, sum_entry_matrix)
            min_heightToBorder = min(row, nRows-1-(row+1))
            min_widthToBorder = min(col, nCols - 1 - (col+1))
            max_height = max(min(min_heightToBorder, max(max_height1, max_height2)), min(min_heightToBorder, max(max_height3, max_height4)))
            max_width = max(min(min_widthToBorder, max(max_width1, max_width3)), min(min_widthToBorder, max(max_width2, max_width4)))

            for height in range(min_height, max_height + 1):
                for width in range(min_width, max_width + 1):
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

def generate_rectangles(matrix, sum_entry_matrix, map_candidates_to_weight):
    dense_cells = set()
    for r in range(len(matrix)):
        for c in range(len(matrix[0])):
            if matrix[r][c] == 1:
                dense_cells.add((r,c))
    rect = list()

    (cell_to_see, maps, min_size) = max_rect_size_dense(matrix, dense_cells, sum_entry_matrix)
    generate_center_one_cell_dense(matrix, min_size, cell_to_see, maps, rect, sum_entry_matrix, map_candidates_to_weight)
    generate_center_two_cell_horizontal_dense(matrix, min_size, cell_to_see, maps, rect, sum_entry_matrix, map_candidates_to_weight)
    generate_center_two_cell_vertical_dense(matrix, min_size, cell_to_see, maps, rect, sum_entry_matrix, map_candidates_to_weight)
    generate_center_four_cell_dense(matrix, min_size, cell_to_see, maps, rect, sum_entry_matrix, map_candidates_to_weight)

    return rect
