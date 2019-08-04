# -*- coding: utf-8 -*-

import os
import pickle

from visualization.Utils import *

from shared.Constant import *

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def write_flux_between_ROI(rectangles, circles):

    map_to_ROI = map_cell_to_ROI(rectangles, circles)
    map_flux_ROI = {}

    for rectangle in rectangles:
        map_flux_ROI[rectangle] = {}
    for circle in circles:
        map_flux_ROI[circle] = {}

    data = get_data()
    for trajectory_id in data:
        positions = data[trajectory_id]['POLYLINE']
        last_ROI = None
        for pos in positions:
            cell = map_pos_to_cell(pos)
            if cell in map_to_ROI:
                current_ROI = map_to_ROI[cell]
                if last_ROI is None:
                    last_ROI = current_ROI
                elif last_ROI != current_ROI:
                    if current_ROI not in map_flux_ROI[last_ROI]:
                        map_flux_ROI[last_ROI][current_ROI] = 1
                    else:
                        map_flux_ROI[last_ROI][current_ROI] += 1
                    last_ROI = current_ROI
    outfile = os.path.join(SCRIPT_DIR, 'logs', 'flux-ROI-{}-{}.pkl'.format(get_percentage_threshold(), side_size()))
    with open(outfile, 'wb') as f:
        pickle.dump(map_flux_ROI, f, pickle.HIGHEST_PROTOCOL)

def get_flux_between_ROI():
    infile = os.path.join(SCRIPT_DIR, 'logs', 'flux-ROI-{}-{}.pkl'.format(get_percentage_threshold(), side_size()))
    with open(infile, 'rb') as f:
        return pickle.load(f)

def show_flux_rois(rectangles, circles):
    m = create_map(rectangles, circles)
    flux_roi = get_flux_between_ROI()
    flux = list()
    for source in flux_roi:
        for target in flux_roi[source]:
            flux.append((flux_roi[source][target], source, target))
    flux = sorted(flux, reverse=True)
    base_width=20
    max_flux = flux[0][0]
    threshold = 0.1
    for idx in range(int(len(flux)*threshold)):
        (f, source, target) = flux[idx]
        width =  int((f/max_flux)*base_width)
        add_arrow_rois(source, target, width, m)
    m.save(os.path.join(get_html_dir(), 'map.html'))
