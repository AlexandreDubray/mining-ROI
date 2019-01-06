#! /usr/bin/env python3

import sys

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from gurobipy import *


def visualize_matrix(matrix):
    ax = sns.heatmap(matrix)
    plt.show()

input_file = '../data/mip-matrix.tsv'
with open(input_file, 'r') as f:
    data = [[int(x) for x in line.split("\t")] for line in f.read().split("\n") if line != ""]
    maxX = -1
    minX = sys.maxsize
    maxY = -1
    minY = sys.maxsize
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i][j] == 1:
                maxX = max(maxX,j)
                minX = min(minX,j)
                maxY = max(maxY,i)
                minY = min(minY,i)
    K = 5

m = Model("model")

nRows = len(data)
row_idx = range(minX, maxX+1)

nCols = len(data[0])
col_idx = range(minY, maxY+1)

cell_idx = [(i,j) for i in row_idx for j in col_idx]
rect_idx = range(K)

rectangles = [(k,i) for k in rect_idx for i in range(4)]
rect = m.addVars(rectangles, lb=0, obj=0, vtype=GRB.INTEGER)
for i in range(K):
    for j in range(4):
        rect[i,j].BranchPriority = 1

all_dim = [(i,j,k) for i in  row_idx for j in col_idx for k in rect_idx]
s = m.addVars(all_dim, vtype=GRB.BINARY)
s1 = m.addVars(all_dim, vtype=GRB.BINARY)
s2 = m.addVars(all_dim, vtype=GRB.BINARY)
s3 = m.addVars(all_dim, vtype=GRB.BINARY)
s4 = m.addVars(all_dim, vtype=GRB.BINARY)

m.update()

# 0 <= x^1 <= x^2 <= N
m.addConstrs((minX <= rect[k,0] for k in rect_idx))
m.addConstrs((rect[k,0] <= rect[k,1] for k in rect_idx))
m.addConstrs((rect[k,1] <= maxX for k in rect_idx))

# 0 <= x^3 <= x^4 <= M
m.addConstrs((minY <= rect[k,2] for k in rect_idx))
m.addConstrs((rect[k,2] <= rect[k,3] for k in rect_idx))
m.addConstrs((rect[k,3] <= maxY for k in rect_idx))

# -Mx(1- s_{ijk}) + x^1_k <= i <= x^2_k + M_x (1 - s_{ijk})
M = len(data) # /!\ assuming data is square
m.addConstrs((-M*(1-s[i,j,k]) + rect[k,0] <= i for k in rect_idx for i in row_idx for j in col_idx))
m.addConstrs((M*(1-s[i,j,k]) + rect[k,1] >= i for k in rect_idx for i in row_idx for j in col_idx))

# -M_y(1 - s_{ijk} + x^3_k <= j <= x^4_k + M_y ( 1 - s_{ijk})
m.addConstrs((-M*(1-s[i,j,k]) + rect[k,2] <= j for k in rect_idx for i in row_idx for j in col_idx))
m.addConstrs((M*(1-s[i,j,k]) + rect[k,3] >= j for k in rect_idx for i in row_idx for j in col_idx))

m.addConstrs((i - rect[k,0] <= M*s1[i,j,k] - 1 for k in rect_idx for i in row_idx for j in col_idx))
m.addConstrs((rect[k,0] - i <= M*(1-s1[i,j,k]) for k in rect_idx for i in row_idx for j in col_idx))
m.addConstrs((rect[k,1] - i <= M*s2[i,j,k] -1 for k in rect_idx for i in row_idx for j in col_idx))
m.addConstrs((i - rect[k,1] <= M*(1- s2[i,j,k]) for k in rect_idx for i in row_idx for j in col_idx))

m.addConstrs((j - rect[k,2] <= M*s3[i,j,k] - 1 for k in rect_idx for i in row_idx for j in col_idx))
m.addConstrs((rect[k,2] - j <= M*(1-s3[i,j,k]) for k in rect_idx for i in row_idx for j in col_idx))
m.addConstrs((rect[k,3] - j <= M*s4[i,j,k]-1 for k in rect_idx for i in row_idx for j in col_idx))
m.addConstrs((j - rect[k,3] <= M*(1-s4[i,j,k]) for k in rect_idx for i in row_idx for j in col_idx))

m.addConstrs(( s[i,j,k] >= 1 - (4 - (s1[i,j,k] + s2[i,j,k] + s3[i,j,k] + s4[i,j,k])) for k in rect_idx for i in row_idx for j in col_idx))
m.addConstrs(( 4*s[i,j,k] <= s1[i,j,k] + s2[i,j,k] + s3[i,j,k] + s4[i,j,k] for k in rect_idx for i in row_idx for j in col_idx))

# deactivate this constraint if we want to allow the rectangles to overlap
m.addConstrs(( s.sum(i,j, '*') <= 1 for i in row_idx for j in col_idx))

# variable + constraint to model objctive function
print("Modeling objectivve function")
n = m.addVars(cell_idx, vtype=GRB.BINARY, obj=0)
m.update()

m.addConstrs((s[i,j,k] <= 1 - n[i,j] for k in rect_idx for i in row_idx for j in col_idx))

# n_ij <= sum_k s_{ijk}
m.addConstrs((1 - n[i,j] <= s.sum(i,j,'*') for i in row_idx for j in col_idx))

p = m.addVars(cell_idx, vtype=GRB.BINARY, obj=1)
m.update()

m.addConstrs((2*p[i,j] <= data[i][j] + n[i,j] for i in row_idx for j in col_idx))
m.addConstrs((data[i][j] + n[i,j] <= p[i,j] + 1 for i in row_idx for j in col_idx))

b = m.addVars(all_dim, vtype=GRB.BINARY, obj=1)
m.update()

m.addConstrs((2*b[i,j,k] <= (1-data[i][j]) + s[i,j,k] for k in rect_idx for i in row_idx for j in col_idx))
m.addConstrs(((1-data[i][j]) + s[i,j,k] <= b[i,j,k] + 1 for k in rect_idx for i in row_idx for j in col_idx))

#set parameters
#m.Params.NodeMethod = 2 # Set method to barrier
m.Params.MIPFocus = 2 # Set focus on optimality, not feasability

m.optimize()

print('Optimal objective: %g' % m.objVal)
for k in rect_idx:
    print("{}-th rectangles:".format(k))
    for i in range(4):
        print(rect[k,i])

