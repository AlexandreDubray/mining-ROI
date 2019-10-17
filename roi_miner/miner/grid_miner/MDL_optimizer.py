# -*- coding: utf-8 -*-
from roi_miner.miner.optimizer import optimize

# Utilities to generate the rectangles
def dense_cells_rectangle(sum_area, rectangle):
    (min_row, min_col, max_row, max_col) = rectangle
    return sum_area[max_row][max_col] - (sum_area[min_row - 1][max_col] if min_row > 0 else 0) - (sum_area[max_row][min_col-1] if min_col > 0 else 0) + (sum_area[min_row-1][min_col-1] if min_row > 0 and min_col > 0 else 0)

def cells_rectangle(rectangle):
    (min_row, min_col, max_row, max_col) = rectangle
    return (max_row-min_row+1)*(max_col-min_col+1)

def weight_rectangle(sum_area, rectangle):
    (min_row, min_col, max_row, max_col) = rectangle
    height = max_row - min_row + 1
    width = max_col - min_col + 1
    # Ratio constraint to have more natural rectangles
    if height > 2*width or width > 2*height:
        return None
    dense_cells = dense_cells_rectangle(sum_area, rectangle)
    non_dense_cells = cells_rectangle(rectangle) - dense_cells
    
    # 4 + 2*dense_cells is the cost to remove the rectangle from the solution
    # 2*non_dense_cells is what we gain if we remove the rectangle from the solution
    if 4 + 2*dense_cells <= 2*non_dense_cells:
        return None
    return (dense_cells, non_dense_cells)

def rectangle_is_in_bound(rectangle, sum_area):
    nrow = len(sum_area)
    ncol = len(sum_area[0])

    return rect[0] <= rect[2] and rect[1] <= rect[3] and 0 <= rect[0] and rect[2] < nrow and 0 <= rect[1] and rect[3] < ncol

def compute_upper_bound(cell, sum_area):
    (row, col) = cell
    nrows = len(sum_area)
    ncols = len(sum_area[0])
    
    max_height = min(row, nrows - 1 - row)
    max_width = min(col, ncols - 1 - col)

    reduced = True
    while reduced and max_height > 0:
        reduced = False
        # The uppermost and lowest row are themselve rectangles
        upper_row = (row + max_height, col - max_width, row + max_height, col + max_width)
        lower_row = (row - max_height, col - max_width, row - max_height, col + max_width)
        if dense_cells_rectangle(sum_area, upper_row) == 0 or dense_cells_rectangle(sum_area, lower_row) == 0:
            # Since all sub-rectangles ending at one of these row will have a full side
            # of non-dense cells, we could prune them. Thus we just avoid enumerating them
            max_height -= 1
            reduced = True
    
    reduced = True
    while reduced and max_width > 0:
        reduced = False
        right_col = (row - max_height, col + max_width, row + max_height, col + max_width)
        left_col = (row - max_height, col - max_width, row + max_height, col - max_width)
        if dense_cells_rectangle(sum_area, right_col) == 0 or dense_cells_rectangle(sum_area, left_col) == 0:
            reduced = True
            max_width -= 1
    return (max_height, max_width)
    
def get_upper_bound_or_update(cell_to_bound, cell, sum_area):
    try:
        return cell_to_bound[cell]
    except KeyError:
        bound = compute_upper_bound(cell, sum_area)
        cell_to_bound[cell] = bound
        return bound
    
def cells_for_centers(matrix, sum_area, dense_cells, map_upbound, map_lowbound):
    nrows = len(matrix)
    ncols = len(matrix[0])
    
    cells_for_center = set()
    
    for cell in dense_cells:
        cells_for_center.add(cell)
        (max_height, max_width) = get_upper_bound_or_update(map_upbound, cell, sum_area)
        
        (row, col) = cell
        
        # The minimum width/height of a rectangle will be set according to the 
        # closest dense cell (in manhattan distance), which is 0 for all dense cells
        map_lowbound[cell] = (0,0)

        for next_row in range(row - max_height, row + max_height + 1):
            for next_col in range(col - max_width, row + max_width + 1):
                # We add all the cells, in the largest rectangle centered
                # in the cell, to the set of possible centers
                cells_for_center.add((next_row, next_col))
                
                (dist_height, dist_width) = (abs(row - next_row), abs(col - next_col))
                try:
                    (min_dist_height, min_dist_width) = map_lowbound[(next_row, next_col)]
                    if dist_height + dist_width < min_dist_height + min_dist_width:
                        map_lowbound[(next_row, next_col)] = (dist_height, dist_width)
                    elif dist_height + dist_width == min_dist_height + min_dist_width:
                        map_lowbound[(next_row, next_col)] = (min(dist_height, min_dist_height), min(dist_width, min_dist_width))
                except KeyError:
                    map_lowbound[(next_row, next_col)] = (dist_height, dist_width)       
    return cells_for_center

