#! /usr/bin/env python3

from gurobipy import *

import time

from mip.candidate_generation.generate_rectangles_dense import generate_rectangles_dense
from mip.candidate_generation.generate_rectangles_opti import generate_rectangles_opti
from mip.candidate_generation.generate_rectangles import generate_rectangles
from mip.candidate_generation.generate_circles import generate_circles

from mip.Utils import create_sum_entry_matrix

# TODO: find a better way to pass the candidates to the function
def compute_sol(data, candidates_rect, candidates_circle, map_candidates_to_weight):
    m = Model("mod")
    # Comment here to show gurobi output
    m.Params.OutputFlag = 0

    nCand = len(candidates_rect) + len(candidates_circle)

    candidates = m.addVars([k for k in range(nCand)], vtype=GRB.BINARY)

    for k in range(len(candidates_rect)):
        (dense_covered, non_dense_covered) = map_candidates_to_weight[candidates_rect[k]]
        candidates[k].Obj = 2*(non_dense_covered - dense_covered) + 4

    for k in range(len(candidates_circle)):
        (dense_covered, non_dense_covered) = map_candidates_to_weight[candidates_circle[k]]
        candidates[len(candidates_rect)+k].Obj = 2*(non_dense_covered - dense_covered) + 3

    m.update()

    # Creating constraint matrix
    constraint_matrix = [[set() for _ in range(len(data[0]))] for _ in range(len(data))]
    for (k, (min_row, min_col, max_row, max_col)) in enumerate(candidates_rect):
        for r in range(min_row, max_row+1):
            for c in range(min_col, max_col+1):
                constraint_matrix[r][c].add(k)

    for (k, (row, col, rad)) in enumerate(candidates_circle):
        idx = k + len(candidates_rect)
        for r in range(rad+1):
            for c in range(col - rad + r, col +rad + 1 - r):
                constraint_matrix[row - r][c].add(idx)
                constraint_matrix[row + r][c].add(idx)

    for row in range(len(data)):
        for col in range(len(data[0])):
            if len(constraint_matrix[row][col]) != 0:
                m.addConstr(quicksum([candidates[idx] for idx in constraint_matrix[row][col]]) <= 1)

    m.optimize()

    rect_opti = set()
    circ_opti = set()

    for v in candidates:
        if candidates[v].X == 1.0:
            if v < len(candidates_rect):
                rect_opti.add(candidates_rect[v])
            else:
                circ_opti.add(candidates_circle[v - len(candidates_rect)])
    return (rect_opti, circ_opti)

def run(data,use_circle=True, synth_rect=None):
    st = time.time()
    sum_entry_matrix = create_sum_entry_matrix(data)
    map_candidates_to_weight = {}
    if synth_rect is None:
        candi_rect = generate_rectangles(data, sum_entry_matrix, map_candidates_to_weight)
    else:
        candi_rect = synth_rect
    if use_circle:
        candi_circ = generate_circles(data, sum_entry_matrix, map_candidates_to_weight)
    else:
        candi_circ = list()
    creation_candidate_time = time.time() - st
    st = time.time()
    sol = compute_sol(data, candi_rect, candi_circ, map_candidates_to_weight) 
    opti_time = time.time() - st
    return {'rois': sol, 'time': (creation_candidate_time, opti_time)}

