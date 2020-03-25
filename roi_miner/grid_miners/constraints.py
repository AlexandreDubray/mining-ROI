# -*- coding: utf-8 -*-


# Constraints that applie on no-specific shapes
def density_constraint(shape):
    return shape.get_description_length() < 0


# Rectangle specific constraints
rectangle_constraints = list()


def register_rectangle_constraint(f, args):
    rectangle_constraints.append((f, args))


def rectangle_diameter_constraint(rectangle, lower_bound, higher_bound):
    return lower_bound <= (rectangle.max_row - rectangle.min_row + 1) + (rectangle.max_col - rectangle.min_row + 1) <= higher_bound


def rectangle_max_ratio_constraint(rectangle, ratio):
    height = rectangle.max_row - rectangle.min_row + 1
    width = rectangle.max_col - rectangle.min_col + 1
    return height <= ratio*width and width <= ratio*height


def rectangle_area_constraint(rectangle, lower_bound, higher_bound):
    return lower_bound <= rectangle.get_nb_cells() <= higher_bound


# Circle specific constraints
circle_constraints = list()


def register_circle_constraint(f, args):
    circle_constraints.append((f, args))


def circle_diameter_constraint(circle, lower_bound, higher_bound):
    return lower_bound <= 2*circle.radius + 1 <= higher_bound


def circle_area_constraint(circle, lower_bound, higher_bound):
    return lower_bound <= circle.get_nb_cells() <= higher_bound
