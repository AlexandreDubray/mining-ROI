# -*- coding: utf-8 -*-

from popular_region import PopularRegion
from popular_region.Utils import get_popular_region_data

from mip import mip_column
from mip.Utils import get_mip_data

from shared.Constant import side_size,set_side_size, set_percentage_threshold
from shared import Constant

from experiment.Utils import get_figures_directory

import matplotlib.pyplot as plt
import matplotlib as mpl

import os
params = {
    'axes.labelsize': 12,
    'font.size': 12,
    'legend.fontsize': 12,
    'legend.loc': 'right',
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'text.usetex': False,
    'figure.figsize': [6.5, 4.5],
    'lines.linewidth': 2,
    }
mpl.rcParams.update(params)

def compute_error_rate(binary_data, rectangular_regions, circular_regions):
    number_dense = sum([sum(x) for x in binary_data])
    number_cell = side_size()**2 # Assuming squared grid for now
    dense_covered = 0
    non_dense_covered = 0

    for (min_row, min_col, max_row, max_col) in rectangular_regions:
        dense = sum([sum(x[min_col:(max_col+1)]) for x in binary_data[min_row:(max_row+1)]])
        dense_covered += dense
        non_dense_covered += ( (max_row-min_row+1)*(max_col-min_col+1) ) - dense

    for (row, col, radius) in circular_regions:
        # Central part
        (min_row, min_col, max_row, max_col) = (row, col-radius, row, col+radius)
        dense = sum([sum(x[min_col:(max_col+1)]) for x in binary_data[min_row:(max_row+1)]])
        dense_covered += dense
        non_dense_covered += ( (max_row-min_row+1)*(max_col-min_col+1) ) - dense

        for r in range(1, radius+1):
            # Upper part
            (min_row, min_col, max_row, max_col) = (row-r, col - (radius-r), row-r, col + (radius-r))
            dense = sum([sum(x[min_col:(max_col+1)]) for x in binary_data[min_row:(max_row+1)]])
            dense_covered += dense
            non_dense_covered += ( (max_row-min_row+1)*(max_col-min_col+1) ) - dense

            # Lower part
            (min_row, min_col, max_row, max_col) = (row+r, col - (radius-r), row+r, col + (radius-r))
            dense = sum([sum(x[min_col:(max_col+1)]) for x in binary_data[min_row:(max_row+1)]])
            dense_covered += dense
            non_dense_covered += ( (max_row-min_row+1)*(max_col-min_col+1) ) - dense
    errors = (number_dense - dense_covered) + non_dense_covered
    return (errors/number_cell)*100

def MDL_on_threshold(size):
    set_side_size(size)
    thresholds = range(5,31)

    mip_error_rate = []
    mip_model_length = []

    # Mip model restricted to use only rectangular regions
    mip_rectangle_error_rate = []
    mip_rectangle_model_length = []

    popular_region_error_rate = []
    popular_region_model_length = []

    for threshold in thresholds:
        set_percentage_threshold(threshold)
        mip_data = get_mip_data()

        mip_regions = mip_column.run(mip_data)['rois']
        error_rate = compute_error_rate(mip_data, mip_regions[0], mip_regions[1])
        model_length = 4*len(mip_regions[0]) + 3*len(mip_regions[1])
        mip_error_rate.append(error_rate)
        mip_model_length.append(model_length)

        mip_rectangles_regions = mip_column.run(mip_data, use_circle=False)['rois']
        error_rate = compute_error_rate(mip_data, mip_rectangles_regions[0], mip_rectangles_regions[1])
        model_length = 4*len(mip_rectangles_regions[0]) + 3*len(mip_rectangles_regions[1])
        mip_rectangle_error_rate.append(error_rate)
        mip_rectangle_model_length.append(model_length)

        popular_region_data = get_popular_region_data()
        # Transform popular region matrix in binary form to compute error rate
        popular_region_binary_data = [[ 1 if popular_region_data[row][col] >= Constant.threshold() else 0 for col in range(size)] for row in range(size)]
        popular_region_regions = PopularRegion.run(popular_region_data)['rois']
        error_rate = compute_error_rate(popular_region_binary_data, popular_region_regions, list())
        model_length = 4*len(popular_region_regions)
        popular_region_error_rate.append(error_rate)
        popular_region_model_length.append(model_length)

    # First graph, error rate over minimum density threshold
    plt.plot(thresholds, mip_error_rate, linestyle=':', label='MIP')
    plt.plot(thresholds, mip_rectangle_error_rate, linestyle='--', label='MIP-rectangles')
    plt.plot(thresholds, popular_region_error_rate, label='PopularRegion')
    plt.xlabel('Minimum density threshold (% of total number of trajectories)')
    plt.ylabel('Percentage of error')
    plt.legend()
    plt.savefig(os.path.join(get_figures_directory(), 'error-rate.pdf'))
    plt.close()

    # Second graph, model length over minimum density threshold
    plt.plot(thresholds, mip_model_length, linestyle=':', label='MIP')
    plt.plot(thresholds, mip_rectangle_model_length, linestyle='--', label='MIP-rectangles')
    plt.plot(thresholds, popular_region_model_length, label='PopularRegion')
    plt.xlabel('Minimum density threshold (% of total number of trajectories)')
    plt.ylabel('Number of integers')
    plt.legend()
    plt.savefig(os.path.join(get_figures_directory(), 'model-length.pdf'))
    plt.close()

