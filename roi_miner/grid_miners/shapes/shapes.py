# -*- coding: utf-8 -*-


class Shape:

    def __init__(self, sum_area):
        self.sum_area = sum_area
        self.constraints = list()

    def get_encoding_size(self):
        raise NotImplementedError()

    def get_nb_dense_cells(self):
        raise NotImplementedError()

    def get_nb_cells(self):
        raise NotImplementedError()

    def get_nb_non_dense_cells(self):
        return self.get_nb_cells() - self.get_nb_dense_cells()

    def get_description_length(self):
        non_dense = self.get_nb_non_dense_cells()
        dense = self.get_nb_dense_cells()
        return 2*(non_dense - dense) + self.get_encoding_size()

    def respect_constraints(self):
        raise NotImplementedError()

    def __contains__(self, cell):
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()
