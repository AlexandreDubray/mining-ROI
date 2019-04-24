# -*- coding: utf-8 -*-

import time
from mip.candidate_generation.Utils import *

naive_considered = 0
def generate_center_one_cell_naive(matrix, selected):
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
                    rect = (row-height, row+height, col-width, col+width)
                    w = weight_rectangle(rect)
                    if w is not None:
                        selected.add(rect)

def generate_center_two_cell_horizontal_naive(matrix, selected):
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
                    rect = (row-height, row+height, col-width, (col+1)+width)
                    w = weight_rectangle(rect)
                    if w is not None:
                        selected.add(rect)

def generate_center_two_cell_vertical_naive(matrix, selected):
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
                    rect = (row-height, (row+1)+height, col-width, col+width)
                    w = weight_rectangle(rect)
                    if w is not None:
                        selected.add(rect)

def generate_center_four_cell_naive(matrix, selected):
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
                    rect = (row-height, (row+1)+height, col-width, (col+1)+width)
                    w = weight_rectangle(rect)
                    if w is not None:
                        selected.add(rect)

def generate_rectangles(matrix):
    global naive_considered
    naive_considered = 0
    st = time.time()
    selected = set()
    generate_center_one_cell_naive(matrix, selected)
    generate_center_two_cell_horizontal_naive(matrix, selected)
    generate_center_two_cell_vertical_naive(matrix, selected)
    generate_center_four_cell_naive(matrix, selected)
    naive_time = time.time() - st
    return (selected, naive_considered, naive_time)
