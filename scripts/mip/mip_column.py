#! /usr/bin/env python3

from gurobipy import *

import sys
import os
import time

from mip import Utils
from shared.Utils import print_flush

data = None
sum_entry_matrix = None

constraint_matrix = None

roi_candidates = None
rectangles_ids_range = [None, None]
circles_ids_range = [None, None]
next_id = None

def compute_sum_entry():
    global sum_entry_matrix
    sum_entry_matrix = [[0 for _ in range(len(data[0]))] for _ in range(len(data))]
    for row in range(len(data)):
        for col in range(len(data[row])):
            if row == 0:
                if col == 0:
                    sum_entry_matrix[row][col] = data[row][col]
                else:
                    sum_entry_matrix[row][col] = data[row][col] + sum_entry_matrix[row][col-1]
            else:
                if col == 0:
                    sum_entry_matrix[row][col] = data[row][col] + sum_entry_matrix[row-1][col]
                else:
                    sum_entry_matrix[row][col] = data[row][col] + sum_entry_matrix[row-1][col] + sum_entry_matrix[row][col-1] - sum_entry_matrix[row-1][col-1]

def prepare_data(use_synt_data, synt_data):
    global data, constraint_matrix
    if use_synt_data:
        if synt_data is None:
            print("Error: You forced the use of synthetic data but do not provide them.")
            sys.exit(1)
        data = synt_data
        compute_sum_entry()
        constraint_matrix = [[set() for col in range(len(data[0]))] for row in range(len(data))]
    else:
        if synt_data is not None:
            print("Warning: You provided synthetic data but did not force to use it.")

        with Utils.get_mip_matrix_file() as f:
            data = [[int(x) for x in line.split("\t")] for line in f.read().split("\n") if line != ""]
            maxCol = -1
            minCol = sys.maxsize
            maxRow = -1
            minRow = sys.maxsize
            for col in range(len(data)):
                for row in range(len(data[0])):
                    if data[row][col] == 1:
                        maxCol = max(maxCol,col)
                        minCol = min(minCol,col)
                        maxRow = max(maxRow,row)
                        minRow = min(minRow,row)
            data = data[minRow:maxRow+1]
            # Reducing grid to strict minimum
            for i,d in enumerate(data):
                data[i] = d[minCol:maxCol+1]
            compute_sum_entry()
            constraint_matrix = [[set() for col in range(len(data[0]))] for row in range(len(data))]

def get_actives_cells_rectangle(rmin, rmax, cmin, cmax):
    global data, sum_entry_matrix
    if rmax == len(data)-1:
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

def weight_rectangle(rmin, rmax, cmin, cmax):
    # Uncomment for "balanced" rectangles"
    if rmax - rmin + 1 > 2*(cmax - cmin + 1) or cmax - cmin + 1 > 2*(rmax - rmin + 1):
        return None
    actives = get_actives_cells_rectangle(rmin, rmax, cmin, cmax)
    unactives = (rmax-rmin+1)*(cmax-cmin+1) - actives
    if actives < unactives:
        return None
    return (actives, unactives)

def parse_rectangles():
    global data, constraint_matrix, roi_candidates, rectangles_ids_range
    if roi_candidates is None:
        roi_candidates = {}
    with Utils.get_mip_rectangles_file() as f:
        for line in f.readlines():
            [rid, rowInf, rowSup, colInf, colSup, dense, nondense] = [int(x) for x in line.split(' ')]
            if rectangles_ids_range[0] is None:
                rectangles_ids_range[0] = rid
            rectangles_ids_range[1] = rid
            roi_candidates[rid] = ((rowInf, rowSup, colInf, colSup), (dense, nondense))
            for col in range(xmin, xmax+1):
                for row in range(ymin, ymax+1):
                    constraint_matrix[row][col].add(rid)

def create_and_store_rectangles():
    global next_id
    with open(Utils.mip_rectangles_file(), "w") as f:
        for rowInf in range(len(data)):
            for rowSup in range(rowInf, len(data)):
                for colInf in range(len(data[0])):
                    for colSup in range(colInf, len(data[0])):
                        rect = (colInf, colSup, rowInf, rowSup)
                        w = weight_rectangle(rowInf, rowSup, colInf, colSup)
                        if w is not None:
                            f.write("{} {} {} {} {} {} {}\n".format(next_id, rowInf, rowSup, colInf, colSup, w[0], w[1]))
                            next_id += 1

