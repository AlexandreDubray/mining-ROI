# -*- coding: utf-8 -*-

from mip.candidate_generation.generate_rectangles_dense import generate_rectangles_dense
from mip.Utils import get_mip_data

import sys

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def dist(c1, c2):
    return abs(c1[0]-c2[0]) + abs(c1[1]-c2[1])

def histogram_distance():
    data = get_mip_data()
    dense_cells = set()
    nRows = len(data)
    nCols = len(data[0])

    for row in range(nRows):
        for col in range(nCols):
            if data[row][col] == 1:
                dense_cells.add((row,col))

    distances = list()

    for c1 in dense_cells:
        minDist = sys.maxsize
        for c2 in dense_cells:
            if c1 != c2:
                d = dist(c1,c2)
                if d < minDist:
                    minDist = d
        distances.append(minDist)

    plt.hist(distances, rwidth=0.5, align='left')
    plt.title('Histogram of min distance between dense cells')
    plt.xlabel('Distance (in Manhattan value)')
    plt.show()

def histogram_distance_in_candidates():
    data = get_mip_data()
    (rects, _, _) = generate_rectangles_dense(data)
    distances = list()

    for (rmin, rmax, cmin, cmax) in rects:
        cells = set()
        for r in range(rmin, rmax+1):
            for c in range(cmin, cmax+1):
                if data[r][c] == 1:
                    cells.add((r,c))

        if len(cells) > 1:
            maxDist = -sys.maxsize
            for c1 in cells:
                for c2 in cells:
                    if c1 != c2:
                        d = dist(c1,c2)
                        if d > maxDist:
                            maxDist = d
            distances.append(maxDist)
    plt.hist(distances, rwidth=0.5, align='left')
    plt.title('Histogram of max distance between dense cells inside each candidates')
    plt.xlabel('Distance (in Manhattan value)')
    plt.show()

def cell_cover_by_candidates():
    data = get_mip_data()
    nRows = len(data)
    nCols = len(data[0])
    total_number_cells = nRows*nCols
    explored = set()
    (rects, _, _) = generate_rectangles_dense(data, explored)

    initial_dense = [[1 if data[row][col] == 1 else 0 for col in range(nCols)] for row in range(nRows)]
    coverage = [[ 0 for _ in range(nCols)] for _ in range(nRows)]
    cells_covered = set()
    for (rmin, rmax, cmin, cmax) in rects:

        for row in range(rmin, rmax+1):
            for col in range(cmin, cmax+1):
                coverage[row][col] = 1
                cells_covered.add((row, col))

    percentage_covered = float(100*(len(cells_covered)/total_number_cells))
    print("Cell covered %d out of %d (%.2f %%)" % (len(cells_covered), total_number_cells, percentage_covered))

    exploration = [[0 for _ in range(nCols)] for _ in range(nRows)]
    cell_explored = set()
    for (rmin, rmax, cmin, cmax) in explored:
        for row in range(rmin, rmax+1):
            for col in range(cmin, cmax+1):
                exploration[row][col] = 1
                cell_explored.add((row, col))

    percentage_explored = float(100*(len(cell_explored)/total_number_cells))
    print("Cell explored %d out of %d (%.2f %%)" % (len(cell_explored), total_number_cells, percentage_explored))


    fig, (ax1, ax2) = plt.subplots(1,2)
    sns.heatmap(initial_dense, ax=ax1)
    sns.heatmap(coverage, ax=ax2)
    #sns.heatmap(coverage, ax=ax1)
    #sns.heatmap(exploration, ax=ax2)
    plt.show()

def histogram_width_height():
    data = get_mip_data()
    nRows = len(data)
    nCols = len(data[0])

    (rects, _, _) = generate_rectangles_dense(data)
    heights = list()
    widths = list()
    ratio = list()

    for rect in rects:
        h = rect[1]-rect[0]+1
        w = rect[3]-rect[2]+1
        r = float(h/w) if w > h else float(w/h)
        heights.append(rect[1]-rect[0]+1)
        widths.append(rect[3]-rect[2]+1)

    bins = np.linspace(0,20, 20)

    plt.hist([heights, widths], bins=bins, label=['height', 'width'])
    plt.title('Histogram of the height width of candidates')
    plt.legend()
    plt.show()

def histogram_ratio():
    data = get_mip_data()
    nRows = len(data)
    nCols = len(data[0])

    (rects, _, _) = generate_rectangles_dense(data)
    ratio = list()

    for rect in rects:
        h = rect[1]-rect[0]+1
        w = rect[3]-rect[2]+1
        r = float(h/w) if w < h else float(w/h)
        ratio.append(r)

    plt.hist(ratio)
    plt.title('Histogram of the height width ratio of candidates')
    plt.legend()
    plt.show()


def run_analysis():
    #cell_cover_by_candidates()
    #histogram_distance_in_candidates()
    histogram_width_height()
    #histogram_ratio()
