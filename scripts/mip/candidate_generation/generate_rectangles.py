# -*- coding: utf-8 -*-

from mip.candidate_generation.Utils import *

naive_considered = 0
def generate_center_one_cell_naive(matrix, selected, map_candidates_to_weight, sum_entry_matrix):
    global naive_considered
    nRow = len(matrix)
    nCol = len(matrix[0])
    
    for row in range(nRow):
        for col in range(nCol):

            maxHeight = min(row, nRow - 1 - row)
            maxWidth = min(col, nCol - 1 - col)

            for height in range(maxHeight+1):
                for width in range(maxWidth+1):
                    naive_considered += 1
                    rect = (row-height, col-width, row+height, col+width)
                    w = weight_rectangle(rect, sum_entry_matrix)
                    if w is not None:
                        selected.append(rect)
                        map_candidates_to_weight[rect] = w

def generate_center_two_cell_horizontal_naive(matrix, selected, map_candidates_to_weight, sum_entry_matrix):
    global naive_considered
    nRow = len(matrix)
    nCol = len(matrix[0])
    
    for row in range(nRow):
        for col in range(nCol-1):

            maxHeight = min(row, nRow - 1 - row)
            maxWidth = min(col, nCol - 1 - (col + 1))

            for height in range(maxHeight+1):
                for width in range(maxWidth+1):
                    naive_considered += 1
                    rect = (row-height, col-width, row+height, (col+1)+width)
                    w = weight_rectangle(rect, sum_entry_matrix)
                    if w is not None:
                        selected.append(rect)
                        map_candidates_to_weight[rect] = w

def generate_center_two_cell_vertical_naive(matrix, selected, map_candidates_to_weight, sum_entry_matrix):
    global naive_considered
    nRow = len(matrix)
    nCol = len(matrix[0])
    
    for row in range(nRow-1):
        for col in range(nCol):

            maxHeight = min(row, nRow - 1 - (row+1))
            maxWidth = min(col, nCol - 1 - col)

            for height in range(maxHeight+1):
                for width in range(maxWidth+1):
                    naive_considered += 1
                    rect = (row-height, col-width, (row+1)+height, col+width)
                    w = weight_rectangle(rect, sum_entry_matrix)
                    if w is not None:
                        selected.append(rect)
                        map_candidates_to_weight[rect] = w

def generate_center_four_cell_naive(matrix, selected, map_candidates_to_weight, sum_entry_matrix):
    global naive_considered
    nRow = len(matrix)
    nCol = len(matrix[0])

    for row in range(nRow-1):
        for col in range(nCol-1):

            maxHeight = min(row, nRow - 1 - (row+1))
            maxWidth = min(col, nCol - 1 - (col+1))

            for height in range(maxHeight+1):
                for width in range(maxWidth+1):
                    naive_considered += 1
                    rect = (row-height, col-width, (row+1)+height, (col+1)+width)
                    w = weight_rectangle(rect, sum_entry_matrix)
                    if w is not None:
                        selected.append(rect)
                        map_candidates_to_weight[rect] = w

def generate_rectangles(matrix, sum_entry_matrix, map_candidates_to_weight):
    global naive_considered
    naive_considered = 0
    selected = list()
    generate_center_one_cell_naive(matrix, selected, map_candidates_to_weight, sum_entry_matrix)
    generate_center_two_cell_horizontal_naive(matrix, selected, map_candidates_to_weight, sum_entry_matrix)
    generate_center_two_cell_vertical_naive(matrix, selected, map_candidates_to_weight, sum_entry_matrix)
    generate_center_four_cell_naive(matrix, selected, map_candidates_to_weight, sum_entry_matrix)
    return selected