def create_rectangles():
    global next_id, constraint_matrix, roi_candidates, rectangles_ids_range
    rectangles_ids_range[0] = next_id

    if roi_candidates is None:
        roi_candidates = {}

    for rowInf in range(len(data)):
        for rowSup in range(rowInf, len(data)):
            for colInf in range(len(data[0])):
                for colSup in range(colInf, len(data[0])):

                    w = weight_rectangle(rowInf, rowSup, colInf, colSup)
                    if w is not None:
                        roi_candidates[next_id] = ((rowInf, rowSup, colInf, colSup), (w[0], w[1]))
                        for r in range(rowInf, rowSup+1):
                            for c in range(colInf, colSup+1):
                                constraint_matrix[r][c].add(next_id)
                        next_id += 1
    rectangles_ids_range[1] = next_id - 1


def weight_circle(row, col, radius):
    actives = 0
    unactives = 0
    # Upper part
    for r in range(1, radius+1):
        rmin = row+r
        rmax = row+r
        cmin = col-radius+r
        cmax = col+radius-r
        act = get_actives_cells_rectangle(rmin, rmax, cmin, cmax)
        actives += act
        unactives += (cmax-cmin+1) - act 

    # Lower part
    for r in range(1, radius+1):
        rmin = row-r
        rmax = row-r
        cmin = col-radius+r
        cmax = col+radius-r
        act = get_actives_cells_rectangle(rmin, rmax, cmin, cmax)
        actives += act
        unactives += (cmax-cmin+1) - act 

    # Middle part
    rmin = row
    rmax = row
    cmin = col-radius
    cmax = col+radius
    act = get_actives_cells_rectangle(rmin, rmax, cmin, cmax)
    actives += act
    unactives += (cmax-cmin+1) - act 

    if actives < unactives:
        return None
    return (actives, unactives)

def parse_circles():
    global data, constraint_matrix, roi_candidates, circles_ids_range
    if roi_candidates is None:
        roi_candidates = {}
    with Utils.get_mip_circles_file() as f:
        for line in f.readlines():
            [cid, row, col, radius, dense, nondense] = [int(x) for x in line.split(" ")]
            if circles_ids_range[0] is None:
                circles_ids_range[0] = cid
            circles_ids_range[1] = cid
            roi_candidates[cid] = ((row, col, radius), (dense, nondense))
            for r in range(0, radius + 1):
                for c in range(col - radius + r, col + radius + 1 - r):
                    # We can add without check because set only keep 1 times the same element
                    constraint_matrix[row - r][c].add(cid)
                    constraint_matrix[row + r][c].add(cid)


def create_and_store_circles():
    global next_id
    with open(Utils.mip_circles_file(), "w") as f:
        for row in range(len(data)):
            for col in range(len(data[row])):
                for radius in range(max(len(data), len(data[row]))):
                    # Circle center in (row, col) with radius radius
                    if row - radius < 0 or row + radius >= len(data):
                        break
                    if col - radius < 0 or col + radius >= len(data[row]):
                        break
                    w = weight_circle(row, col, radius)
                    if w is not None:
                        f.write("{} {} {} {} {} {}\n".format(next_id, row, col, radius, w[0], w[1]))
                        next_id += 1

def create_circles():
    global next_id, constraint_matrix, roi_candidates, circles_ids_range

    circles_ids_range[0] = next_id
    if roi_candidates is None:
        roi_candidates = {}

    for row in range(len(data)):
        for col in range(len(data[0])):
            for radius in range(max(len(data), len(data[row]))):
                # Circle center in (row, col) with radius radius
                if row - radius < 0 or row + radius >= len(data):
                    break
                if col - radius < 0 or col + radius >= len(data[row]):
                    break
                w = weight_circle(row, col, radius)
                if w is not None:
                    roi_candidates[next_id] = ((row, col, radius), (w[0],w[1]))
                    for r in range(0, radius+1):
                        for c in range(col-radius+r, col+radius+1-r):
                            constraint_matrix[row-r][c].add(next_id)
                            constraint_matrix[row+r][c].add(next_id)
                    next_id += 1
    circles_ids_range[1] = next_id - 1

