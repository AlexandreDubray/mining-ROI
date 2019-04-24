# -*- coding: utf-8 -*-

import time
from mip.candidate_generation.Utils import *

def compute_upper_bound(row, col, nRows, nCols):
    maxHeight = min(row, nRows - 1 - row)
    maxWidth = min(col, nCols - 1 - col)

    activeCellsUpperRow = get_actives_cells_rectangle(row+maxHeight, row+maxHeight, col - maxWidth, col+maxWidth)
    activeCellsLowerRow = get_actives_cells_rectangle(row-maxHeight, row-maxHeight, col - maxWidth, col+maxWidth)
    canReduce = (activeCellsUpperRow == 0 or activeCellsLowerRow == 0) and maxHeight > 0
    while canReduce:
        maxHeight -= 1
        activeCellsUpperRow = get_actives_cells_rectangle(row+maxHeight, row+maxHeight, col - maxWidth, col+maxWidth)
        activeCellsLowerRow = get_actives_cells_rectangle(row-maxHeight, row-maxHeight, col - maxWidth, col+maxWidth)
        canReduce = (activeCellsUpperRow == 0 or activeCellsLowerRow == 0) and maxHeight > 0

    activeCellRightCol = get_actives_cells_rectangle(row-maxHeight, row+maxHeight, col+maxWidth, col+maxWidth)
    activeCellLeftCol = get_actives_cells_rectangle(row-maxHeight, row+maxHeight, col-maxWidth, col-maxWidth)
    canReduce = (activeCellRightCol == 0 or activeCellLeftCol == 0) and maxWidth > 0

    while canReduce:
        maxWidth -= 1
        activeCellRightCol = get_actives_cells_rectangle(row-maxHeight, row+maxHeight, col+maxWidth, col+maxWidth)
        activeCellLeftCol = get_actives_cells_rectangle(row-maxHeight, row+maxHeight, col-maxWidth, col-maxWidth)
        canReduce = (activeCellRightCol == 0 or activeCellLeftCol == 0) and maxWidth > 0

    return (maxHeight, maxWidth)

def get_upper_bound_or_update(row, col, nRows, nCols, maps):
    if (row,col) not in maps:
        maps[(row, col)] = compute_upper_bound(row, col, nRows, nCols)
    return maps[(row,col)]


def max_rect_size_dense(matrix, dense_cell):
    nRows = len(matrix)
    nCols = len(matrix[0])

    cells_to_consider = set()

    map_cell_to_bound = {}
    min_size = {}

    for (row, col) in dense_cell:
        cells_to_consider.add((row, col))
        (maxHeight, maxWidth) = get_upper_bound_or_update(row, col, nRows, nCols, map_cell_to_bound)
        map_cell_to_bound[(row, col)] = (maxHeight, maxWidth)

        for next_row in range(row-maxHeight, row+maxHeight+1):
            for next_col in range(col-maxWidth, col+maxWidth+1):
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

opti_dense_considered = 0
def generate_center_one_cell_dense(matrix, min_size, cell_to_consider, map_cell_to_upbound, selected, explored):
    global opti_dense_considered
    nRows = len(matrix)
    nCols = len(matrix[0])
    for (row, col) in cell_to_consider:

        (minHeight, minWidth) = min_size[(row,col)]
        (maxHeight, maxWidth) = get_upper_bound_or_update(row, col, nRows, nCols, map_cell_to_upbound)

        for height in range(minHeight, maxHeight + 1):
            for width in range(minWidth, maxWidth + 1):
                opti_dense_considered += 1
                rect = (row-height, row+height, col-width, col+width)

                cells_in_col = rect[1]-rect[0]+1
                ones_first_col = get_actives_cells_rectangle(row-height, row+height, col-width, col-width)
                ones_last_col = get_actives_cells_rectangle(row-height, row+height, col+width, col+width)
                zeros_first_col = cells_in_col - ones_first_col
                zeros_last_col = cells_in_col - ones_last_col
                if 4+2*ones_first_col <= 2*zeros_first_col or 4+2*ones_last_col <= 2*zeros_last_col:
                    break

                if explored is not None:
                    explored.add(rect)
                w = weight_rectangle(rect)
                if w is not None:
                    selected.add(rect)

