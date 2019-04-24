#! /usr/bin/env python3

from gurobipy import *

import sys
import os
import time

from mip.candidate_generation.generate_rectangles_dense import generate_rectangles_dense
from mip import Utils

def prepare_data(use_synt_data, synt_data):
    if use_synt_data:
        if synt_data is None:
            print("Error: You forced the use of synthetic data but do not provide them.")
            sys.exit(1)
        data = synt_data
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
    return data

def compute_sol(data, use_synt_data, candidates_rect, candidates_circle):
    m = Model("columns-gen-model")
    # Comment here to show gurobi output
    m.Params.OutputFlag = 0

    nCand = len(candidates_rect) + len(candidates_circle)

    candidates = m.addVars([k for k in range(nCand)], vtype=GRB.BINARY)

    for k in range(len(candidates_rect)):
        cost = 2*(candidates_rectangle[k][1][1] - candidates_rectangle[k][1][0]) + 4
        candidates[k].Obj = cost

    for k in range(len(candidates_circle)):
        cost = 2*(candidates_circle[k][1][1] - candidates_circle[k][1][0]) + 3
        candidates[len(candidates_rect)+k].Obj = cost

    m.update()

    # Creating constraint matrix
    constraint_matrix = [[set() for _ in range(len(data[0]))] for _ in range(len(data))]
    for (k,(rect, _,)) in enumerate(candidates_rect):
        for r in range(rect[0], rect[1]+1):
            for c in range(rect[2], rect[3]+1):
                constraint_matrix[r][c].add(k)

    for (k, ((row,col,rad), _)) in enumerate(candidates_circle):
        idx = k + len(candidates_rectangle)
        for r in range(0, rad+1):
            for c in range(col - rad + r, col +rad + 1 - r):
                constraint_matrix[row - r][c].add(idx)
                constraint_matrix[row + r][c].add(idx)

    for row in range(len(data)):
        for col in range(len(data[0])):
            if len(constraint_matrix[row][col]) != 0:
                m.addConstr(quicksum([candidates[idx] for idx in constraint_matrix[row][col]]) <= 1)

    m.optimize()

    rect_opti = []
    circ_opti = []

    for (idx,v) in enumerate(candidates):
        if candidates[v].X == 1.0:
            if v < len(candidates_rectangles):
                rect_opti.append(candidates_rectangle[v])
            else:
                circ_opti.append(candidates_circle[v - len(candidates_rectangles)])
    return (rect_opti, circ_opti)

def run(use_synt_data=False, synt_data=None, use_circle=False, synth_rect=None):
    data = prepare_data(use_synt_data, synt_data)
    if synth_rect is None:
        candi_rect = generate_rectangles_dense(data)
    else:
        candi_rect = synth_rect
    # In the case we do not run experiment, we might want to store the ROIs in a file
    # to avoid creating them again. To do so uncomment this line and comment the one above
    #parse_rectangles()
    #if not use_synt_data and use_circle:
    if use_circle:
        candi_circ = create_circles()
        # Same here
        #parse_circles()
    else:
        candi_circ = list()

    (roi_rect, roi_circ) = compute_sol(data, use_synt_data, candi_rect, candi_circ)

