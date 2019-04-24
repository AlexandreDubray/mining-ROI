# -*- coding: utf-8 -*-

from mip.Utils import get_mip_data

from mip.candidate_generation.Utils import *

from mip.candidate_generation.generate_rectangles import generate_rectangles
from mip.candidate_generation.generate_rectangles_dense import generate_rectangles_dense
from mip.candidate_generation.generate_rectangles_opti import generate_rectangles_opti

from shared.Constant import set_side_size, set_percentage_threshold

def first_row_more_zeros(data, rect):
    ones = sum(data[rect[0]][rect[2]:(rect[3]+1)])
    zeros = (rect[3]-rect[2]+1) - ones
    return ones <= zeros

def last_row_more_zeros(data, rect):
    ones = sum(data[rect[1]][rect[2]:(rect[3]+1)])
    zeros = (rect[3]-rect[2]+1) - ones
    return ones <= zeros

def first_col_more_zeros(data, rect):
    ones = sum([ r[rect[2]] for r in data[rect[0]:(rect[1]+1)]])
    zeros = (rect[1]-rect[0]+1) - ones
    return ones <= zeros

def last_col_more_zeros(data, rect):
    ones = sum([ r[rect[3]] for r in data[rect[0]:(rect[1]+1)]])
    zeros = (rect[1]-rect[0]+1) - ones
    return ones <= zeros

def better_row_division(data, rect):
    nelem_per_col = rect[1] - rect[0] + 1
    single_one = 0
    error = 0
    possible_rect = 0
    curr_rect = False
    #print(rect)

    for col in range(rect[2], rect[3]+1):
        curr_col = [ data[row][col] for row in range(rect[0], rect[1]+1)]
        scol = sum(curr_col)

        if curr_rect:
            if scol < nelem_per_col - scol:
                # There is more 0's than 1's in the current col
                error += nelem_per_col - scol
                single_one += scol
                possible_rect += 1
                curr_rect = False
            elif col == rect[3]:
                error += nelem_per_col - scol
                possible_rect += 1
            else:
                error += nelem_per_col - scol

        else:
            if col != rect[3]:
                if scol == nelem_per_col:
                    # Full col of 1's
                    snext_col = sum([ data[row][col+1] for row in range(rect[0], rect[1]+1)]) 
                    if snext_col == nelem_per_col:
                        # next is also full of 1's => start new rectangle
                        curr_rect = True
                    elif snext_col >= nelem_per_col - snext_col:
                        # There is more (or equally) 1's than error in the next rectangle
                        curr_rect == True
                    elif nelem_per_col > 2:
                        # If more than 2 element per col, worth to take single rectangle with this col
                        possible_rect += 1
                    else:
                        error += nelem_per_col - scol
                        single_one += scol
                else:
                    error += nelem_per_col - scol
                    single_one += scol
            else:
                error += nelem_per_col - scol
                single_one += scol
    current_weight = 4 + error*2

    if possible_rect == 1 and single_one == 0:
        # Just the same rectangle
        return (False, current_weight)

    possible_weight = 4*possible_rect + single_one*2
    if possible_weight > current_weight:
        pass
        #print("Current weight : %d" % current_weight)
        #print("Possible rectangles : %d with %d one's to remember => %d weight" % (possible_rect, single_one, possible_weight))
    return (possible_weight <= current_weight, possible_weight)

def split_row(data, rect):
    weight = weight_rectangle(rect)
    current_weight = weight[0] - weight[1]
    assert(current_weight > 0)

    for row in range(rect[0], rect[1]):
        subrect1 = (rect[0], row, rect[2], rect[3])
        weight1 = weight_rectangle(subrect1)

        subrect2 = (row+1, rect[1], rect[2], rect[3])
        weight2 = weight_rectangle(subrect2)

        if weight1 is not None and weight2 is not None:
            if 8 + (weight1[0]-weight1[1]) + (weight2[0]-weight2[1]) <= current_weight:
                return True
        (better_div1, possible_weight1) = better_row_division(data, subrect1)
        (better_div2, possible_weight2) = better_row_division(data, subrect2)
        if possible_weight1 + possible_weight2 <= current_weight:
            return True
    return False