def generate_center_two_cell_horizontal_dense(matrix, min_size, cell_to_consider, map_cell_to_upbound, selected, explored):
    global opti_dense_considered
    nRows = len(matrix)
    nCols = len(matrix[0])
    for (row, col) in cell_to_consider:

        if (row, col+1) in cell_to_consider:

            (minHeight1, minWidth1) = min_size[(row, col)]
            (minHeight2, minWidth2) = min_size[(row, col)]
            (minHeight, minWidth) = (min(minHeight1, minHeight2), min(minWidth1, minWidth2))


            (maxHeight1, maxWidth1) = get_upper_bound_or_update(row, col, nRows, nCols, map_cell_to_upbound)
            (maxHeight2, maxWidth2) = get_upper_bound_or_update(row, col+1, nRows, nCols, map_cell_to_upbound)
            minWidthToBorder = min(col, nCols - 1 - (col+1))
            (maxHeight, maxWidth) = (max(maxHeight1, maxHeight2), min(minWidthToBorder, max(maxWidth1, maxWidth2)))

            for height in range(minHeight, maxHeight + 1):
                for width in range(minWidth, maxWidth + 1):
                    opti_dense_considered += 1
                    rect = (row-height, row+height, col-width, (col+1)+width)

                    cells_in_col = rect[1]-rect[0]+1
                    ones_first_col = get_actives_cells_rectangle(row-height, row+height, col-width, col-width)
                    ones_last_col = get_actives_cells_rectangle(row-height, row+height, col+1+width, col+1+width)
                    zeros_first_col = cells_in_col - ones_first_col
                    zeros_last_col = cells_in_col - ones_last_col
                    if 4+2*ones_first_col <= 2*zeros_first_col or 4+2*ones_last_col <= 2*zeros_last_col:
                        break

                    if explored is not None:
                        explored.add(rect)
                    w = weight_rectangle(rect)
                    if w is not None:
                        selected.add(rect)


def generate_center_two_cell_vertical_dense(matrix, min_size, cell_to_consider, map_cell_to_upbound, selected, explored):
    global opti_dense_considered
    nRows = len(matrix)
    nCols = len(matrix[0])
    for (row, col) in cell_to_consider:

        if (row+1, col) in cell_to_consider:

            (minHeight1, minWidth1) = min_size[(row,col)]
            (minHeight2, minWidth2) = min_size[(row+1,col)]
            (minHeight, minWidth) = (min(minHeight1,minHeight2), min(minWidth1,minWidth2))

            (maxHeight1, maxWidth1) = get_upper_bound_or_update(row, col, nRows, nCols, map_cell_to_upbound)
            (maxHeight2, maxWidth2) = get_upper_bound_or_update(row + 1, col, nRows, nCols, map_cell_to_upbound)
            minHeightToBorder = min(row, nRows-1-(row+1))
            (maxHeight, maxWidth) = (min(minHeightToBorder, max(maxHeight1, maxHeight2)), max(maxWidth1, maxWidth2))

            for height in range(minHeight, maxHeight + 1):
                for width in range(minWidth, maxWidth + 1):
                    opti_dense_considered += 1
                    rect = (row-height, (row+1)+height, col-width, col+width)

                    cells_in_col = rect[1]-rect[0]+1
                    ones_first_col = get_actives_cells_rectangle(row-height, row+1+height, col-width, col-width)
                    ones_last_col = get_actives_cells_rectangle(row-height, row+1+height, col+width, col+width)
                    zeros_first_col = cells_in_col - ones_first_col
                    zeros_last_col = cells_in_col - ones_last_col
                    if 4+2*ones_first_col <= 2*zeros_first_col or 4+2*ones_last_col <= 2*zeros_last_col:
                        break

                    if explored is not None:
                        explored.add(rect)
                    w = weight_rectangle(rect)
                    if w is not None:
                        selected.add(rect)

