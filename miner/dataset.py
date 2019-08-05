# -*- coding: utf-8 -*-
import sys
import os
import pickle

class Dataset:

    def __init__(self, filepath, save_directory, side_size, density_threshold):
        self.filepath = filepath
        self.save_directory = save_directory
        self.side_size = side_size
        self.grid_size = self.side_size**2
        self.density_threshold = density_threshold
        self.influx = [0 for _ in range(self.grid_size)]
        self.__parse_data_file()

    def __parse_data_file(self):
        """
        Parsing the data file. For now we assume the following format:
            - One trajectory per line
            - Each trajectory is a list of string (longitude,latitude) separated by a space
            - Each latitude and longitude are floating number
        """
        self.min_longitude = sys.maxsize
        self.max_longitude = -sys.maxsize
        self.min_latitude = sys.maxsize
        self.max_latitude = -sys.maxsize
        print('First pass on dataset for constants')
        with open(self.filepath, 'r') as f:
            lines = f.readlines()
        self.number_trajectories = len(lines)
        self.threshold = int(self.density_threshold * self.number_trajectories)
        counter = 0
        for line in lines:
            for pos in line[:-1].split(' '):
                (longitude,latitude) = self.__convert_pos(pos)
                self.min_longitude = longitude if longitude < self.min_longitude else self.min_longitude
                self.max_longitude = longitude if longitude > self.max_longitude else self.max_longitude
                self.min_latitude = latitude if latitude < self.min_latitude else self.min_latitude
                self.max_latitude = latitude if latitude > self.max_latitude else self.max_latitude
        self.ratio_longitude = (self.max_longitude-self.min_longitude)/self.side_size
        self.ratio_latitude = (self.max_latitude-self.min_longitude)/self.side_size

        print('Second pass on dataset, creating input matrix')
        for line in lines:
            last_idx = None
            for pos in line[:-1].split(' '):
                (longitude, latitude) = self.__convert_pos(pos)
                idx = self.__map_pos_to_idx(longitude, latitude)
                if last_idx != idx:
                    self.influx[idx] += 1
        self.binary_matrix = [[1 if self.influx[self.__map_cell_to_idx(row, col)] >= self.threshold else 0 for col in range(self.side_size)] for row in range(self.side_size)]

        self.save_dataset()

    def __convert_pos(self, string):
        """Convert a string representation (lat,long) to a tuple of float"""
        pos = string[1:-1].split(',')
        return (float(pos[0]),float(pos[1]))

    def __map_pos_to_idx(self, longitude, latitude):
        """Map a particular position to its index in the grid"""
        row = int((latitude - self.min_latitude)/self.ratio_longitude) if latitude != self.max_latitude else self.side_size - 1
        column = int((longitude - self.min_longitude)/self.ratio_longitude) if longitude != self.max_longitude else self.side_size - 1
        return self.__map_cell_to_idx(row, column)

    def __map_cell_to_idx(self, row, column):
        return row * self.side_size + column

    def get_data(self):
        return self.binary_matrix

    def save_dataset(self):
        dataset_name = self.filepath.split('/')[-1].split('.')[0]
        save_name = dataset_name + '-' + str(self.side_size) + '-' + str(self.density_threshold) + '.pkl'
        save_path = os.path.join(self.save_directory, save_name)
        with open(save_path, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

