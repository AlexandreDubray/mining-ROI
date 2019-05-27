# -*- coding: utf-8 -*-

import random
import os
import time
random.seed(11781400)

from mip.candidate_generation.generate_rectangles import generate_rectangles
from mip.candidate_generation.generate_rectangles_dense import generate_rectangles_dense
from mip.candidate_generation.Utils import weight_rectangle, get_dense_cells_rectangle
from mip import mip_column
from mip.Utils import get_mip_data,create_sum_entry_matrix

from experiment.Utils import get_figures_directory

import matplotlib.pyplot as plt
import matplotlib as mpl

params = {
    'axes.labelsize': 12,
    'font.size': 12,
    'legend.fontsize': 7,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'text.usetex': False,
    'figure.figsize': [6.5, 4.5]
    }
mpl.rcParams.update(params)

def create_sample(data, sum_entry_matrix, dense_cells, max_candi):
    nRows = len(data)
    nCols = len(data[0])
    generated_candidates = set()
    map_candidates_to_weight = {}
    while len(generated_candidates) < max_candi:
        (row, col) = random.sample(dense_cells, 1)[0]
        rect = (row, col, row, col)
        w = weight_rectangle(rect, sum_entry_matrix)
        while w is not None and len(generated_candidates) < max_candi:
            generated_candidates.add(rect)
            map_candidates_to_weight[rect] = w

            next_rect = list()
            weights = list()

            if rect[0] > 0:
                next_rect.append((rect[0]-1, rect[1], rect[2], rect[3]))
                weights.append(get_dense_cells_rectangle(next_rect[-1], sum_entry_matrix))
            if rect[2] < nRows - 1:
                next_rect.append((rect[0], rect[1], rect[2]+1, rect[3]))
                weights.append(get_dense_cells_rectangle(next_rect[-1], sum_entry_matrix))
            if rect[1] > 0:
                next_rect.append((rect[0], rect[1]-1, rect[2], rect[3]))
                weights.append(get_dense_cells_rectangle(next_rect[-1], sum_entry_matrix))
            if rect[3] < nCols - 1:
                next_rect.append((rect[0], rect[1], rect[2], rect[3]+1))
                weights.append(get_dense_cells_rectangle(next_rect[-1], sum_entry_matrix))

            rect = random.choices(next_rect, weights, k=1)[0]
            w = weight_rectangle(rect, sum_entry_matrix)
    return (generated_candidates, map_candidates_to_weight)

def recall_precision(data,dense_cells, regions):
    nb_dense = len(dense_cells)
    nb_covered = 0
    found = 0
    if len(regions) == 0:
        # Might be the case for low number of candidates
        return (0.0, 0.0)
    for (min_row, min_col, max_row, max_col) in regions:
        found += sum([sum(row[min_col:(max_col+1)]) for row in data[min_row:(max_row+1)]])
        nb_covered += (max_row-min_row+1)*(max_col-min_col+1)
    return (float(found/nb_dense), float(found/nb_covered))

def compute_objective(data, regions):
    nb_dense = sum([sum(data[r]) for r in range(len(data))])
    dense_covered = 0
    non_dense_covered = 0
    for (min_row, min_col, max_row, max_col) in regions:
        dense = sum([sum(data[row][min_col:(max_col+1)]) for row in range(min_row, max_row+1)])
        non_dense = (max_row-min_row+1)*(max_col-min_col+1) - dense
        dense_covered += dense
        non_dense_covered += non_dense
    return 4*len(regions) + 2*((nb_dense - dense_covered) + non_dense_covered)

def metrics_random_sample():
    mip_data = get_mip_data()
    dense_cells = set()
    for r in range(len(mip_data)):
        for c in range(len(mip_data[0])):
            if mip_data[r][c] == 1:
                dense_cells.add((r,c))

    sum_entry_matrix = create_sum_entry_matrix(mip_data)
    all_mip_candidates = generate_rectangles(mip_data, sum_entry_matrix, {})

    st = time.time()
    _ = generate_rectangles_dense(mip_data, sum_entry_matrix, {})
    generate_candi_time = time.time() - st

    # We only generate rectangular regions so we can only compare to rectangular optimum
    mip_sol = mip_column.run(mip_data, use_circle=False)
    mip_regions = mip_sol['rois'][0]
    (mip_recall, mip_preci) = recall_precision(mip_data,dense_cells, mip_regions)
    optimal_obj = compute_objective(mip_data, mip_regions)

    recalls = list()
    precisions = list()
    objectives = list()
    runtime = list()

    p_values = [x/100 for x in range(1,76)]

    for portion in p_values:
        target_number_candidates = int(len(all_mip_candidates)*portion)
        print("Target number candidates : {} ({} %)".format(target_number_candidates, portion))
        recall = 0
        precision = 0
        acc = 0
        obj = 0
        rt = 0
        nRuns = 20
        for _ in range(nRuns):
            st = time.time()
            (sampled_regions, map_to_weight) = create_sample(mip_data, sum_entry_matrix, dense_cells, target_number_candidates)
            rt += time.time() - st
            sampled_sol = mip_column.run(mip_data, use_circle=False, synth_rect=list(sampled_regions), synth_map_to_weight=map_to_weight)
            regions = sampled_sol['rois'][0]
            (rc, pr) = recall_precision(mip_data,dense_cells, regions)
            recall += rc
            precision += pr
            obj += compute_objective(mip_data, regions)
        recall = float(recall/nRuns)
        precision= float(precision/nRuns)
        acc = float(acc/nRuns)
        obj = float(obj/nRuns)
        rt = float(rt/nRuns)
        recalls.append(recall)
        precisions.append(precision)
        objectives.append(obj)
        runtime.append(rt)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    lns1 = ax1.plot(p_values, recalls, label='Recall random sample')
    lns2 = ax1.plot(p_values, precisions, label='Precision random sample')
    lns3 = ax1.axhline(y=mip_recall, linestyle=':', label='recall MIP-rectangles')
    lns4 = ax1.axhline(y=mip_preci, linestyle='-.', label='precision MIP-rectangles')
    ax1.set_xlabel('Percentage of full set of candidates generated')

    lns5 = ax2.plot(p_values, runtime, color='r', label='Runtime of the sampling')
    lns6 = ax2.axhline(y= generate_candi_time, color='r', linestyle=':', label='Runtime generation candidate')
    ax2.set_ylabel('Runtime in seconds')

    lns = lns1 + lns2 + [lns3, lns4] + lns5 + [lns6]
    labs = [l.get_label() for l in lns]
    plt.legend(lns, labs, loc='lower right')
    plt.savefig(os.path.join(get_figures_directory(),'random-sample-metrics.pdf'), bbox_inches='tight')
    plt.close()

    plt.plot(p_values, objectives, label='Desc. length random sample')
    plt.axhline(y=optimal_obj,color='r', label='Minimum Desc. length')
    plt.xlabel('Percentage of full set of candidates generated')
    plt.legend()
    plt.savefig(os.path.join(get_figures_directory(),'random-sample-desc-length.pdf'), bbox_inches='tight')
    plt.close()
