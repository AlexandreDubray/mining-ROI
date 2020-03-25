# -*- coding: utf-8 -*-
from miner.grid_miners.shapes.shapes import Shape


class Cluster(Shape):

    def __init__(self, cells, sum_area=None):
        super().__init__(sum_area)
        self.cells = cells

    def __contains__(self, cell):
        return cell in self.cells

    def get_encoding_size(self):
        return 2*len(self.cells)

    def get_nb_dense_cells(self):
        return len(self.cells)

    def get_nb_cells(self):
        return len(self.cells)

    def respect_constraints(self):
        return True

    def __iter__(self):
        for row, col in self.cells:
            yield row, col

    def __str__(self):
        return "Cluster containing the cells : {}".format(' '.join([str(x) for x in self.cells]))
