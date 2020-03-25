# -*- coding: utf-8 -*-

from roi_miner.grid_miners.shapes.shapes import Shape
from roi_miner.grid_miners.constraints import rectangle_constraints


class Rectangle(Shape):

    def __init__(self, min_row, min_col, max_row, max_col, sum_area):
        super().__init__(sum_area)
        assert (min_row >= 0 and min_col >= 0 and max_row >= 0 and max_col >= 0)
        self.min_row = min_row
        self.max_row = max_row
        self.min_col = min_col
        self.max_col = max_col

    def get_encoding_size(self):
        return 4

    def get_nb_dense_cells(self):
        dense_cells = self.sum_area[self.max_row][self.max_col]
        dense_cells -= self.sum_area[self.min_row - 1][self.max_col] if self.min_row > 0 else 0
        dense_cells -= self.sum_area[self.max_row][self.min_col - 1] if self.min_col > 0 else 0
        dense_cells += self.sum_area[self.min_row - 1][self.min_col - 1] if self.min_row > 0 and self.min_col > 0 else 0
        return dense_cells

    def get_nb_cells(self):
        return (self.max_row - self.min_row + 1) * (self.max_col - self.min_col + 1)

    def distance_to_cell(self, row, col):
        return min(abs(row - self.min_row), abs(row - self.max_row)) +\
               min(abs(col - self.min_col), abs(col - self.max_col))

    def respect_constraints(self):
        for f, args in rectangle_constraints:
            if not f(self, *args):
                return False
        return True

    def __contains__(self, cell):
        assert (type(cell) == tuple)
        assert (len(cell) == 2)
        (row, col) = cell
        return self.min_row <= row <= self.max_row and self.min_col <= col <= self.max_col

    def __iter__(self):
        for row in range(self.min_row, self.max_row + 1):
            for col in range(self.min_col, self.max_col + 1):
                yield row, col

    def __str__(self):
        return "Rectangle with lower left corner ({},{}) and upper right ({},{})".format(self.min_row, self.min_col,
                                                                                         self.max_row, self.max_col)
