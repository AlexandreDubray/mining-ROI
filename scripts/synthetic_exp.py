#! /usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time

from mip.mip_column import run as run_mip
from baseline.Greedy import run as run_baseline

import matplotlib.pyplot as plt
import matplotlib as mpl

params = {
    'axes.labelsize': 12,
    'font.size': 12,
    'legend.fontsize': 11,
    'legend.loc': 'right',
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'text.usetex': False,
    'figure.figsize': [6.5, 4.5]
    }
mpl.rcParams.update(params)

random.seed(11781400)

size = 20

# (row1, row2, col1, col2)
rectangles = [
        (0,1,9,12),
        (3,3,2,10),
        (2,8,16,18),
        (8,11,6,9),
        (7,13,1,2),
        (10,12,16,17),
        (16,18,1,4),
        (14,19,6,8),
        (16,18,11,14),
        (15,16,15,16)]

total_dense = 0

def create_correct():
    global total_dense
    initial = [[0 for _ in range(size)] for _ in range(size)]
    for (r1,r2,c1,c2) in rectangles:
        for r in range(r1,r2+1):
            for c in range(c1,c2+1):
                initial[r][c] = 1
                total_dense += 1
    return initial

def create_matrix(initial, p):
    matrix = [[x for x in row] for row in initial]
    for row in range(len(matrix)):
        for col in range(len(matrix[row])):
            if random.uniform(0.0, 1.0) < p:
                # Inverting the entry
                #print('Inverting ({},{})'.format(row+1, col+1))
                matrix[row][col] = 1 - matrix[row][col]
    return matrix

def compute_true_positive(rois, initial):
    true_positive = 0
    true_and_false_positive = 0
    for (r1,r2,c1,c2) in rois:
        for r in range(r1,r2+1):
            for c in range(c1,c2+1):
                if initial[r][c] == 1:
                    true_positive += 1
                true_and_false_positive +=1
    return (true_positive, true_and_false_positive)

def parse_file():
    with open('synthetic_log.log', 'r') as f:
        lines = f.readlines()
        recall_mip = [float(x) for x in lines[0].split(' ')]
        recall_baseline = [float(x) for x in lines[1].split(' ')]
        precision_mip = [float(x) for x in lines[2].split(' ')]
        precision_baseline = [float(x) for x in lines[3].split(' ')]
        f1_mip = [float(x) for x in lines[4].split(' ')]
        f1_baseline = [float(x) for x in lines[5].split(' ')]

    p_values = [x/100.0 for x in range(0,51)]

    plt.plot(p_values, recall_mip, linestyle=':', label='recall MIP')
    plt.plot(p_values, recall_baseline, linestyle='--', label='recall PopularRegion')

    plt.plot(p_values, precision_mip, linestyle='-.', label='precision MIP')
    plt.plot(p_values, precision_baseline, linestyle='-', label='precision PopularRegion')

    #plt.plot(p_values, f1_mip, label='f1 MIP')
    #plt.plot(p_values, f1_baseline, label='f1 PopularRegion')

    plt.xlabel('percentage of noise')
    #plt.legend(prop={'size':7})
    plt.legend(bbox_to_anchor=(1.0,0.75))
    plt.savefig('synthetic_metric.pdf', bbox_inches='tight')
    plt.close()

