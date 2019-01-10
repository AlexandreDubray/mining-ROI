#! /usr/bin/env python
# -*- coding: utf-8 -*-

from visualization.visu_map import visu_baseline, visu_mip, visu_initial

def main():
    # Run the baseline algorithm and the visualization of the results
    #
    # Mip should not be runned by default since it needs an academic
    # connection to run gurobi
    visu_initial()
    visu_baseline()
    visu_mip()
    visu_mip_vs_baseline()

if __name__ == '__main__':
    main()
