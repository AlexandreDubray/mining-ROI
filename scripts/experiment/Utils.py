# -*- coding: utf-8 -*-

import os
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_figures_directory():
    directory_path = os.path.join(SCRIPT_DIR, 'figures')
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)
    return directory_path

def print_rect(data, rect):
    (min_row, min_col, max_row,max_col) = rect
    for r in range(min_row, max_row+1):
        print(' '.join([str(x) for x in data[r][min_col:(max_col+1)]]))

# Small utility function to more readable large number
def print_number(number):
    print(split_number(str(number)))

def split_number(number):
    if len(number) <= 3:
        return number
    return split_number(number[:-3]) + " " + number[-3:]

def split_int(number):
    return split_number(str(number))
