#! /usr/bin/env python3

from gurobipy import *

import sys
import os

from mip import Utils
from shared.Utils import print_flush

data = None
number_supported = 0

constraint_matrix = None

roi_candidates = None
rectangles_ids_range = [None, None]
circles_ids_range = [None, None]
next_id = 0

def prepare_data():
    global data, constraint_matrix, number_supported
    number_supported = 0
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
                    number_supported += 1
        data = data[minRow:maxRow+1]
        # Reducing grid to strict minimum
        for i,d in enumerate(data):
            data[i] = d[minCol:maxCol+1]

    #for r in range(len(data)-1, -1, -1):
    #    print(' '.join([str(x) for x in data[r]]))

    constraint_matrix = [[set() for col in range(len(data[0]))] for row in range(len(data))]

def weight_rectangle(xmin, xmax, ymin, ymax):
    global data
    # Uncomment for more balanced area
    if xmax - xmin + 1 > 2*(ymax-ymin+1) or ymax-ymin+1 > 2*(xmax - xmin+1):
        return None
    active = 0
    unactive = 0
    for col in range(xmin, xmax+1):
        for row in range(ymin, ymax+1):
            if data[row][col] == 1:
                active += 1
            else:
                unactive += 1
    if active == 0 or active < unactive:
        return None
    return (active, unactive)

def parse_rectangles():
    global data, constraint_matrix, roi_candidates, rectangles_ids_range
    if roi_candidates is None:
        roi_candidates = {}
    with Utils.get_mip_rectangles_file() as f:
        for line in f.readlines():
            [rid, xmin, xmax, ymin, ymax, dense, nondense] = [int(x) for x in line.split(" ")]
            if rectangles_ids_range[0] is None:
                rectangles_ids_range[0] = rid
            rectangles_ids_range[1] = rid
            roi_candidates[rid] = ((xmin, xmax, ymin, ymax), (dense, nondense))
            for col in range(xmin, xmax+1):
                for row in range(ymin, ymax+1):
                    constraint_matrix[row][col].add(rid)

def create_rectangles():
    global next_id
    with open(Utils.mip_rectangles_file(), "w") as f:
        for rowInf in range(len(data)):
            for rowSup in range(rowInf, len(data)):
                for colInf in range(len(data[0])):
                    for colSup in range(colInf, len(data[0])):
                        rect = (colInf, colSup, rowInf, rowSup)
                        w = weight_rectangle(colInf, colSup, rowInf, rowSup)
                        if w is not None:
                            f.write("{} {} {} {} {} {} {}\n".format(next_id, colInf, colSup, rowInf, rowSup, w[0], w[1]))
                            next_id += 1

def weight_circle(row, col, radius):
    global data
    dense = 0
    nondense =  0
    for r in range(0, radius + 1):
        for c in range(col - radius + r, col + radius + 1 - r):
            if data[row - r][c] == 1:
                dense += 1
            else:
                nondense += 1

            # Check because we need only to count once the middle line
            if r != 0:
                if data[row + r][c] == 1:
                    dense += 1
                else:
                    nondense += 1

    if dense == 0 or nondense > dense:
        return None
    return (dense, nondense)

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


def create_circles():
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

def idx_is_rectangle(idx):
    return idx >= rectangles_ids_range[0] and idx <= rectangles_ids_range[1]

def idx_is_circle(idx):
    return idx >= circles_ids_range[0] and idx <= circles_ids_range[1]

def compute_sol(K):
    m = Model("columns-gen-model")

    roi_cand_idx = range(len(roi_candidates))
    row_idx = range(len(data))
    col_idx = range(len(data[0]))

    candidates = m.addVars([k for k in roi_cand_idx], vtype=GRB.BINARY)

    # setting up the cost
    for k in roi_cand_idx:
        candidates[k].Obj = -(roi_candidates[k][1][0] - roi_candidates[k][1][1])

    m.update()

    for row in row_idx:
        for col in col_idx:
            if len(constraint_matrix[row][col]) != 0:
                m.addConstr(quicksum([candidates[idx] for idx in constraint_matrix[row][col]]) <= 1)

    m.addConstr(candidates.sum('*') <= K)

    m.optimize()
    
    with open(Utils.mip_gurobi_output_file(), "a") as f:
        f.write("{} {}\n".format(K, m.objVal))
        for k in roi_cand_idx:
            if candidates[k].X == 1:
                if idx_is_rectangle(k):
                    curr_rect = roi_candidates[k]
                    # colMin colMax rowMin rowMax
                    f.write("rectangle {} {} {} {} {} {}\n".format(curr_rect[0][0], curr_rect[0][1], curr_rect[0][2], curr_rect[0][3], curr_rect[1][0], curr_rect[1][1]))
                elif idx_is_circle(k):
                    curr_circ = roi_candidates[k]
                    f.write("circle {} {} {} {} {}\n".format(curr_circ[0][0], curr_circ[0][1], curr_circ[0][2], curr_circ[1][0], curr_circ[1][1]))
                else:
                    print("Unknown index in mip solution\n")
                    sys.exit(1)

        f.write("\n")

def run():
    prepare_data()
    parse_rectangles()
    parse_circles()
    for k in range(1,number_supported+1):
        compute_sol(k)
