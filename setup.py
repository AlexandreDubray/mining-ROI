from distutils.core import setup

setup(
    name='mining-ROI',
    version='0.0.1',
    packages=['roi_miner', 'roi_miner.grid_miners', 'roi_miner.grid_miners.MDL_miner', 'roi_miner.grid_miners.shapes'],
    author='Dubray Alexandre',
    install_requires=['gurobipy'],
    description='Mining constrained Regions of Interest on trajectory data'
)