def generate_center_four_cell_dense(matrix, min_size, cell_to_consider, map_cell_to_upbound, selected, explored):
    global opti_dense_considered
    nRows = len(matrix)
    nCols = len(matrix[0])
    for (row, col) in cell_to_consider:

        if (row+1,col) in cell_to_consider and (row, col+1) in cell_to_consider and (row+1,col+1) in cell_to_consider:
            (minHeight1, minWidth1) = min_size[(row,col)]
            (minHeight2, minWidth2) = min_size[(row+1,col)]
            (minHeight3, minWidth3) = min_size[(row, col+1)]
            (minHeight4, minWidth4) = min_size[(row+1, col+1)]
            (minHeight, minWidth) = (min(minHeight1,minHeight2,minHeight3,minHeight4), min(minWidth1,minWidth2,minWidth3,minWidth4))

            (maxHeight1, maxWidth1) = get_upper_bound_or_update(row, col, nRows, nCols, map_cell_to_upbound)
            (maxHeight2, maxWidth2) = get_upper_bound_or_update(row +1, col , nRows, nCols, map_cell_to_upbound)
            (maxHeight3, maxWidth3) = get_upper_bound_or_update(row, col+1, nRows, nCols, map_cell_to_upbound)
            (maxHeight4, maxWidth4) = get_upper_bound_or_update(row + 1, col + 1, nRows, nCols, map_cell_to_upbound)
            minHeightToBorder = min(row, nRows-1-(row+1))
            minWidthToBorder = min(col, nCols - 1 - (col+1))
            maxHeight = max(min(minHeightToBorder, max(maxHeight1, maxHeight2)), min(minHeightToBorder, max(maxHeight3, maxHeight4)))
            maxWidth = max(min(minWidthToBorder, max(maxWidth1, maxWidth3)), min(minWidthToBorder, max(maxWidth2, maxWidth4)))

            for height in range(minHeight, maxHeight + 1):
                for width in range(minWidth, maxWidth + 1):
                    opti_dense_considered += 1
                    rect = (row-height, (row+1)+height, col-width, (col+1)+width)

                    cells_in_col = rect[1]-rect[0]+1
                    ones_first_col = get_actives_cells_rectangle(row-height, row+1+height, col-width, col-width)
                    ones_last_col = get_actives_cells_rectangle(row-height, row+1+height, col+1+width, col+1+width)
                    zeros_first_col = cells_in_col - ones_first_col
                    zeros_last_col = cells_in_col - ones_last_col
                    if 4+2*ones_first_col <= 2*zeros_first_col or 4+2*ones_last_col <= 2*zeros_last_col:
                        break

                    if explored is not None:
                        explored.add(rect)
                    w = weight_rectangle(rect)
                    if w is not None:
                        selected.add(rect)

def generate_rectangles_dense(matrix, explored=None):
    global opti_dense_considered
    opti_dense_considered = 0
    st = time.time()
    dense_cells = set()
    dense_id = 0
    for r in range(len(matrix)):
        for c in range(len(matrix[0])):
            if matrix[r][c] == 1:
                dense_cells.add((r,c))
    rect = set()

    (cell_to_see, maps, min_size) = max_rect_size_dense(matrix, dense_cells)
    generate_center_one_cell_dense(matrix, min_size, cell_to_see, maps, rect, explored)
    generate_center_two_cell_horizontal_dense(matrix, min_size, cell_to_see, maps, rect, explored)
    generate_center_two_cell_vertical_dense(matrix, min_size, cell_to_see, maps, rect, explored)
    generate_center_four_cell_dense(matrix, min_size, cell_to_see, maps, rect, explored)

    run_time = time.time() - st
    return (rect, opti_dense_considered, run_time)
