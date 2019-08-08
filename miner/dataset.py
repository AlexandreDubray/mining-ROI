# -*- coding: utf-8 -*-
import sys
import os
import pickle

script_dir = os.path.dirname(os.path.abspath(__file__))
datasets_dir = os.path.join(script_dir, '..', 'datasets')

class Dataset:

    def __init__(self, filepath):
        self.filepath = filepath
        self.dataset_name = self.filepath.split('/')[-1].split('.')[0]
        self.instances = dict()

    def create_instance(self, side_size, density_threshold, influx=None):
        if (side_size, density_threshold) in self.instances:
            return
        print("Creating instance for grid with side of size {} and density threshold {}".format(side_size, density_threshold))
        if influx is None:
            # No influx, need to parse the database
            self.__parse_data_file(side_size, density_threshold)
        else:
            # Influx is provided, there is an instance with the same size of grid
            # so we can avoid re-parsing the dataset
            print("Instance with same grid size found. Using it as a basis")
            for (side,threshold) in self.instances:
                if side == side_size:
                    instance = self.instances[(side,threshold)]
                    new_instance = {}
                    for key,value in instances.items():
                        new_instance[key] = value
                    new_instance['threshold'] = int(new_instance['number_trajectories']*density_threshold)
                    new_instance['binary_matrix'] = [[1 if new_instance['influx'][self.__map_cell_to_idx(row, col, side_size)] >= new_instance['threshold'] else 0 for col in range(side_size)] for row in range(side_size)]
                    self.instances[(side_size, density_threshold)] = new_instance
                    return

    def __parse_data_file(self, side_size, density_threshold):
        """
        Parsing the data file. For now we assume the following format:
            - One trajectory per line
            - Each trajectory is a list of string (longitude,latitude) separated by a space
            - Each latitude and longitude are floating number
        """
        print("Parsing data set")
        instance = {}
        with open(self.filepath, 'r') as f:
            lines = f.readlines()
        number_trajectories = len(lines)
        instance['number_trajectories'] = number_trajectories
        instance['threshold'] = int(density_threshold * number_trajectories)

        min_longitude = sys.maxsize
        max_longitude = -sys.maxsize
        min_latitude = sys.maxsize
        max_latitude = -sys.maxsize
        for line in lines:
            for pos in line[:-1].split(' '):
                (longitude,latitude) = self.__convert_pos(pos)
                min_longitude = longitude if longitude < min_longitude else min_longitude
                max_longitude = longitude if longitude > max_longitude else max_longitude
                min_latitude = latitude if latitude < min_latitude else min_latitude
                max_latitude = latitude if latitude > max_latitude else max_latitude
        ratio_longitude = (max_longitude-min_longitude)/side_size
        ratio_latitude = (max_latitude-min_latitude)/side_size

        instance['min_latitude'] = min_latitude
        instance['max_latitude'] = max_latitude
        instance['min_longitude'] = min_longitude
        instance['max_longitude'] = max_longitude
        instance['ratio_latitude'] = ratio_latitude
        instance['ratio_longitude'] = ratio_longitude

        influx = [0 for _ in range(side_size**2)]
        for line in lines:
            last_idx = None
            for pos in line.rstrip().split(' '):
                (longitude, latitude) = self.__convert_pos(pos)
                idx = self.__map_pos_to_idx(instance, side_size, longitude, latitude)
                if last_idx != idx:
                    influx[idx] += 1
                last_idx = idx
        binary_matrix = [[1 if influx[self.__map_cell_to_idx(row, col, side_size)] >= instance['threshold'] else 0 for col in range(side_size)] for row in range(side_size)]
        instance['influx'] = influx
        instance['binary_matrix'] = binary_matrix
        self.instances[(side_size, density_threshold)] = instance
        print("Data set parsed, updating pickle file")
        self.save_dataset()

    def __convert_pos(self, string):
        """Convert a string representation (lat,long) to a tuple of float"""
        pos = string[1:-1].split(',')
        return (float(pos[0]),float(pos[1]))

    def __map_pos_to_idx(self, instance, side_size, longitude, latitude):
        """Map a particular position to its index in the grid"""
        row = int((latitude - instance['min_latitude']) / instance['ratio_latitude']) if latitude != instance['max_latitude'] else side_size - 1
        column = int((longitude - instance['min_longitude']) / instance['ratio_longitude']) if longitude != instance['max_longitude'] else side_size - 1
        return self.__map_cell_to_idx(row, column, side_size)

    def __map_cell_to_idx(self, row, column, side_size):
        return row * side_size + column

    def save_dataset(self):
        save_path = os.path.join(datasets_dir, self.dataset_name + '.pkl')
        with open(save_path, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def __map_rectangle_to_polyline(self, instance, rectangle):
        (min_row, min_col, max_row, max_col) = rectangle
        low_latitude = instance['min_latitude'] + min_row * instance['ratio_latitude']
        high_latitude = instance['min_latitude'] + (max_row + 1) * instance['ratio_latitude']
        low_longitude = instance['min_longitude'] + min_col * instance['ratio_longitude']
        high_longitude = instance['min_longitude'] + (max_col + 1) * instance['ratio_longitude']
        return [[low_latitude,low_longitude],
                [low_latitude, high_longitude],
                [high_latitude,high_longitude],
                [high_latitude,low_longitude],
                [low_latitude, low_longitude]]

    def __map_circle_to_polyline(self, instance, circle):
        (row, col, radius) = circle
        polyline = list()
        # Start the polyline at the uppermost cell
        (upper_row, upper_col) = (row + radius, col)
        # We add the top border
        current_lat_long = [instance['min_latitude'] + (upper_row + 1) * instance['ratio_latitude'], instance['min_longitude'] + upper_col * instance['ratio_longitude']]
        polyline.append(current_lat_long.copy())
        current_lat_long = [current_lat_long[0], current_lat_long[1] + instance['ratio_longitude']]
        polyline.append(current_lat_long.copy())

        # Border until the rightmost border
        for _ in range(radius):
            current_lat_long[0] -= instance['ratio_latitude']
            polyline.append(current_lat_long.copy())
            current_lat_long[1] += instance['ratio_longitude']
            polyline.append(current_lat_long.copy())
        # We add the right border
        current_lat_long[0] -= instance['ratio_latitude']
        polyline.append(current_lat_long.copy())

        # Until the lowest border
        for _ in range(radius):
            current_lat_long[1] -= instance['ratio_longitude']
            polyline.append(current_lat_long.copy())
            current_lat_long[0] -= instance['ratio_latitude']
            polyline.append(current_lat_long.copy())
        #Lowest border
        current_lat_long[1] -= instance['ratio_longitude']
        polyline.append(current_lat_long.copy())

        # Until the left border
        for _ in range(radius):
            current_lat_long[0] += instance['ratio_latitude']
            polyline.append(current_lat_long.copy())
            current_lat_long[1] -= instance['ratio_longitude']
            polyline.append(current_lat_long.copy())
        #Left border
        current_lat_long[0] += instance['ratio_latitude']
        polyline.append(current_lat_long.copy())

        #Closing the polyline (until the upper most border
        for _ in range(radius):
            current_lat_long[1] += instance['ratio_longitude']
            polyline.append(current_lat_long.copy())
            current_lat_long[0] += instance['ratio_latitude']
            polyline.append(current_lat_long.copy())
        return polyline
    
    def set_solution(self, side_size, density_threshold, regions):
        """Set the find ROIs in the object and write a JSON file with the coordinate of the ROIs"""
        instance = self.instances[(side_size, density_threshold)]
        instance['regions'] = regions
        rectangles = regions[0]
        circles = regions[1]
        rectangles_polyline = [self.__map_rectangle_to_polyline(instance, rectangle) for rectangle in rectangles]
        circles_polyline = [self.__map_circle_to_polyline(instance, circle) for circle in circles]
        center = [(instance['min_latitude'] + instance['max_latitude'])/2.0,
                (instance['min_longitude'] + instance['max_longitude'])/2.0]
        json_str="""{{
    "center": {},
    "rectangles": {},
    "circles": {}
}}""".format(center, rectangles_polyline, circles_polyline)

        json_file = os.path.join(datasets_dir, self.dataset_name + '-' + str(side_size) + '-' + str(density_threshold) + '.json')
        with open(json_file, 'w') as f:
            f.write(json_str)

        instance['center_coordinate'] = center
        instance['rectangles_coordinates'] = rectangles_polyline
        instance['circles_coordinates'] = circles_polyline
        self.save_dataset()

