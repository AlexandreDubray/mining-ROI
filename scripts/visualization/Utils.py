# -*- coding: utf-8 -*-

import os
import sys
from shared.Utils import ratio_latitude, ratio_longitude, get_data, get_long_lat_from_str, map_pos_to_cell
from shared.Constant import *

from mip.Utils import get_mip_matrix_file

import pickle
import numpy as np
import folium

from geographiclib.geodesic import Geodesic

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_html_dir():
    return os.path.join(SCRIPT_DIR, '..', '..', 'webapp')

def create_map(rectangles, circles):
    m = folium.Map(
            location=[min_latitude+(max_latitude-min_latitude)/2, min_longitude+(max_longitude-min_longitude)/2],
            zoom_start=14,
            #tiles='http://{s}.www.toolserver.org/tiles/bw-mapnik/{z}/{x}/{y}.png',
            #attr='&copy; ' + '<a href="http://openstreetmap.org">OpenStreetMap</a>' + ' Contributors'
            )
    for rectangle in rectangles:
        add_rectangle_to_map(rectangle, m)

    for circle in circles:
        add_circle_to_map(circle, m)

    return m

def add_rectangle_to_map(rectangle, m):
    (min_lat, max_lat, min_long, max_long) = map_rectangle_to_pos(rectangle)
    folium.Polygon(
            locations=[(min_lat,min_long), (min_lat, max_long), (max_lat, max_long), (max_lat, min_long), (min_lat, min_long)],
            fill_color='707070',
            color='#000000',
            fill_opacity=0.5).add_to(m)

def add_circle_to_map(circle, m):
    folium.Polygon(
            locations = map_circle_to_pos(circle),
            fill_color='707070',
            color='#000000',
            fill_opacity=0.5).add_to(m)

def add_arrow_rois(source_roi, target_roi, value, m):
    positions = get_source_target_pos(source_roi, target_roi)
    (source_lat, source_long) = positions[0]
    (target_lat, target_long) = positions[1]
    folium.PolyLine(
            locations=[(source_lat, source_long), (target_lat, target_long)],
            weight=value,
            opacity=0.7,
            #color='red',
            ).add_to(m)

    get_arrow((source_lat, source_long), (target_lat, target_long), value).add_to(m)


def map_rectangle_to_pos(rect):
    (min_row, min_col, max_row, max_col) = rect
    # min_row -> lower latitude
    # min_col -> lower longitude
    min_lat = min_latitude + min_row*ratio_latitude()
    max_lat = min_latitude + (max_row+1)*ratio_latitude()
    max_long = min_longitude + min_col*ratio_longitude()
    min_long = min_longitude +(max_col+1)*ratio_longitude()
    return (min_lat, max_lat, min_long, max_long)

def map_cell_to_lat_long(row, col):
    return map_rectangle_to_pos(row, row, col, col)

def map_circle_to_pos(circle):
    (row, col, radius) = circle
    lgn_lat = list()
    # Highest cell in the circle
    (upLat1, upLat2, upLong1, upLong2) = map_rectangle_to_pos((row+radius+1, col, row+radius+1, col))
    # Adding top cell border
    lgn_lat.append((upLat1, upLong2))
    lgn_lat.append((upLat1, upLong1))

    # from up to right
    current_pos = (upLat1, upLong1)
    for _ in range(radius):
        # go one below, then one right
        next_pos = (current_pos[0] - ratio_latitude(), current_pos[1])
        lgn_lat.append(next_pos)
        next_pos = (next_pos[0], next_pos[1]+ratio_longitude())
        lgn_lat.append(next_pos)
        current_pos = next_pos

    #adding right border
    current_pos = (current_pos[0] - ratio_latitude(), current_pos[1])
    lgn_lat.append(current_pos)

    #from right to bottom
    for _ in range(radius):
        #go one left then one bottom
        next_pos = (current_pos[0], current_pos[1] - ratio_longitude())
        lgn_lat.append(next_pos)
        next_pos = (next_pos[0] - ratio_latitude(), next_pos[1])
        lgn_lat.append(next_pos)
        current_pos = next_pos

    # addign bottom border
    current_pos = (current_pos[0], current_pos[1] - ratio_longitude())
    lgn_lat.append(current_pos)
    
    #from bottom to left
    for _ in range(radius):
        # go one up then one left
        next_pos = (current_pos[0] + ratio_latitude(), current_pos[1])
        lgn_lat.append(next_pos)
        next_pos = (next_pos[0], next_pos[1] - ratio_longitude())
        lgn_lat.append(next_pos)
        current_pos = next_pos

    # left border
    current_pos = (current_pos[0] + ratio_latitude(), current_pos[1])
    lgn_lat.append(current_pos)
    
    # left to up
    for _ in range(radius):
        # one right then one up
        next_pos = (current_pos[0], current_pos[1]+ratio_longitude())
        lgn_lat.append(next_pos)
        next_pos = (next_pos[0] + ratio_latitude(), next_pos[1])
        lgn_lat.append(next_pos)
        current_pos = next_pos

    return lgn_lat