def run_synthetic_experiment():
    parse_file()
    return
    initial = create_correct()
    p_values = [x/100.0 for x in range(0,51)]

    recall_mip = list()
    precision_mip = list()
    f1_mip = list()

    recall_baseline = list()
    precision_baseline = list()
    f1_baseline = list()

    repet = 20
    for prob in p_values:
        print(prob)
        rc_mip = 0
        pr_mip = 0
        rc_base = 0
        pr_base = 0
        for _ in range(repet):
            matrix = create_matrix(initial, prob)
            mip_rois = run_mip(use_synt_data=True, synt_data=matrix)[0]
            mip_rois = [(x,y,z,t) for ((x,y,z,t),_) in mip_rois]
            baseline_rois = [(x,y,z,t) for x,y,z,t,_,_ in run_baseline(use_synt_data=True, synt_data=matrix)]
            (tp,tpfp) = compute_true_positive(mip_rois, initial)
            rc_mip += float(tp/total_dense)
            pr_mip += float(tp/tpfp)

            (tp,tpfp) = compute_true_positive(baseline_rois, initial)
            rc_base += float(tp/total_dense)
            pr_base += float(tp/tpfp)

        recall_mip.append(rc_mip/repet)
        precision_mip.append(pr_mip/repet)
        f1_mip.append(2.0* ((recall_mip[-1]*precision_mip[-1])/(recall_mip[-1]+precision_mip[-1])))

        recall_baseline.append(rc_base/repet)
        precision_baseline.append(pr_base/repet)
        f1_baseline.append(2.0* ((recall_baseline[-1]*precision_baseline[-1])/(recall_baseline[-1]+precision_baseline[-1])))

    with open('synthetic_log.log', 'w') as f:
        f.write('{}\n'.format(' '.join([str(x) for x in recall_mip])))
        f.write('{}\n'.format(' '.join([str(x) for x in recall_baseline])))
        f.write('{}\n'.format(' '.join([str(x) for x in precision_mip])))
        f.write('{}\n'.format(' '.join([str(x) for x in precision_baseline])))
        f.write('{}\n'.format(' '.join([str(x) for x in f1_mip])))
        f.write('{}\n'.format(' '.join([str(x) for x in f1_baseline])))

    parse_file()

def matrix_fifteen():
    initial = create_correct()
    prob = 0.03
    matrix = create_matrix(initial, prob)
    mip_rois = run_mip(use_synt_data=True, synt_data=matrix, use_circle=True)[0]
    mip_rois = [(x+1,y+1,z+1,t+1) for ((x,y,z,t),_) in mip_rois]
    baseline_rois = [(x+1,y+1,z+1,t+1) for x,y,z,t,_,_ in run_baseline(use_synt_data=True, synt_data=matrix)]
    print(mip_rois)
    print(baseline_rois)


def increase_dimension(matrix):
    index = random.randint(0,len(matrix)-1)
    for row in matrix:
        row.insert(index,row[index])
    row_to_copy = matrix[index]
    matrix.insert(index, [x for x in row_to_copy])

def parse_time():
    creation_time = list()
    solve_time = list()
    with open('time-mip.out', 'r') as f:
        for line in f.readlines():
            (ct,st) = [float(x) for x in line.split(' ')]
            creation_time.append(ct)
            solve_time.append(st)

    with open('time-baseline.out', 'r') as f:
        base_rtime = [float(x) for x in f.readlines()[0].split(' ')]

    side_size = range(20,51)
    plt.plot(side_size, creation_time, linestyle='-', label='Generation of candidates')
    plt.plot(side_size, solve_time, linestyle='--', label='Solving optimization')
    plt.plot(side_size, base_rtime, linestyle=':', label='PopularRegion')
    plt.ylabel('Time in seconds')
    plt.xlabel('Side size of the square grid')
    plt.legend()
    plt.savefig('time-mip.pdf')
    plt.close()


def runtime_mip():
    parse_time()
    return
    initial = create_correct()
    mip_time = list()
    repet = 20
    for dim in range(50-19):
        print("Size {}".format(20+dim))
        increase_dimension(initial)
        ctime = 0.0
        rtime = 0.0
        for _ in range(repet):
            matrix = create_matrix(initial, 0.15)
            (_, creation_roi_time, run_time) = run_mip(use_synt_data=True, synt_data=matrix)
            ctime += creation_roi_time
            rtime += run_time
        mip_time.append([str(ctime/repet), str(rtime/repet)])

    with open('time-mip.out', 'w') as f:
        for t in mip_time:
            f.write('{}\n'.format(' '.join(t)))
    parse_time()

def runtime_baseline():
    initial = create_correct()
    baseline_time = list()
    repet = 20
    for dim in range(50-19):
        print("Size {}".format(20+dim))
        increase_dimension(initial)
        rtime = 0.0
        for _ in range(repet):
            matrix = create_matrix(initial, 0.15)
            start_time = time.time()
            _ = run_baseline(use_synt_data=True, synt_data=matrix)
            end_time = time.time()
            rtime += end_time - start_time
        baseline_time.append(str(rtime/repet))

    with open('time-baseline.out', 'w') as f:
        f.write(' '.join(baseline_time))
    parse_time()

