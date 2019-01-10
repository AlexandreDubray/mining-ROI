#! /usr/bin/env python3

from gurobipy import *

import sys
import os

from mip import Utils

data = None
constraint_matrix = None
rectangles = None

def prepare_data():
    global data, constraint_matrix
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

    constraint_matrix = [[set() for col in range(len(data[0]))] for row in range(len(data))]

def weight(xmin, xmax, ymin, ymax, rect_id):
    global data, constraint_matrix
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
    return active - unactive

def parse_rectangles():
    global data, constraint_matrix, rectangles
    rectangles = {}
    with Utils.get_mip_rectangles_file() as f:
        for line in f.readlines():
            [rid, xmin, xmax, ymin, ymax, w] = [int(x) for x in line.split(" ")]
            rectangles[rid] = ((xmin, xmax, ymin, ymax), w)
            for col in range(xmin, xmax+1):
                for row in range(ymin, ymax+1):
                    constraint_matrix[row][col].add(rid)

def create_rectangles():
    next_id = 0
    with open(Utils.mip_rectangles_file, "w") as f:
        for rowInf in range(len(data)):
            for rowSup in range(rowInf, len(data)):
                for colInf in range(len(data[0])):
                    for colSup in range(colInf, len(data[0])):
                        rect = (colInf, colSup, rowInf, rowSup)
                        w = weight(colInf, colSup, rowInf, rowSup, next_id)
                        if w is not None:
                            f.write("{} {} {} {} {} {}\n".format(next_id, colInf, colSup, rowInf, rowSup, w))
                            next_id += 1

def compute_sol(K):
    if data is None:
        prepare_data()

    if rectangles is None:
        parse_rectangles()

    m = Model("columns-gen-model")

    rect_idx = range(len(rectangles))
    row_idx = range(len(data))
    col_idx = range(len(data[0]))

    r = [k for k in rect_idx]
    rects = m.addVars(r, vtype=GRB.BINARY)

    # setting up the cost
    print_flush("Setting up the costs")
    for k in rect_idx:
        rects[k].Obj = -rectangles[k][1]

    m.update()

    for row in row_idx:
        for col in col_idx:
            if len(constraint_matrix[row][col]) != 0:
                non_overlap_rects = constraint_matrix[row][col]
                m.addConstr(quicksum([rects[k] for k in non_overlap_rects]) <= 1)

    m.addConstr(rects.sum('*') <= K)

    m.optimize()
    
    with open(os.path.join(SCRIPT_DIR, '..', 'data','mip-sol.out'), "a") as f:
        f.write("{} {}\n".format(K, m.objVal))
        for k in rect_idx:
            if rects[k].X == 1:
                curr_rect = rectangles[k]
                f.write("{} {} {} {}\n".format(curr_rect[0][0], curr_rect[0][1], curr_rect[0][2], curr_rect[0][3]))
        f.write("\n")

def run():
    for k in range(1,):
        compute_sol(k)