def get_mip_shift():
    with get_mip_matrix_file() as f:
        data = [[int(x) for x in line.split("\t")] for line in f.read().split("\n") if line != ""]
    max_col = -1
    min_col = sys.maxsize
    max_row = -1
    min_row = sys.maxsize
    for col in range(len(data)):
        for row in range(len(data[0])):
            if data[row][col] == 1:
                max_col = max(max_col,col)
                min_col = min(min_col,col)
                max_row = max(max_row,row)
                min_row = min(min_row,row)
    return (min_row, min_col)

def project_back_mip_regions(rectangles, circles):
    (row_shift, col_shift) = get_mip_shift()
    rectangles_back_proj = [(min_row + row_shift, min_col + col_shift, max_row + row_shift, max_col + col_shift) for (min_row, min_col, max_row, max_col) in rectangles]
    circles_back_proj = [(row + row_shift, col + col_shift, radius) for (row,col,radius) in circles]
    return (rectangles_back_proj, circles_back_proj)

def map_cell_to_ROI(rectangles, circles):
    map_to_ROI = {}

    for rect in rectangles:
        (min_row, min_col, max_row, max_col) = rect
        for row in range(min_row, max_row+1):
            for col in range(min_col, max_col+1):
                map_to_ROI[(row,col)] = rect

    for circ in circles:
        (row, col, radius) = circ
        for rad in range(radius+1):
            for c in range(col - radius + rad, col + radius - rad + 1):
                map_to_ROI[(row-rad, c)] = circ
                map_to_ROI[(row+rad, c)] = circ
    return map_to_ROI

def get_center_cell_roi(roi):
    if len(roi) == 3:
        # circle
        (row, col) = (roi[0], roi[1])
    else:
        #rectangle
        (min_row, min_col, max_row, max_col) = roi
        height = (max_row - min_row + 1)
        width = (max_col - min_col + 1)
        if height % 2 == 0:
            # Height is even, thus the center is composed of multiple cell in the row axis.
            # We take the upper row to compute the pos
            row = min_row + height/2
            if width % 2 == 0:
                # The center is four cells
                col = min_col + width/2
            else:
                # The center is two cell on the same column
                col = min_col + (width-1)/2
        else:
            # Height is odd, center is one cell on the row axis
            row = min_row + (height-1)/2
            if width % 2 == 0:
                # The center is two cell on the same row
                col = min_col + width/2
            else:
                # The center is a single cell
                col = min_col + (width-1)/2
    return (row,col)

# Code took from https://medium.com/@bobhaffner/folium-lines-with-arrows-25a0fe88e4e
def get_bearing(p1, p2):
    long_diff = np.radians(p2[1] - p1[1])
    lat1 = np.radians(p1[0])
    lat2 = np.radians(p2[0])
    x = np.sin(long_diff) * np.cos(lat2)
    y = (np.cos(lat1)*np.sin(lat2) - (np.sin(lat1)*np.cos(lat2)*np.cos(long_diff)))

    bearing = np.degrees(np.arctan2(x,y))
    if bearing < 0:
        return bearing + 360
    return bearing

def get_arrow(source, target, radius):
    rotation = get_bearing(source, target) - 90
    #rotation = Geodesic.WGS84.Inverse(source[0],source[1],target[0], target[1])['azi1'] - 90

    return folium.RegularPolygonMarker(location=target, fill_color='blue',
            number_of_sides=3, radius=radius, rotation=rotation)

def get_roi_cells(roi):
    cells = list()
    if len(roi) == 4:
        for r in range(roi[0], roi[2]+1):
            for c in range(roi[1], roi[3]+1):
                cells.append((r,c))
    else:
        for rad in range(roi[2]+1):
            for c in range(roi[1] - roi[2] + rad, roi[1]+ roi[2] - rad + 1):
                cells.append((roi[0]-rad, c))
                cells.append((roi[0]+rad, c))
    return cells

occupied = {}
def get_source_target_pos(source, target):
    global occupied
    source_center = get_center_cell_roi(source)
    if target not in occupied:
        occupied[target] = set()
    target_cell = None
    d = sys.maxsize
    for (row,col) in get_roi_cells(target):
        if (row,col) not in occupied[target]:
            dist = abs(row-source_center[0]) + abs(col-source_center[1])
            if dist < d:
                d = dist
                target_cell = (row,col)
    if target_cell is None:
        occupied[target] = set()
        return get_source_target_pos(source, target)
    occupied[target].add(target_cell)

    source_latitude = min_latitude + source_center[0]*ratio_latitude() + ratio_latitude()/2
    source_longitude = min_longitude + source_center[1]*ratio_longitude() + ratio_longitude()/2

    target_latitude = min_latitude + target_cell[0]*ratio_latitude() + ratio_latitude()/2
    target_longitude = min_longitude + target_cell[1]*ratio_longitude() + ratio_longitude()/2

    return ((source_latitude, source_longitude), (target_latitude, target_longitude))

