# -*- coding: utf-8 -*-

from popular_region import PopularRegion
from popular_region.Utils import get_popular_region_data

from mip import mip_column
from mip.Utils import get_mip_data, create_sum_entry_matrix
from mip.candidate_generation.generate_rectangles_dense import generate_rectangles_dense
from mip.candidate_generation.generate_circles import generate_circles

from shared.Constant import side_size,set_side_size, set_percentage_threshold

from experiment.Utils import split_int

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

def runtime(print_latex=False):
    sizes = [100,150,200]
    thresholds = [2,5]

    number_dense_cells = {}
    number_mip_candidates = {}

    mip_runtime = {}
    mip_candidate_generation_time = {}

    popular_region_runtime = {}

    nruns = 20
    for size in sizes:
        for threshold in thresholds:
            print("{} {}".format(size, threshold))
            set_side_size(size)
            set_percentage_threshold(threshold)

            mip_data = get_mip_data()
            dense_cells = sum([sum(x) for x in mip_data])
            number_dense_cells[(size,threshold)] = dense_cells
            sum_entry_matrix = create_sum_entry_matrix(mip_data)
            number_mip_candidates[(size, threshold)] = len(generate_rectangles_dense(mip_data, sum_entry_matrix, {})) + len(generate_circles(mip_data, sum_entry_matrix, {}))

            popular_region_data = get_popular_region_data()
            mip_rt = 0
            mip_ct = 0
            popular_region_rt = 0
            for _ in range(nruns):
                mip_sol = mip_column.run(mip_data)
                mip_ct += mip_sol['time'][0]
                mip_rt += mip_sol['time'][1]

                popular_region_sol = PopularRegion.run(popular_region_data)
                popular_region_rt += popular_region_sol['time']
            print("MIP: generation of candidates %.4f seconds , optimization %.4f seconds" % (mip_ct/nruns, mip_rt/nruns))
            print("PopularRegion : run time %.4f seconds" % (popular_region_rt/nruns))
            mip_runtime[(size,threshold)] = mip_rt/nruns
            mip_candidate_generation_time[(size,threshold)] = mip_ct/nruns
            popular_region_runtime[(size,threshold)] = popular_region_rt/nruns

    print(popular_region_runtime)
    if print_latex:

        latex_table="""
\\begin{{table}}[!h]
\centering
\\resizebox{{\columnwidth}}{{!}}{{%
\\begin{{tabular}}{{|l|lll|lll|}}
\hline
Minimum density threshold & \multicolumn{{3}}{{c||}}{{2\%}} & \multicolumn{{3}}{{c|}}{{5\%}} \\\\
\hline \hline
Grid side size            & 100 & 150 & 200           & 100 & 150 & 200 \\\\
\hline
Number of dense cells ($|\mathcal{{G}}^*|$) & {} & {} & {} & {} & {} & {} \\\\ \hline
Number of MIP candidates                  & {} & {} & {} & {} & {} & {} \\\\
MIP candidate generation time (s)         & {:.3f} & {:.3f} & {:.3f} & {:.3f} & {:.3f} & {:.3f} \\\\
MIP optimization time (s)                 & {:.3f} & {:.3f} & {:.3f} & {:.3f} & {:.3f} & {:.3f} \\\\ \hline
\\textit{{PopularRegion}} run time (s)       & {:.3f} & {:.3f} & {:.3f} & {:.3f} & {:.3f} & {:.3f} \\\\ \hline
\end{{tabular}}%
}}
\caption{{Run time of the methods for different grid sizes and minimum density thresholds.}}
\label{{tab:runtime}}
\end{{table}}
        """.format(split_int(number_dense_cells[(100,2)]),
                split_int(number_dense_cells[(150,2)]),
                split_int(number_dense_cells[(200,2)]),
                split_int(number_dense_cells[(100,5)]),
                split_int(number_dense_cells[(150,5)]),
                split_int(number_dense_cells[(200,5)]),
                split_int(number_mip_candidates[(100,2)]),
                split_int(number_mip_candidates[(150,2)]),
                split_int(number_mip_candidates[(200,2)]),
                split_int(number_mip_candidates[(100,5)]),
                split_int(number_mip_candidates[(150,5)]),
                split_int(number_mip_candidates[(200,5)]),
                mip_candidate_generation_time[(100,2)],
                mip_candidate_generation_time[(150,2)],
                mip_candidate_generation_time[(200,2)],
                mip_candidate_generation_time[(100,5)],
                mip_candidate_generation_time[(150,5)],
                mip_candidate_generation_time[(200,5)],
                mip_runtime[(100,2)], mip_runtime[(150,2)], mip_runtime[(200,2)],
                mip_runtime[(100,5)], mip_runtime[(150,5)], mip_runtime[(200,5)],
                popular_region_runtime[(100,2)], popular_region_runtime[(150,2)],
                popular_region_runtime[(200,2)], popular_region_runtime[(100,5)],
                popular_region_runtime[(150,5)], 
                popular_region_runtime[(200,5)])
        print(latex_table)


