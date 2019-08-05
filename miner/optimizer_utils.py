# -*- coding: utf-8 -*-

import os
import sys

def create_sum_entry_matrix(mip_data):
    sum_entry_matrix = [[0 for _ in range(len(mip_data[0]))] for _ in range(len(mip_data))]
    for row in range(len(mip_data)):
        for col in range(len(mip_data[row])):
            if row == 0:
                if col == 0:
                    sum_entry_matrix[row][col] = mip_data[row][col]
                else:
                    sum_entry_matrix[row][col] = mip_data[row][col] + sum_entry_matrix[row][col-1]
            else:
                if col == 0:
                    sum_entry_matrix[row][col] = mip_data[row][col] + sum_entry_matrix[row-1][col]
                else:
                    sum_entry_matrix[row][col] = mip_data[row][col] + sum_entry_matrix[row-1][col] + sum_entry_matrix[row][col-1] - sum_entry_matrix[row-1][col-1]
    return sum_entry_matrix
