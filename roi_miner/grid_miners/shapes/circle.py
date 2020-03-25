# -*- coding: utf-8 -*-
from roi_miner.grid_miners.shapes.shapes import Shape
from roi_miner.grid_miners.constraints import circle_constraints


class Circle(Shape):

    def __init__(self, row, col, radius, sum_area):
        super().__init__(sum_area)
        assert(radius > 0 and row > 0 and col > 0)
        self.row = row
        self.col = col
        self.radius = radius

    def get_encoding_size(self):
        return 3

    def __get_dense_cells_for_rect(self, min_row, min_col, max_row, max_col):
        dense_cells = self.sum_area[max_row][max_col]
        dense_cells -= self.sum_area[min_row - 1][max_col] if min_row > 0 else 0
        dense_cells -= self.sum_area[max_row][min_col - 1] if min_col > 0 else 0
        dense_cells += self.sum_area[min_row - 1][min_col - 1] if min_row > 0 and min_col > 0 else 0
        return dense_cells

    def get_nb_dense_cells(self):
        dense_cells = self.__get_dense_cells_for_rect(self.row, self.col - self.radius, self.row, self.col + self.radius)
        for r in range(1, self.radius + 1):
            dense_cells += self.__get_dense_cells_for_rect(self.row - r, self.col - self.radius + r, self.row - r, self.col + self.radius - r)
            dense_cells += self.__get_dense_cells_for_rect(self.row + r, self.col - self.radius + r, self.row + r, self.col + self.radius - r)
        return dense_cells

    def get_nb_cells(self):
        """
        circle of radius 1 -> 5 cells (1 + 4)
                     radius 2 -> 1 + 4 + 8
                     radius 3 -> 1 + 4 + 8 + 12

                     radius n -> 1 + sum_{i=1}^n (4i) = 1 + 4 * ((n (n + 1))/2)
        """
        ret = 1 + 4*((self.radius * (self.radius + 1))/2)
        assert(int(ret) == ret)
        return int(ret)

    def respect_constraints(self):
        for f, args in circle_constraints:
            if not f(self, *args):
                return False
        return True

    def __contains__(self, cell):
        assert(type(cell) == tuple)
        assert(len(cell) == 2)
        (row, col) = cell
        distance_from_center = abs(row - self.row) + abs(col - self.col)
        return distance_from_center <= self.radius

    def __iter__(self):
        for row in range(self.row - self.radius, self.row + self.radius + 1):
            d = abs(row - self.row)
            for col in range(self.col - self.radius + d, self.col + self.radius - d + 1):
                yield row, col

    def __str__(self):
        return "Circle centred in ({},{}) of radius {}".format(self.row, self.col, self.radius)
