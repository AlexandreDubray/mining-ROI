#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import math

from mip import Utils

def count_dense_nondense(xmin, xmax, ymin, ymax, data):
    dense = 0
    undense = 0
    for row in range(ymin, ymax+1):
        for col in range(xmin, xmax+1):
            if data[row][col] == 1:
                dense += 1
            else:
                undense += 1
    return (dense, undense)

def total_error_rectangles(rectangles, data, N):
    total_dense_covered = 0
    total_nondense_covered = 0
    for xmin, xmax, ymin, ymax in rectangles:
        (d,nd) = count_dense_nondense(xmin,xmax,ymin,ymax, data)
        total_dense_covered += d
        total_nondense_covered += nd
    return (N - total_dense_covered) + total_nondense_covered

def run_mdl():
    (data, N) = Utils.get_initial_mip_data()
    
    with open(Utils.mip_gurobi_output_file, 'r') as f:
        bestLength = sys.maxsize
        rects = None
        for out in f.read().split('\n\n')[:-1]:

            covered = 0
            errored = 0

            s = out.split('\n')
            first = s[0]

            rs = s[1:]
            rss = [x.split(' ') for x in rs]
            re = [ (int(x), int(y), int(z), int(t)) for x,y,z,t in rss]

            total_error_encode = total_error_rectangles(re, data, N)

            split = first.split(' ')
            K = int(split[0])
            length = K*math.log(4) + math.log(2)*total_error_encode
            if length < bestLength:
                bestLength = length 
                rects = [x for x in re]
        
        with open(Utils.mip_output_file, 'w') as f:
            for rect in rects:
                f.write('{}\n'.format(' '.join([str(x) for x in rect])))