# map each cell to its centers, there is four type of centers
def center_one_cell(cell, cells_for_center):
    return {cell}

def center_two_cells_row(cell, cells_for_center):
    cell_row = (cell[0]+1, cell[1])
    if cell_row in cells_for_center:
        return {cell, cell_row}
    return None

def center_two_cells_col(cell, cells_for_center):
    cell_col = (cell[0], cell[1]+1)
    if cell_col in cells_for_center:
        return {cell, cell_col}
    return None
    
def center_four_cells(cell, cells_for_center):
    cell_row = (cell[0]+1, cell[1])
    cell_col = (cell[0], cell[1]+1)
    cell_diag = (cell[0]+1, cell[1]+1)
    if cell_row in cells_for_center and cell_col in cells_for_center and cell_diag in cells_for_center:
        return {cell, cell_row, cell_col, cell_diag}
    return None

def dist_to_border(center, nrows, ncols):
    (min_row, min_col) = map(min, zip(*center))
    (max_row, max_col) = map(max, zip(*center))
    height_to_border = min(min_row, nrows - 1 - max_row)
    width_to_border = min(min_col, ncols - 1 - max_col)
    return (height_to_border, width_to_border)

def generate_from_center(matrix, lowbound, upbound, cells_for_center, center_map, selected, sum_area, weight_map):
    nrows = len(matrix)
    ncols = len(matrix[0])
    
    for cell in cells_for_center:
        center = center_map(cell, cells_for_center)
        if center is not None:
            lowbounds = [lowbound[x] for x in center]
            upbounds = [get_upper_bound_or_update(upbound, x, sum_area) for x in center]
            (height_to_border, width_to_border) = dist_to_border(center, nrows, ncols)
            (min_height, min_width) = map(min, zip(*lowbounds))
            (max_height, max_width) = map(max, zip(*upbounds))
            max_height = min(max_height, height_to_border)
            max_width = min(max_width, width_to_border)
            
            (min_row, min_col) = map(min, zip(*center))
            (max_row, max_col) = map(max, zip(*center))

            for height in range(min_height, max_height+1):
                for width in range(min_width, max_width+1):
                    rect = (min_row - height, min_col - width, max_row + height, max_col + width)
                    
                    cells_in_col = rect[2] - rect[0] + 1
                    
                    first_col = (rect[0], rect[1], rect[2], rect[1])
                    dense_first_col = dense_cells_rectangle(sum_area, first_col)
                    non_dense_first_col = cells_in_col - dense_first_col
                    
                    last_col = (rect[0], rect[3], rect[2], rect[3])
                    dense_last_col = dense_cells_rectangle(sum_area, last_col)
                    non_dense_last_col = cells_in_col - dense_last_col
                    
                    if 4 + 2*dense_first_col <= 2*non_dense_first_col or 4 + 2*dense_last_col <= 2*non_dense_last_col:
                        break
                    
                    w = weight_rectangle(sum_area, rect)
                    if w is not None:
                        selected.append(rect)
                        weight_map[rect] = 2*(w[1]-w[0]) + 4

def generate_rectangles(matrix, sum_area, map_weight):
    dense_cells = set()
    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            if matrix[row][col] == 1:
                dense_cells.add((row,col))
    
    cell_to_upbound = {}
    cell_to_lowbound = {}
    
    center_cells = cells_for_centers(matrix, sum_area, dense_cells, cell_to_upbound, cell_to_lowbound)
    
    candidates = list()
    weight_map = {}

    generate_from_center(matrix, cell_to_lowbound, cell_to_upbound, center_cells, center_one_cell, candidates, sum_area, map_weight)
    generate_from_center(matrix, cell_to_lowbound, cell_to_upbound, center_cells, center_two_cells_row, candidates, sum_area, map_weight)
    generate_from_center(matrix, cell_to_lowbound, cell_to_upbound, center_cells, center_two_cells_col, candidates, sum_area, map_weight)
    generate_from_center(matrix, cell_to_lowbound, cell_to_upbound, center_cells, center_four_cells, candidates, sum_area, map_weight)
    return candidates

