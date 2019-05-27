# -*- coding: utf-8 -*-

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

def get_dense_cells_rectangle(rectangle, sum_entry_matrix):
    (min_row, min_col, max_row, max_col) = rectangle
    if max_row == len(sum_entry_matrix)-1:
        if min_col == 0:
            if min_row == 0:
                return sum_entry_matrix[max_row][max_col]
            else:
                return sum_entry_matrix[max_row][max_col] - sum_entry_matrix[min_row-1][max_col]
        else:
            if min_row == 0:
                return sum_entry_matrix[max_row][max_col] - sum_entry_matrix[max_row][min_col-1]
            else:
                return sum_entry_matrix[max_row][max_col] - sum_entry_matrix[max_row][min_col-1] - sum_entry_matrix[min_row-1][max_col] + sum_entry_matrix[min_row-1][min_col-1]
    else:
        if min_col == 0:
            if min_row == 0:
                return sum_entry_matrix[max_row][max_col]
            else:
                return sum_entry_matrix[max_row][max_col] - sum_entry_matrix[min_row-1][max_col]
        else:
            if min_row == 0:
                return sum_entry_matrix[max_row][max_col] - sum_entry_matrix[max_row][min_col-1]
            else:
                return sum_entry_matrix[max_row][max_col] - sum_entry_matrix[max_row][min_col-1] - sum_entry_matrix[min_row-1][max_col] + sum_entry_matrix[min_row-1][min_col-1]

def no_dense_cell(rectangle, sum_entry_matrix):
    return get_dense_cells_rectangle(rectangle, sum_entry_matrix) == 0

def number_cell_in_rectangle(rectangle):
    (min_row, min_col, max_row,max_col) = rectangle
    return (max_row-min_row+1)*(max_col-min_col+1)

def weight_rectangle(rectangle, sum_entry_matrix):
    assert(rectangle[0] <= rectangle[2])
    assert(rectangle[1] <= rectangle[3])
    dense = get_dense_cells_rectangle(rectangle, sum_entry_matrix)
    non_dense = number_cell_in_rectangle(rectangle) - dense
    if 4+2*dense <= 2*non_dense or dense <= non_dense:
        # Such rectangle are not usefull w.r.t. the MDL criterion
        return None
    return (dense, non_dense)

def compute_upper_bound(row, col, nRows, nCols, sum_entry_matrix):
    max_height = min(row, nRows - 1 - row)
    max_width = min(col, nCols - 1 - col)

    reduced = True
    while reduced and max_height > 0:
        reduced = False
        upper_rect = (row+max_height, col-max_width, row+max_height, col+max_width)
        lower_rect = (row-max_height, col-max_width, row-max_height, col+max_width)
        if no_dense_cell(upper_rect, sum_entry_matrix) or no_dense_cell(lower_rect, sum_entry_matrix):
            max_height -= 1
            reduced = True

    reduced = True
    while reduced and max_width > 0:
        left_rect = (row-max_height, col-max_width, row+max_height, col-max_width)
        right_rect = (row-max_height, col+max_width, row+max_height, col+max_width)
        reduced = False
        if no_dense_cell(left_rect, sum_entry_matrix) or no_dense_cell(right_rect, sum_entry_matrix):
            max_width -= 1
            reduced = True

    return (max_height, max_width)
