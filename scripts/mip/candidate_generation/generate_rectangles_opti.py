# -*- coding: utf-8 -*-

import time
from mip.candidate_generation.Utils import *

def min_rect_size(matrix):
    nRows = len(matrix)
    nCols = len(matrix[0])
    row_dist = [0 for _ in range(nRows)]
    col_dist = [0 for _ in range(nCols)]

    for row in range(nRows):
        for delta_row in range(min(row, nRows-row-1)):
            uRow = row + delta_row
            if uRow < nRows:
                if get_actives_cells_rectangle(uRow,uRow,0,nCols-1) > 0:
                    row_dist[row] = delta_row
                    break
            lRow = row - delta_row
            if lRow > 0:
                if get_actives_cells_rectangle(lRow,lRow,0,nCols-1) > 0:
                    row_dist[row] = delta_row
                    break

    for col in range(nCols):
        for delta_col in range(min(col, nCols - col - 1)):
            uCol = col + delta_col
            if uCol < nCols:
                if get_actives_cells_rectangle(0, nRows-1, uCol, uCol) > 0:
                    col_dist[col] = delta_col
                    break

            lCol = col - delta_col
            if lCol > 0:
                if get_actives_cells_rectangle(0, nRows-1, lCol, lCol) > 0:
                    col_dist[col] = delta_col
                    break
    return (row_dist, col_dist)

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

def max_rect_size(matrix):
    nRows = len(matrix)
    nCols = len(matrix[0])

    dist_matrix = []
    for row in range(nRows):
        dist_matrix.append([])
        for col in range(nCols):
            dist_matrix[row].append(compute_upper_bound(row, col, nRows, nCols))
    return dist_matrix

opti_considered = 0
def generate_center_one_cell(matrix, min_row_dist, min_col_dist, max_dist, selected):
    global opti_considered 
    nRow = len(matrix)
    nCol = len(matrix[0])
    
    for row in range(nRow):
        for col in range(nCol):

            (minHeight, minWidth) = (min_row_dist[row], min_col_dist[col])
            (maxHeight, maxWidth) = max_dist[row][col]

            for height in range(minHeight, maxHeight+1):
                for width in range(minHeight, maxWidth+1):
                    opti_considered += 1
                    rect = (row-height, row+height, col-width, col+width)

                    if width > minWidth and width != maxWidth:
                        # No point in pruning the last element explored for this width
                        cells_in_col = rect[1]-rect[0]+1
                        ones_first_col = get_actives_cells_rectangle(row-height, row+height, col-width, col-width)
                        ones_last_col = get_actives_cells_rectangle(row-height, row+height, col+width, col+width)
                        zeros_first_col = cells_in_col - ones_first_col
                        zeros_last_col = cells_in_col - ones_last_col
                        if 4+2*ones_first_col <= 2*zeros_first_col or 4+2*ones_last_col <= 2*zeros_last_col:
                            break

                    w = weight_rectangle(rect)
                    if w is not None:
                        selected.add(rect)

def generate_center_two_cell_horizontal(matrix, min_row_dist, min_col_dist, max_dist, selected):
    global opti_considered
    nRow = len(matrix)
    nCol = len(matrix[0])
    
    for row in range(nRow):
        for col in range(nCol-1):

            (minHeight1, minWidth1) = (min_row_dist[row], min_col_dist[col])
            (minHeight2, minWidth2) = (min_row_dist[row], min_col_dist[col+1])
            (minHeight, minWidth) = (min(minHeight1, minHeight2), min(minWidth1, minWidth2))

            (maxHeight1, maxWidth1) = max_dist[row][col]
            (maxHeight2, maxWidth2) = max_dist[row][col+1]
            minWidthToBorder = min(col, nCol - 1 - (col+1))
            (maxHeight, maxWidth) = (max(maxHeight1, maxHeight2), min(minWidthToBorder,max(maxWidth1, maxWidth2)))

            for height in range(minHeight, maxHeight+1):
                for width in range(minWidth, maxWidth+1):
                    opti_considered += 1
                    rect = (row-height, row+height, col-width, col+1+width)

                    if width > minWidth and width != maxWidth:
                        # No point in pruning the last element explored for this width
                        cells_in_col = rect[1]-rect[0]+1
                        ones_first_col = get_actives_cells_rectangle(row-height, row+height, col-width, col-width)
                        ones_last_col = get_actives_cells_rectangle(row-height, row+height, col+1+width, col+1+width)
                        zeros_first_col = cells_in_col - ones_first_col
                        zeros_last_col = cells_in_col - ones_last_col
                        if 4+2*ones_first_col <= 2*zeros_first_col or 4+2*ones_last_col <= 2*zeros_last_col:
                            break

                    w = weight_rectangle(rect)
                    if w is not None:
                        selected.add(rect)

