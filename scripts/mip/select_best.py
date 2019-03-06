#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time

from mip import Utils

def run_mdl():
    start_time = time.time()
    (_, N) = Utils.get_initial_mip_data()
    
    with Utils.get_gurobi_output_file() as f:
        bestLength = sys.maxsize
        rects = None
        circles = None
        for out in f.read().split('\n\n')[:-1]:

            covered = 0
            errored = 0

            s = out.split('\n')
            K = int(s[0].split(' ')[0])

            curr_rect = list()
            curr_circ = list()

            for i in range(1, len(s)):
                roi = s[i].split(' ')
                if roi[0] == 'rectangle':
                    (x,y,z,t, dense, nondense) = [int(x) for x in roi[1:]]
                    covered += dense
                    errored += nondense
                    curr_rect.append((x,y,z,t, dense, nondense))
                elif roi[0] == 'circle':
                    (row, col, radius, dense, nondense) = [int(x) for x in roi[1:]]
                    covered += dense
                    errored += nondense
                    curr_circ.append((row, col, radius, dense, nondense))
                else:
                    print("Unknown roi type {}".format(roi[0]))
                    sys.exit(1)

            total_error_encode = (N - covered) + errored
            length = len(curr_rect)*4 + len(curr_circ)*3 + total_error_encode*2
            if length < bestLength:
                bestLength = length 
                rects = [x for x in curr_rect]
                circles = [x for x in curr_circ]
        
        end_time = time.time()
        with open(Utils.mip_time_file(), 'w') as f:
            f.write('{}'.format(end_time - start_time))
        with open(Utils.mip_output_file(), 'w') as f:
            for rect in rects:
                f.write('rectangle {}\n'.format(' '.join([str(x) for x in rect])))
            for circle in circles:
                f.write('circle {}\n'.format(' '.join([str(x) for x in circle])))

