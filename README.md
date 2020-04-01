# mining-ROI

This repository contains code to mine Regions Of Interest from trajectory data.

## Installation

To run the optimization model you need the [gurobi solver](https://www.gurobi.com/) and its python package `gurobipy`.

You can clone the repository and install the package with `pip install .`

## How to use

The miner is separated in two part: the generation of the candidates and the optimizer. You can decide to use only the 
optimizer with your set of candidates, or to use the predefined grid-based MDL miner.

### Grid-based MDL miner

For a full example, you can look at the file `examples/ILP-example.py`.

#### Basic usage

First you need to load a grid of density and set a minimum density threshold. Then you can just run

```python
from roi_miner.grid_miners.MDL_miner.MDL_otpimizer import mine_rois

rois = mine_rois(grid_density, density_threshold)
```

which return a list of `Shapes` which are the optimals ROIs.

#### Adding constraints

You can add constraints on the shapes by registering a function with its arguments. At generation time, these constraints
will be checked. So for example, if we want to add a constraint on the diameter of the `Circle`, we can do

```python
from roi_miner.grid_miners.constraints import *

# Some code here ...

register_circle_constraint(circle_diameter_constraint, (2,5,))
```

We provide some initial constraint in `roi_miner.grid_miners.constraints` but you can define yours.

Finally, the call to `mines_rois` take two optionnal parameters `min_distance_rois` and `max_distance_rois`.
These are distance constraints between the ROIs. We can not have two ROIs at a distance less than `min_distance_rois` and 
more than `max_distance_rois`.


### Only use the optimizer

You can also only use the optimizer with your own candidates (or shapes). The signature of the optimization function is

```python
def optimize(candidates, weights, exclusive_constraints)
```
With `candidates` the set of candidates, `weights` their weights.
`exclusive_constraints` contains a list of set of candidates index that can not be taken together.