def generate_center_two_cell_vertical(matrix, min_row_dist, min_col_dist, max_dist, selected):
    global opti_considered
    nRow = len(matrix)
    nCol = len(matrix[0])
    
    for row in range(nRow-1):
        for col in range(nCol):

            (minHeight1, minWidth1) = (min_row_dist[row], min_col_dist[col])
            (minHeight2, minWidth2) = (min_row_dist[row+1], min_col_dist[col])
            (minHeight, minWidth) = (min(minHeight1, minHeight2), min(minWidth1, minWidth2))

            (maxHeight1, maxWidth1) = max_dist[row][col]
            (maxHeight2, maxWidth2) = max_dist[row+1][col]
            minHeightToBorder = min(row, nRow-1-(row+1))
            (maxHeight, maxWidth) = (min(minHeightToBorder, max(maxHeight1, maxHeight2)), max(maxWidth1, maxWidth2))

            for height in range(minHeight, maxHeight+1):
                for width in range(minWidth, maxWidth+1):
                    opti_considered += 1
                    rect = (row-height, (row+1)+height, col-width, col+width)

                    if width > minWidth and width != maxWidth:
                        # No point in pruning the last element explored for this width
                        cells_in_col = rect[1]-rect[0]+1
                        ones_first_col = get_actives_cells_rectangle(row-height, row+1+height, col-width, col-width)
                        ones_last_col = get_actives_cells_rectangle(row-height, row+1+height, col+width, col+width)
                        zeros_first_col = cells_in_col - ones_first_col
                        zeros_last_col = cells_in_col - ones_last_col
                        if 4+2*ones_first_col <= 2*zeros_first_col or 4+2*ones_last_col <= 2*zeros_last_col:
                            break

                    w = weight_rectangle(rect)
                    if w is not None:
                        selected.add(rect)

def generate_center_four_cell(matrix, min_row_dist, min_col_dist, max_dist, selected):
    global opti_considered
    nRow = len(matrix)
    nCol = len(matrix[0])
    
    for row in range(nRow-1):
        for col in range(nCol-1):

            (minHeight1, minWidth1) = (min_row_dist[row], min_col_dist[col])
            minWidth2 =  min_col_dist[col+1]
            minHeight3 = min_col_dist[col]
            # minHeight1 == minHeight2 and minHeight3 == minHeight 4(same row)
            # minWidth1 == minWidth3 and minWidth2 == minWidth4 (same col)
            (minHeight, minWidth) = (min(minHeight1, minHeight3), min(minWidth1, minWidth2))

            (maxHeight1, maxWidth1) = max_dist[row][col]
            (maxHeight2, maxWidth2) = max_dist[row][col+1]
            (maxHeight3, maxWidth3) = max_dist[row+1][col]
            (maxHeight4, maxWidth4) = max_dist[row+1][col+1]
            minWidthToBorder = min(col, nCol-1-(col+1))
            minHeightToBorder = min(row, nRow-1-(row+1))
            maxHeight = max(min(minHeightToBorder, max(maxHeight1, maxHeight2)), min(minHeightToBorder, max(maxHeight3, maxHeight4)))
            maxWidth = max(min(minWidthToBorder, max(maxWidth1, maxWidth3)), min(minWidthToBorder, max(maxWidth2, maxWidth4)))

            for height in range(minHeight, maxHeight+1):
                for width in range(minWidth, maxWidth+1):
                    opti_considered += 1
                    rect = (row-height, (row+1)+height, col-width, (col+1)+width)

                    if width > minWidth and width != maxWidth:
                        # No point in pruning the last element explored for this width
                        cells_in_col = rect[1]-rect[0]+1
                        ones_first_col = get_actives_cells_rectangle(row-height, row+1+height, col-width, col-width)
                        ones_last_col = get_actives_cells_rectangle(row-height, row+1+height, col+1+width, col+1+width)
                        zeros_first_col = cells_in_col - ones_first_col
                        zeros_last_col = cells_in_col - ones_last_col
                        if 4+2*ones_first_col <= 2*zeros_first_col or 4+2*ones_last_col <= 2*zeros_last_col:
                            break

                    w = weight_rectangle(rect)
                    if w is not None:
                        selected.add(rect)

def generate_rectangles_opti(matrix):
    global opti_considered
    opti_considered = 0
    st = time.time()
    rect = set()
    (min_row_dist, min_col_dist) = min_rect_size(matrix)
    max_dist = max_rect_size(matrix)
    generate_center_one_cell(matrix, min_row_dist, min_col_dist, max_dist, rect)
    generate_center_two_cell_horizontal(matrix, min_row_dist, min_col_dist, max_dist, rect)
    generate_center_two_cell_vertical(matrix, min_row_dist, min_col_dist, max_dist, rect)
    generate_center_four_cell(matrix, min_row_dist, min_col_dist, max_dist, rect)
    run_time = time.time() - st
    """
    print("Base optimisation:")
    print("Considered :\t%s" % (split_number(str(opti_considered))))
    print("Selected :  \t%s" % (split_number(str(len(rect)))))
    print("Time :      \t%.2f seconds" % (run_time))
    """
    return (rect, opti_considered, run_time)