def compute_weight_circle(center, radius, sum_area):
    dense_cells = 0
    non_dense_cells = 0
    (row, col) = center
    central_rect = (row, col - radius, row, col + radius)
    dense = dense_cells_rectangle(sum_area, central_rect)
    dense_cells += dense
    non_dense_cells += radius*2 + 1 - dense
    
    for r in range(1, radius+1):
        upper_rect = (row + r, col - (radius - r), row + r, col + (radius - r))
        lower_rect = (row - r, col - (radius - r), row - r, col + (radius - r))
        nb_cell = upper_rect[3] - upper_rect[1] +1
        upper_dense = dense_cells_rectangle(sum_area, upper_rect)
        lower_dense = dense_cells_rectangle(sum_area, lower_rect)
        
        dense_cells += upper_dense + lower_dense
        non_dense_cells += 2*nb_cell - upper_dense - lower_dense
    
    if 3 + 2*dense_cells <= 2*non_dense_cells or dense_cells <= non_dense_cells:
        return None
    return (dense_cells, non_dense_cells)

def generate_circles(matrix, sum_area, map_weight):
    nrows = len(matrix)
    ncols = len(matrix[0])
    candidates = list()
    
    for row in range(nrows):
        for col in range(ncols):
            dist_row = min(row, nrows - 1 - row)
            dist_col = min(col, ncols - 1 - col)
            max_radius = min(dist_row, dist_col)
            
            # We do not consider the circles of radius 0 since it is already handled
            # by the rectangles
            for radius in range(1, max_radius + 1):
                w = compute_weight_circle((row,col), radius, sum_area)
                if w is not None:
                    candidates.append((row, col, radius))
                    map_weight[(row, col, radius)] = 2*(w[1]-w[0]) + 3
    return candidates

def _create_sum_area_matrix(matrix):
    nrows = len(matrix)
    ncols = len(matrix[0])
    sum_area = [[0 for _ in range(ncols)] for _ in range(nrows)]
    for row in range(nrows):
        for col in range(ncols):
            sum_area[row][col] = matrix[row][col] + (sum_area[row - 1][col] if row > 0 else 0) + (sum_area[row][col-1] if col > 0 else 0) - (sum_area[row-1][col-1] if col > 0 and row > 0 else 0)
    return sum_area

def _create_constraints(matrix, rectangles, circles):
    constraint_matrix = [[set() for _ in range(len(matrix[0]))] for _ in range(len(matrix))]
    for (k, (min_row, min_col, max_row, max_col)) in enumerate(rectangles):
        for r in range(min_row, max_row+1):
            for c in range(min_col, max_col+1):
                constraint_matrix[r][c].add(k)

    for (k, (row, col, rad)) in enumerate(circles):
        idx = k + len(rectangles)
        for r in range(rad+1):
            for c in range(col - rad + r, col +rad + 1 - r):
                constraint_matrix[row - r][c].add(idx)
                constraint_matrix[row + r][c].add(idx)

    overlaps = list()

    for row in range(len(constraint_matrix)):
        for col in range(len(constraint_matrix[0])):
            s = constraint_matrix[row][col]
            if len(s) > 0:
                overlaps.append(s)
    return overlaps

def mine_rois(density_grid, density_threshold):
    nrows = len(density_grid)
    ncols = len(density_grid[0])
    binary_matrix = [[1 if density_grid[row][col] >= density_threshold else 0 for col in range(ncols)] for row in range(nrows)]
    sum_area = _create_sum_area_matrix(binary_matrix)

    map_weight = {}
    rectangles = generate_rectangles(binary_matrix, sum_area, map_weight)
    circles = generate_circles(binary_matrix, sum_area, map_weight)

    candidates = rectangles + circles
    weights = [map_weight[x] for x in candidates]
    overlaps = _create_constraints(binary_matrix, rectangles, circles)
    return optimize(rectangles + circles, weights, overlaps)
