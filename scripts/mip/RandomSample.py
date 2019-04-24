# -*- coding: utf-8 -*-

import random
random.seed(11781400)

from mip.candidate_generation.generate_rectangles_dense import generate_rectangles_dense
from mip.mip_column import run as run_mip

import matplotlib.pyplot as plt

def create_sample(data, dense_cells, niter):
    nRows = len(data)
    nCols = len(data[0])
    generated_candidates = set()
    for _ in range(niter):
        (row, col) = random.sample(dense_cells, 1)[0]
        rect = (row, row, col, col)
        w = weight_rectangle(rect)
        while w is not None:
            generated_candidates.add(r)

            next_rect = list()
            weights = list()

            if rect[0] > 0:
                next_rect.append((rect[0]-1, rect[1], rect[2], rect[3]))
                weights.append(get_actives_cells_rectangle(rect[0]-1, rect[1], rect[2], rect[3]))
            if rect[1] < nRows - 1:
                next_rect.append((rect[0], rect[1]+1, rect[2], rect[3]))
                weights.append(get_actives_cells_rectangle(rect[0], rect[1]+1, rect[2], rect[3]))
            if rect[2] > 0:
                next_rect.append((rect[0], rect[1], rect[2]-1, rect[3]))
                weights.append(get_actives_cells_rectangle(rect[0], rect[1], rect[2]-1, rect[3]))
            if rect[3] < nCols - 1:
                next_rect.append((rect[0], rect[1], rect[2], rect[3]+1))
                weights.append(get_actives_cells_rectangle(rect[0], rect[1], rect[2], rect[3]+1))

            rect = random.choices(next_rect, weights, k=1)[0]
            w = weight_rectangle(rect)
    return generated_candidates

def recall_precision(dense_cells, regions):
    nb_dense = len(dense_cells)
    nb_covered = 0
    found = 0
    for ((r1,r2,r3,r4),_) in regions:
        for r in range(r1, r2+1):
            for c in range(c1,c2+1):
                nb_covered += 1
                if (r,c) in dense_cells:
                    found += 1
    return (float(found/nb_dense), float(found/nb_covered))

def run_comparison(data):
    dense_cells = set()
    for r in range(len(data)):
        for c in range(len(data[0])):
            if data[r][c] == 1:
                dense_cells.add((r,c))

    (baseline_regions, _) = run_mip()
    (base_recall, base_preci) = recall_precision(dense_cells, baseline_regions)

    recalls = list()
    precisions = list()
    iter_range = list(range(1000, 11000, 1000))
    for niter in iter_range:
        sampled_regions = create_sample(data, dense_cells, niter)
        (regions, _) = run_mip(synth_rect=sampled_regions)
        (recall, precision) = recall_precision(dense_cells, regions)
        recalls.append(recall)
        precisions.append(precision)

    plt.plot(iter_range, recalls, label='Recall sample')
    plt.plot(iter_range, precisions, label='Precision sample')
    plt.axhline(y=baseline_recall, label='baseline recall')
    plt.axhline(y=baseline_precision, label='baseline precision')
    plt.show()
