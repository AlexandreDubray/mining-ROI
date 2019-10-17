# mining-ROI

This repository contains code to mine Regions Of Interest from trajectory data.

## Installation
You can clone the repository and install the package with `pip install .`

## How to use

### The optimizer

The current optimizer will select a set of non-overlapping predefined weighted regions such that the sum
of the return regions is minimal. The following piece of code shows how to use the optimizer

```python
from roi_miner.miner.optimizer import optimize

regions = create_regions(6) # Function that create 6 regions
weights = [3,1,2,5,10,2] # One weight per function
overlaps = [[0,2,4],[1,2,3]] # Id of regions that are not allowed to be selected at the same time
selected_regions = optimize(regions, weight, overlaps)
```

The regions are any possible python objects, it does not count in the optimization process.
Each region must have a weight given that will be use to find the optimal solution (it can be positive, negative, float, etc..)
The `overlaps` variable define which set of ROI can not be taken together. For example, if we take the region `0`, then we
can not take the region `2` and `4` (and vice-versa).

### Predefined optimization

We provide pre-defined optimization/process to mine ROI. At the moment, we provide
- `grid_miner.MDL_optimizer` that find ROI on a grid while minimizing a MDL criterion. It need as argument a density grid and a density threshold:
```python
from roi_miner.miner.grid_miner.MDL_optimizer import mine_rois

mine_rois(density_matrix, threshold)
```
