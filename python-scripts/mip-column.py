#! /usr/bin/env python3

from gurobipy import *

import sys
import os

def print_flush(message):
    print(message)
    sys.stdout.flush()

print_flush("Parsing data")
input_file = './mip-matrix.tsv'
with open(input_file, 'r') as f:
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
    K = 224

constraint_matrix = [[list() for col in range(len(data[0]))] for row in range(len(data))]

def weight(xmin, xmax, ymin, ymax, rect_id):
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
    for col in range(xmin, xmax+1):
        for row in range(ymin, ymax+1):
            constraint_matrix[row][col].append(rect_id)
    return active - unactive

print_flush("Creating rectangles")
rectangles = {}
if not os.path.isfile('./rectangles.in'):
    next_id = 0
    with open("rectangles.in", "w") as f:
        for rowInf in range(len(data)):
            for rowSup in range(rowInf, len(data)):
                for colInf in range(len(data[0])):
                    for colSup in range(colInf, len(data[0])):
                        rect = (colInf, colSup, rowInf, rowSup)
                        w = weight(colInf, colSup, rowInf, rowSup, next_id)
                        if w is not None:
                            f.write("{} {} {} {} {} {}\n".format(next_id, colInf, colSup, rowInf, rowSup, w))
                            rectangles[next_id] = ((colInf, colSup, rowInf, rowSup), w)
                            next_id += 1
else:
    with open("rectangles.in", "r") as f:
        for line in f.readlines():
            [rid, xmin, xmax, ymin, ymax, w] = [int(x) for x in line.split(" ")]
            rectangles[rid] = ((xmin, xmax, ymin, ymax), w)
            for col in range(xmin, xmax+1):
                for row in range(ymin, ymax+1):
                    constraint_matrix[row][col].append(rid)

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
            non_overlap_rects = set(constraint_matrix[row][col])
            m.addConstr(quicksum([rects[k] for k in non_overlap_rects]) <= 1)

m.addConstr(rects.sum('*') <= K)

m.optimize()

with open("mip-sol.out", "w") as f:
    for k in rect_idx:
        if rects[k].X == 1:
            r = rectangles[k]
            f.write("{} {} {} {}\n".format(r[0][0], r[0][1], r[0][2], r[0][3]))