def better_col_division(data, rect):
    nelem_per_row = rect[3] - rect[2] + 1
    single_one = 0
    error = 0
    possible_rect = 0
    curr_rect = False
    for row in range(rect[0], rect[1]+1):
        curr_row = data[row][rect[2]:(rect[3]+1)]
        srow = sum(curr_row)
        if curr_rect:
            if srow < nelem_per_row - srow:
                # There is more 0's than 1's in the current col
                error += nelem_per_row - srow
                single_one += srow
                possible_rect += 1
                curr_rect = False
            elif row == rect[1]:
                error += nelem_per_row - srow
                possible_rect += 1
            else:
                error += nelem_per_row - srow
        else:
            if row != rect[1]:
                if srow == nelem_per_row:
                    snext_row = sum(data[row+1][rect[2]:(rect[3]+1)]) 
                    # Full row of 1's
                    if snext_row == nelem_per_row:
                        # next is also full of 1's => start new rectangle
                        curr_rect = True
                    elif snext_row >= nelem_per_row - snext_row:
                        # There is more 1's than 0's in the next row
                        curr_rect = True
                    elif nelem_per_row > 2:
                        # If more than 2 element per col, worth to take single rectangle with this col
                        possible_rect += 1
                    else:
                        error += nelem_per_row - srow
                        single_one += srow
                else:
                    error += nelem_per_row - srow
                    single_one += srow
            else:
                error += nelem_per_row - srow
                single_one += srow

    current_weight = 4 + error*2
    if possible_rect == 1 and single_one == 0:
        # Just the same rectangle
        return (False, current_weight)

    possible_weight = 4*possible_rect + single_one*2
    if possible_weight > current_weight:
        pass
        #print("Current weight : %d" % current_weight)
        #print("Possible rectangles : %d with %d one's to remember => %d weight" % (possible_rect, single_one, possible_weight))
    return (possible_weight <= current_weight, possible_weight)

def split_col(data, rect):
    weight = weight_rectangle(rect)
    current_weight = weight[0] - weight[1]
    assert(current_weight > 0)

    for col in range(rect[2], rect[3]):
        subrect1 = (rect[0], rect[1], rect[2], col)
        weight1 = weight_rectangle(subrect1)

        subrect2 = (rect[0], rect[1], col+1, rect[3])
        weight2 = weight_rectangle(subrect2)

        if weight1 is not None and weight2 is not None:
            if 8 + (weight1[0]-weight1[1]) + (weight2[0]-weight2[1]) <= current_weight:
                return True

        (better_div1, possible_weight1) = better_col_division(data, subrect1)
        (better_div2, possible_weight2) = better_col_division(data, subrect2)
        if possible_weight1 + possible_weight2 <= current_weight:
            return True
    return False

def remove_rows(data, rect):
    nbRows = rect[1]-rect[0]+1

    # do not remove all rows. Else we are in the case of nb_zeros > nb_ones which
    # can't happened because the rect would not be a valid candidate.
    for nb_row in range(1, nbRows):
        for srow in range(rect[0], rect[1]-nb_row+1):
            total_cells = nb_row*(rect[3]-rect[2]+1)
            nb_ones = get_actives_cells_rectangle(srow, srow+nb_row-1, rect[2], rect[3])
            nb_zeros = total_cells - nb_ones
            weight_new_rect = 4 if nb_row < (nbRows-1) else 0
            if weight_new_rect + 2*nb_ones <= 2 * nb_zeros:
                return True
    return False

def remove_cols(data, rect):
    nbCols = rect[3]-rect[2]+1

    # do not remove all cols. See comment in `remove_rows`
    for nb_col in range(1, nbCols):
        for scol in range(rect[2], rect[3]-nb_col+1):
            total_cells = (rect[1]-rect[0]+1)*nb_col
            nb_ones = get_actives_cells_rectangle(rect[0], rect[1], scol, scol+nb_col-1)
            nb_zeros = total_cells-nb_ones
            weight_new_rect = 4 if nb_col < (nbCols-1) else 0
            if weight_new_rect + 2*nb_ones <= 2*nb_zeros:
                return True
    return False

def print_unproved_rect(data,rect):
    show = False
    if show:
        print(rect)
        print_rect(data, rect)
        print("-------------------------")

