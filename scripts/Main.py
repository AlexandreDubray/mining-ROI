#! /usr/bin/env python
# -*- coding: utf-8 -*-


from popular_region import PopularRegion
from popular_region.Utils import get_popular_region_data

from mip import mip_column
from mip.Utils import get_mip_data

from experiment.MDL_analysis import MDL_on_threshold
from experiment.synthetic_exp import metrics_on_noise
from experiment.RandomSample import metrics_random_sample
from experiment.runtime import runtime

from shared.Utils import get_mip_shift

def main():
    mip_data = get_mip_data()
    mip_sol = mip_column.run(mip_data)

    popular_region_data = get_popular_region_data()
    popular_region_sol = PopularRegion.run(popular_region_data)

if __name__ == '__main__':
    main()
