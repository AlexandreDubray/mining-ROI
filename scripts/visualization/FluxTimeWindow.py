# -*- coding: utf-8 -*-

from shared.Utils import get_data
from visualization.Utils import *
import pickle
from datetime import datetime

def get_flux(rectangles, circles, start_time, end_time):
    map_to_ROI = map_cell_to_ROI(rectangles, circles)
    map_flux_ROI = {}

    for rectangle in rectangles:
        map_flux_ROI[rectangle] = {}
    for circle in circles:
        map_flux_ROI[circle] = {}
    data = get_data()
    count = 0
    count_no_ROI = 0
    for trajectory_id in data:
        timestamp = data[trajectory_id]['TIMESTAMP']
        date = datetime.fromtimestamp(timestamp)
        if date.hour >= start_time and date.hour <= end_time:
            positions = data[trajectory_id]['POLYLINE']
            count += 1
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
            if last_ROI is None:
                count_no_ROI += 1
    print(count)
    print(count_no_ROI)
    return map_flux_ROI

def show_flux_time_window(rectangles, circles, start_time, end_time, filename):
    m = create_map(rectangles, circles)
    flux_roi = get_flux(rectangles, circles, start_time, end_time)
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

    m.save(os.path.join(get_html_dir(), filename + ".html"))