def check_opti(data, rect_base, rect_opti):
    side_zeros = 0
    better_decomp = 0
    not_proved_better = 0
    for rect in rect_base:
        if rect not in rect_opti:
            if first_row_more_zeros(data, rect) or last_row_more_zeros(data, rect) or first_col_more_zeros(data, rect) or last_col_more_zeros(data, rect):
                side_zeros += 1

            elif (rect[1]-rect[0]+1) > (rect[3]-rect[2]+1):
                # More rows than column. Something like
                # x x x
                # x x x
                # x x x
                # x x x
                # x x x
                # x x x
                # x x x
                # x x x
                (better_div, _) = better_col_division(data,rect)
                if better_div:
                    better_decomp += 1
                elif split_col(data, rect):
                    better_decomp += 1
                elif remove_cols(data, rect):
                    better_decomp += 1
                else:
                    (better_div, _) = better_row_division(data, rect)
                    if better_div:
                        better_decomp += 1
                    elif split_row(data, rect):
                        better_decomp += 1
                    elif remove_rows(data, rect):
                        better_decomp += 1
                    else:
                        print_unproved_rect(data, rect)
                        not_proved_better += 1

            else:
                # more columns than row. Something like
                # x x x x x x x x x x x x x 
                # x x x x x x x x x x x x x 
                # x x x x x x x x x x x x x 
                (better_div, _) = better_row_division(data, rect)
                if better_div:
                    better_decomp += 1
                elif split_row(data, rect):
                    better_decomp += 1
                elif remove_rows(data, rect):
                    better_decomp += 1
                else:
                    (better_div, _) = better_col_division(data, rect)
                    if better_div:
                        better_decomp += 1
                    elif split_col(data, rect):
                        better_decomp += 1
                    elif remove_cols(data, rect):
                        better_decomp += 1
                    else:
                        print_unproved_rect(data, rect)
                        not_proved_better += 1
    print("The optimized code pruned %s rectangles from the set" % split_number(str(side_zeros + better_decomp + not_proved_better)))
    print("%s rectangles had a full side with more zeros than ones" % split_number(str(side_zeros)))
    print("%s rectangles have a better decomposition" % split_number(str(better_decomp)))
    print("%s rectangles must be checked by hand" % split_number(str(not_proved_better)))
    return (side_zeros, better_decomp, not_proved_better)

def run_set_comparaison(threshold):
    sizes = [100, 150, 200]
    latex_table =r"""
    \begin{table}[!h]
    \resizebox{\columnwidth}{!}{%
    \begin{tabular}{|l|l|l|l|l||l|l|l|l||l|l|l|l|}
    \hline
    """
    latex_table += r"""
    grid size          & \multicolumn{4}{c||}{100}                           & \multicolumn{4}{c||}{150}                           & \multicolumn{4}{c|}{200}                           \\ \hline
                       & Pruned & Side more zeros  & Better decomp. & Other       & Pruned & Side more zeros & Better decomp. & Other       & Pruned & Side more zeros & Better decomp. & Other       \\ \hline
    """
    latex_table += "\n"
    
    set_percentage_threshold(threshold)
    naive_output = {}
    for size in sizes:
        set_side_size(size)
        data = get_mip_data()
        reset_sum_entry_matrix()

        (naive_rects, _, _) = generate_rectangles(data)
        naive_output[size] = naive_rects

    bound_opti_string = "Bound optimization "

    for size in sizes:
        set_side_size(size)
        data = get_mip_data()
        reset_sum_entry_matrix()

        (bound_opti_rects, _, _) = generate_rectangles_opti(data)
        (side_zeros, better_decomp, other) = check_opti(data, naive_output[size], bound_opti_rects)
        bound_opti_string += "& %s & %s & %s & %s " % (split_int(side_zeros + better_decomp + other), split_int(side_zeros), split_int(better_decomp), split_int(other))
    bound_opti_string += r"\\ \hline"
    bound_opti_string += "\n"

    latex_table += bound_opti_string
    latex_table += "\n"

    dense_opti_string = "Dense optimization "
    for size in sizes:
        set_side_size(size)
        data = get_mip_data()
        reset_sum_entry_matrix()

        (dense_opti_rects, _, _) = generate_rectangles_dense(data)
        (side_zeros, better_decomp, other) = check_opti(data, naive_output[size], dense_opti_rects)
        dense_opti_string += "& %s & %s & %s & %s " % (split_int(side_zeros + better_decomp + other), split_int(side_zeros), split_int(better_decomp), split_int(other))
    dense_opti_string += r"\\ \hline"
    dense_opti_string += "\n"

    latex_table += dense_opti_string
    latex_table += "\n"

    latex_table += """
    \end{tabular}
    }
    """
    latex_table += """
    \caption{Candidates set comparison to the naive process for threshold %d \%%. 'Size more zeros' refere to a rectangle with more zeros than ones on one of its side. 
    'Better decomp.' refers to a rectangle where we could find a better decomposition.}
    """ % threshold
    latex_table += "\n"
    latex_table += "\end{table}"
    print(latex_table)


