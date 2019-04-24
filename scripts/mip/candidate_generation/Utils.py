# -*- coding: utf-8 -*-

import mip

def print_rect(data, rect):
    for r in range(rect[0], rect[1]+1):
        print(' '.join([str(x) for x in data[r][rect[2]:(rect[3]+1)]]))

# Small utility function to more readable large number
def print_number(number):
    print(split_number(str(number)))

def split_number(number):
    if len(number) <= 3:
        return number
    return split_number(number[:-3]) + " " + number[-3:]

def split_int(number):
    return split_number(str(number))

sum_entry_matrix = None
def create_sum_entry_matrix():
    global sum_entry_matrix
    mip_data = mip.Utils.get_mip_data()
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

def get_sum_entry_matrix():
    if sum_entry_matrix is None:
        create_sum_entry_matrix()
    return sum_entry_matrix

def reset_sum_entry_matrix():
    global sum_entry_matrix
    create_sum_entry_matrix()


def get_actives_cells_rectangle(rmin, rmax, cmin, cmax):
    sum_entry_matrix = get_sum_entry_matrix()
    if rmax == len(sum_entry_matrix)-1:
        if cmin == 0:
            if rmin == 0:
                return sum_entry_matrix[rmax][cmax]
            else:
                return sum_entry_matrix[rmax][cmax] - sum_entry_matrix[rmin-1][cmax]
        else:
            if rmin == 0:
                return sum_entry_matrix[rmax][cmax] - sum_entry_matrix[rmax][cmin-1]
            else:
                return sum_entry_matrix[rmax][cmax] - sum_entry_matrix[rmax][cmin-1] - sum_entry_matrix[rmin-1][cmax] + sum_entry_matrix[rmin-1][cmin-1]
    else:
        if cmin == 0:
            if rmin == 0:
                return sum_entry_matrix[rmax][cmax]
            else:
                return sum_entry_matrix[rmax][cmax] - sum_entry_matrix[rmin-1][cmax]
        else:
            if rmin == 0:
                return sum_entry_matrix[rmax][cmax] - sum_entry_matrix[rmax][cmin-1]
            else:
                return sum_entry_matrix[rmax][cmax] - sum_entry_matrix[rmax][cmin-1] - sum_entry_matrix[rmin-1][cmax] + sum_entry_matrix[rmin-1][cmin-1]

def weight_rectangle(rectangle):
    assert(rectangle[0] <= rectangle[1])
    assert(rectangle[2] <= rectangle[3])
    # Uncomment for "balanced" rectangles"
    #if rmax - rmin + 1 > 2*(cmax - cmin + 1) or cmax - cmin + 1 > 2*(rmax - rmin + 1):
    #    return None
    actives = get_actives_cells_rectangle(rectangle[0], rectangle[1], rectangle[2], rectangle[3])
    unactives = (rectangle[1]-rectangle[0]+1)*(rectangle[3]-rectangle[2]+1) - actives
    if actives <= unactives:
        return None
    return (actives, unactives)

def neighbors(row, col, matrix):
    if row == 0:
        if col == 0:
            return [(row, col+1), (row+1, col)]
        elif col == len(matrix)-1:
            return [(row, col-1), (row+1, col)]
        else:
            return [(row, col-1), (row, col+1), (row+1, col)]
    elif row == len(matrix)-1:
        if col == 0:
            return [(row-1, col),(row, col+1)]
        elif col == len(matrix)-1:
            return [(row-1, col),(row, col-1)]
        else:
            return [(row, col-1), (row, col+1), (row-1, col)]
    else:
        if col == 0:
            return [(row+1, col), (row-1, col), (row,col+1)]
        elif col == len(matrix)-1:
            return [(row+1, col), (row-1, col), (row, col-1)]
        else:
            return [(row+1, col), (row-1, col), (row, col+1), (row, col-1)]
