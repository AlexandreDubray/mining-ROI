#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

import folium

from visualization import Utils

from shared.Utils import *
from shared.Constant import side_size

from baseline.Utils import get_output_file as get_base_output_file
from baseline.Greedy import run as baseline_run

from mip.Utils import get_mip_matrix_file, get_mip_output_file

def create_map():
    m = folium.Map(
            location=[min_latitude+(max_latitude-min_latitude)/2, min_longitude+(max_longitude-min_longitude)/2],
            zoom_start=13
            )
    return m

def add_rectangles_to_map(minRow, maxRow, minCol, maxCol, m, color, fop):
    (minLat, maxLat, minLong, maxLong) = map_rectangles_to_pos(minRow, maxRow, minCol, maxCol)
    folium.Polygon(
            locations=[(minLat, minLong), (minLat, maxLong), (maxLat, maxLong), (maxLat, minLong), (minLat, minLong)],
            fill_color=color,
            fill_opacity=fop
            ).add_to(m)

def add_circle_to_map(row, col, radius, m, color, fop):
    folium.Polygon(
            locations = map_circle_to_pos(row, col, radius),
            fill_color=color,
            fill_opacity=fop
            ).add_to(m)

def visu_baseline():
    print_flush('Creating HTML for visualization of baseline algorithm')
    with get_base_output_file() as f:
        rois = list()
        for line in f.readlines():
            rois.append([int(x) for x in line.split(' ')])

    m = create_map()
    for x,y,z,t in rois:
        add_rectangles_to_map(x,y,z,t,m, 'red', 0.5)
    m.save(os.path.join(Utils.get_html_dir(), 'baseline.html'))

def visu_initial():
    m = create_map()
    data = get_initial_matrix()
    for row in range(side_size):
        for col in range(side_size):
            if data[row][col] >= threshold:
                add_rectangles_to_map(row, row, col, col, m, 'blue', 0.5)
    m.save(os.path.join(Utils.get_html_dir(), 'initial.html'))

def visu_mip():
    m = create_map()
    rects = list()
    circs = list()
    with get_mip_output_file() as f:
        for line in f.readlines():
            s = line.split(' ')
            if s[0] == 'rectangle':
                rects.append([int(x) for x in s[1:]])
            elif s[0] == 'circle':
                circs.append([int(x) for x in s[1:]])
    (offr, offc) = get_mip_shift()
    for x,y,z,t in rects:
        add_rectangles_to_map(z+offr,t+offr,x+offc,y+offc,m, 'green', 0.5)
    for (row, col, radius) in circs:
        add_circle_to_map(row+offr, col+offc, radius,m, 'blue', 0.5)
    m.save(os.path.join(Utils.get_html_dir(), 'mip.html'))

def visu_mip_vs_baseline():

    data = [[0 for col in range(side_size)] for row in range(side_size)]
    m = create_map()

    rects = list()
    with get_mip_output_file() as f:
        for line in f.readlines():
            rects.append([int(x) for x in line.split(' ')])
    (offr, offc) = get_mip_shift()
    for x,y,z,t in rects:
        for i in range(z+offr, t+offr+1):
            for j in range(x+offc, y+offc+1):
                data[i][j] = 1

    # Adding the baseline output
    with get_base_output_file() as f:
        rois = list()
        for line in f.readlines():
            rois.append([int(x) for x in line.split(' ')])

    for x,y,z,t in rois:
        for i in range(x,y+1):
            for j in range(z,t+1):
                if data[i][j] == 1:
                    data[i][j] = 3
                else:
                    data[i][j] = 2

    for row in range(len(data)):
        for col in range(len(data[row])):
            # Only in MIP
            if data[row][col] == 1:
                add_rectangles_to_map(row,row,col,col, m, 'green', 1.0)
            # Only in baseline
            elif data[row][col] == 2:
                add_rectangles_to_map(row,row,col,col, m, 'red', 1.0)
            # in both
            elif data[row][col] == 3:
                add_rectangles_to_map(row,row,col,col, m, 'blue', 1.0)
                    

    m.save(os.path.join(Utils.get_html_dir(), 'mip_vs_baseline.html'))
