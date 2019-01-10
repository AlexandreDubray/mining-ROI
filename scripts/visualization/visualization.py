#! /usr/env/bin python3

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import sys

sol_file = './mip-sol.out'
data_file = '../data/mip-matrix.tsv'

N = 0

with open(data_file, 'r') as f:
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
                N += 1

data = data[minY:maxY+1]
for i,d in enumerate(data):
    data[i] = d[minX:maxX+1]

out = [ [0 for i in range(len(data[0]))] for j in range(len(data))]

covered = 0
errored = 0

with open(sol_file, 'r') as f:
    for line in f.readlines():
        [xmin, xmax, ymin, ymax] = [int(x) for x in line.split(" ")]
        for col in range(xmin, xmax+1):
            for row in range(ymin, ymax+1):
                out[row][col] += 1
                if data[row][col] == 1:
                    covered += 1
                else:
                    errored += 1

print("Total number of cell to cover : {}".format(N))
print("error is {} + {} = {}".format(errored, (N - covered), errored + (N-covered)))

fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)
sns.heatmap(data, ax=ax1)
sns.heatmap(out, ax=ax2)
plt.show()
