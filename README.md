# mining-ROI

This repository contains code to mine Regions Of Interest from trajectory data

## Format of the data
At the moment, the data must be formatted in the following way
  - One trajectory per line
  - Each trajectory is a sequence of tuple `(longitude,latitude)` separate by a space (no space after the last position in the sequence) : `(long1, lat1) (long2, lat2) ... (longN, latN)`

## Dependencies

To run the program, you need a valid [Gurobi](http://www.gurobi.com/) licence and the `gurobipy` python package. This project assumes Python 3.x
  
## How to use the program
To run the program, use the following command line
 
`python Main.py path size threshold` where
  - `path` is the path to the data set file
  - `size` is the size of the side of the grid (for now we only work with square grid)
  - `threshold` is the minimum density threshold (express as a percentage of the total number of trajectories)
  
So for example `python Main.py ./DatasetName 100 0.05` will run the algorithm on the DatasetName dataset with a grid of size 
100 by 100 and a minimum density threshold of 5 percent.

## See the results
Suppose we run the command `python Main.py DatasetName size threshold`. To see/use the resulting ROIs you can either
  1) Open the `.html` file in the `vizualisation` folder. Then you can add a file with the button and select in the folder
  `datasets` (created when first launching the program) the file `DatasetName-size-threshold.json`. This will then show the 
  ROIs on a map.
  2) All the informations and results are also stored in a pickle file in the `datasets` folder (using the same name as in 1,
  the file would be name `DatasetName.pkl`) which is basically the `Dataset` (file `miner/dataset.py`) python object for the particular data set (Python documentation to come).
  
