#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

from mip import Utils

def run_mdl():
    N = 0
    with Utils.get_mip_matrix_file() as f:
        data = [[int(x) for x in line.split("\t")] for line in f.read().split("\n") if line != ""]
        maxX = -1
        minX = sys.maxsize
        maxY = -1
        minY = sys.maxsize
        for row in range(len(data)):
            for col in range(len(data[row])):
                if data[row][col] == 1:
                    maxX = max(maxX,col)
                    minX = min(minX,col)
                    maxY = max(maxY,row)
                    minY = min(minY,row)
                    N += 1

    data = data[minY:maxY+1]
    for i,d in enumerate(data):
        data[i] = d[minX:maxX+1]

    #for r in range(len(data)-1, -1, -1):
    #    print(' '.join([str(x) for x in data[r]]))
    
    with open(Utils.mip_gurobi_output_file, 'r') as f:
        bestK = None
        bestError = None
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

            for xmin, xmax, ymin, ymax in re:
                for col in range(xmin, xmax+1):
                    for row in range(ymin, ymax+1):
                        if data[row][col] == 1:
                            covered += 1
                        else:
                            errored += 1
            total_error_encode = (N - covered) + errored
            split = first.split(' ')
            K = int(split[0])
            if K + total_error_encode < bestLength:
                bestK = K
                bestError = total_error_encode
                bestLength = bestK + bestError
                rects = [x for x in re]
        
        with open(Utils.mip_output_file, 'w') as f:
            for rect in rects:
                f.write('{}\n'.format(' '.join([str(x) for x in rect])))

