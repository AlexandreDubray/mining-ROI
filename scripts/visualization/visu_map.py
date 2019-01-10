#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

import folium

from visualization import Utils

from shared.Utils import *

from baseline.Utils import get_output_file as get_base_output_file
from baseline.Greedy import run as baseline_run

from mip.Utils import get_mip_matrix_file, get_mip_output_file

def create_map():
    m = folium.Map(location=[min_latitude+(max_latitude-min_latitude)/2, min_longitude+(max_longitude-min_longitude)/2])
    return m

def add_rectangles_to_map(minRow, maxRow, minCol, maxCol, m):
    (minLat, maxLat, minLong, maxLong) = map_rectangles_to_pos(minRow, maxRow, minCol, maxCol)
    folium.Polygon(
            locations=[(minLat, minLong), (minLat, maxLong), (maxLat, maxLong), (maxLat, minLong), (minLat, minLong)],
            fill_color='red'
            ).add_to(m)

def visu_baseline():
    print_flush('Creating HTML for visualization of baseline algorithm')
    with get_base_output_file() as f:
        rois = list()
        for line in f.readlines():
            rois.append([int(x) for x in line.split(' ')])

    m = create_map()
    for x,y,z,t in rois:
        add_rectangles_to_map(x,y,z,t,m)
    m.save(os.path.join(Utils.get_html_dir(), 'baseline.html'))

def visu_initial():
    m = create_map()
    data = get_initial_matrix()
    for row in range(side_size):
        for col in range(side_size):
            if data[row][col] >= threshold:
                add_rectangles_to_map(row, row, col, col, m)
    m.save(os.path.join(Utils.get_html_dir(), 'initial.html'))

def visu_initial_mip():
    with get_mip_matrix_file() as f:
        m = create_map()
        data = [[int(x) for x in line.split('\t')] for line in f.read().split('\n') if line != '']

    for row in range(side_size):
        for col in range(side_size):
            if data[row][col] == 1:
                add_rectangles_to_map(row, row, col, col, m)
    m.save(os.path.join(Utils.get_html_dir(), 'initial-mip.html'))

def visu_mip():
    m = create_map()
    rects = list()
    with get_mip_output_file() as f:
        for line in f.readlines():
            rects.append([int(x) for x in line.split(' ')])
    (offr, offc) = Utils.get_mip_shift()
    for x,y,z,t in rects:
        add_rectangles_to_map(x+offr,y+offr,z+offc,t+offc,m)
        m.save(os.path.join(Utils.get_html_dir(), 'mip.html'))

