#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

import folium

from Utils import *
import baseline
import select_best

SCRIPT_DIR = os.getcwd()

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
    try:
        with open(os.path.join(SCRIPT_DIR, '..', 'output', 'baseline.out'), 'r') as f:
            rois = list()
            for line in f.readlines():
                rois.append([int(x) for x in line.split(' ')])
        m = create_map()
        for x,y,z,t in rois:
            add_rectangles_to_map(x,y,z,t,m)
        m.save(os.path.join(SCRIPT_DIR, '..', 'webapp', 'baseline.html'))

    except FileNotFoundError:
        baseline.main()
        visu_baseline()


def visu_initial():
    m = create_map()
    data = baseline.get_data()
    for row in range(side_size):
        for col in range(side_size):
            if data[row][col] >= threshold:
                add_rectangles_to_map(row, row, col, col, m)
    m.save(os.path.join(SCRIPT_DIR, '..', 'webapp', 'initial.html'))

def visu_mip():
    try:
        m = create_map()
        rects = list()
        with open(os.path.join(SCRIPT_DIR, '..', 'output', 'mip.out'), 'r') as f:
            for line in f.readlines():
                rects.append([int(x) for x in line.split(' ')])
        for x,y,z,t in rects:
            add_rectangles_to_map(x,y,z,t,m)
            m.save(os.path.join(SCRIPT_DIR, '..', 'webapp', 'mip.html'))
    except FileNotFoundError:
        select_best.main()


visu_initial()
visu_baseline()
visu_mip()