def run_time_comparaison(threshold):
    sizes = [100, 150,200]

    latex_table =r"""
    \begin{table}[!h]
    \resizebox{\columnwidth}{!}{%
    \begin{tabular}{|l|l|l|l||l|l|l||l|l|l|}
    \hline
    """
    latex_table += r"""
    grid size          & \multicolumn{3}{c||}{100}                           & \multicolumn{3}{c||}{150}                           & \multicolumn{3}{c|}{200}                           \\ \hline
                       & \multicolumn{1}{c|}{Explored} & Selected & Time(s) & \multicolumn{1}{c|}{Explored} & Selected & Time(s) & \multicolumn{1}{c|}{Explored} & Selected & Time(s) \\ \hline
    """

    set_percentage_threshold(threshold)

    naive_string = "Naive process "
    for size in sizes:
        set_side_size(size)
        data = get_mip_data()
        reset_sum_entry_matrix()

        (naive_rects, naive_considered, naive_time) = generate_rectangles(data)
        naive_string += "& %s & %s & %.2f " % (split_int(naive_considered), split_int(len(naive_rects)), naive_time)
    naive_string += r"\\ \hline"
    naive_string += "\n"
    latex_table += naive_string

    opti_string = "Bound optimization "
    for size in sizes:
        set_side_size(size)
        data = get_mip_data()
        reset_sum_entry_matrix()

        (opti_rects, opti_considered, opti_time) = generate_rectangles_opti(data)
        opti_string += "& %s & %s & %.2f " %(split_int(opti_considered), split_int(len(opti_rects)), opti_time)
    opti_string += r"\\ \hline"
    opti_string += "\n"
    latex_table += opti_string

    dense_string = "Dense optimization "
    for size in sizes:
        set_side_size(size)
        data = get_mip_data()
        reset_sum_entry_matrix()

        (dense_rects, dense_considered, dense_time) = generate_rectangles_dense(data)
        dense_string += "& %s & %s & %.2f " %(split_int(dense_considered), split_int(len(dense_rects)), dense_time)
    dense_string += r"\\ \hline"
    dense_string += "\n"
    latex_table += dense_string

    latex_table += r"""
    \end{tabular}
    }
    """
    latex_table += "\caption{Comparison of explored search space, with candidate selected, for threshold %d \%%}" % threshold
    latex_table += """
    \end{table}
    """
    print(latex_table)

def run_comparaison():
    run_time_comparaison(5)
    run_set_comparaison(5)

    run_time_comparaison(2)
    run_set_comparaison(2)

def run_generation():
    data = get_mip_data()
    (naive_rect, naive_considered, naive_time) = generate_rectangles(data)
    print("Base algorithm (brute force):")
    print("Considered :\t%s" % (split_number(str(naive_considered))))
    print("Selected :  \t%s" % (split_number(str(len(naive_rect)))))
    print("Time :      \t%.2f seconds" % (naive_time))
    (opti_rect, dense_considered, dense_time) = generate_rectangles_dense(data)
    print("Dense optimisation:")
    print("Considered :\t%s" % (split_number(str(dense_considered))))
    print("Selected :  \t%s" % (split_number(str(len(opti_rect)))))
    print("Time :      \t%.2f seconds" % (dense_time))
    #(opti_rect, _, _ ) = generate_rectangles_opti(data)
    _ = check_opti(data, naive_rect, opti_rect)