def idx_is_rectangle(idx):
    return idx >= rectangles_ids_range[0] and idx <= rectangles_ids_range[1]

def idx_is_circle(idx):
    return idx >= circles_ids_range[0] and idx <= circles_ids_range[1]

def compute_sol(use_synt_data):
    m = Model("columns-gen-model")
    # Comment here to show gurobi output
    m.Params.OutputFlag = 0

    roi_cand_idx = range(len(roi_candidates))

    candidates = m.addVars([k for k in roi_cand_idx], vtype=GRB.BINARY)
    #candidates = m.addVars([k for k in roi_cand_idx])

    # setting up the cost
    for k in roi_cand_idx:
        cost = -2*(roi_candidates[k][1][0] - roi_candidates[k][1][1])
        if idx_is_rectangle(k):
            cost += 4
        elif idx_is_circle(k):
            cost += 3
        candidates[k].Obj = cost

    m.update()

    for row in range(len(data)):
        for col in range(len(data[0])):
            if len(constraint_matrix[row][col]) != 0:
                m.addConstr(quicksum([candidates[idx] for idx in constraint_matrix[row][col]]) <= 1)

    m.optimize()

    return [idx for idx,v in enumerate(candidates) if candidates[v].X == 1.0]

def parse_solution(candidates, use_synt_data, use_circle):
    if use_synt_data:
        return [roi_candidates[k] for k in candidates]
    else:
        with open(Utils.mip_output_file() if use_circle else Utils.mip_no_circle_output_file() , "w") as f:
            for k in candidates:
                if idx_is_rectangle(k):
                    curr_rect = roi_candidates[k]
                    # rowMin, rowMax, colMin, colMax
                    f.write("rectangle {} {} {} {} {} {}\n".format(curr_rect[0][0], curr_rect[0][1], curr_rect[0][2], curr_rect[0][3], curr_rect[1][0], curr_rect[1][1]))
                elif idx_is_circle(k):
                    curr_circ = roi_candidates[k]
                    f.write("circle {} {} {} {} {}\n".format(curr_circ[0][0], curr_circ[0][1], curr_circ[0][2], curr_circ[1][0], curr_circ[1][1]))
                else:
                    print("Unknown index in mip solution : {}".format(k))
                    print("Rectangles boundaries : {} {}".format(rectangles_ids_range[0], rectangles_ids_range[1]))
                    print("Circles boundaries : {} {}".format(circles_ids_range[0], circles_ids_range[1]))
                    sys.exit(1)

def clean_env():
    global next_id, circles_ids_range, rectangles_ids_range, roi_candidates

    next_id = 0
    circles_ids_range = [None, None]
    rectangles_ids_range = [None, None]
    roi_candidates = None

def run(use_synt_data=False, synt_data=None, use_circle=False):
    clean_env()
    prepare_data(use_synt_data, synt_data)
    start_time = time.time()
    create_rectangles()
    # In the case we do not run experiment, we might want to store the ROIs in a file
    # to avoid creating them again. To do so uncomment this line and comment the one above
    #parse_rectangles()
    #if not use_synt_data and use_circle:
    if use_circle:
        create_circles()
        # Same here
        #parse_circles()
    end_creation_time = time.time()
    sol = compute_sol(True if use_synt_data else False)
    end_time = time.time()

    #rois = parse_solution(sol, use_synt_data, use_circle)
    total_nb_dense = 0
    for d in data:
        total_nb_dense += sum(d)
    with open(Utils.mip_time_file(), 'a') as f:
        f.write('{}\n'.format(total_nb_dense))
        f.write('{}\n'.format(len(roi_candidates)))
        f.write('{}\n'.format(end_time - end_creation_time))
    #return (rois, end_creation_time - start_time, end_time - end_creation_time)

