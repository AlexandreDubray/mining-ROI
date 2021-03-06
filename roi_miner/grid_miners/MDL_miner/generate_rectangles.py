from roi_miner.grid_miners.shapes.rectangle import Rectangle


def dense_cells_rectangle(sum_area, rectangle):
    (min_row, min_col, max_row, max_col) = rectangle
    return sum_area[max_row][max_col] - (sum_area[min_row - 1][max_col] if min_row > 0 else 0) - (
        sum_area[max_row][min_col - 1] if min_col > 0 else 0) + (
               sum_area[min_row - 1][min_col - 1] if min_row > 0 and min_col > 0 else 0)


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
    return max_height, max_width


def get_upper_bound_or_update(cell_to_bound, cell, sum_area):
    try:
        return cell_to_bound[cell]
    except KeyError:
        bound = compute_upper_bound(cell, sum_area)
        cell_to_bound[cell] = bound
        return bound


def cells_for_centers(sum_area, dense_cells, map_upbound, map_lowbound):
    cells_for_center = set()

    for cell in dense_cells:
        cells_for_center.add(cell)
        (max_height, max_width) = get_upper_bound_or_update(map_upbound, cell, sum_area)

        (row, col) = cell

        # The minimum width/height of a rectangle will be set according to the
        # closest dense cell (in manhattan distance), which is 0 for all dense cells
        map_lowbound[cell] = (0, 0)

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
                        map_lowbound[(next_row, next_col)] = min(dist_height, min_dist_height), min(dist_width, min_dist_width)
                except KeyError:
                    map_lowbound[(next_row, next_col)] = (dist_height, dist_width)
    return cells_for_center


# map each cell to its centers, there is four type of centers
def center_one_cell(cell, cells_for_center):
    return {cell}


def center_two_cells_row(cell, cells_for_center):
    cell_row = (cell[0] + 1, cell[1])
    if cell_row in cells_for_center:
        return {cell, cell_row}
    return None


def center_two_cells_col(cell, cells_for_center):
    cell_col = (cell[0], cell[1] + 1)
    if cell_col in cells_for_center:
        return {cell, cell_col}
    return None


def center_four_cells(cell, cells_for_center):
    cell_row = (cell[0] + 1, cell[1])
    cell_col = (cell[0], cell[1] + 1)
    cell_diag = (cell[0] + 1, cell[1] + 1)
    if cell_row in cells_for_center and cell_col in cells_for_center and cell_diag in cells_for_center:
        return {cell, cell_row, cell_col, cell_diag}
    return None


def dist_to_border(center, nrows, ncols):
    (min_row, min_col) = map(min, zip(*center))
    (max_row, max_col) = map(max, zip(*center))
    height_to_border = min(min_row, nrows - 1 - max_row)
    width_to_border = min(min_col, ncols - 1 - max_col)
    return height_to_border, width_to_border


def generate_from_center(matrix, lowbound, upbound, cells_for_center, center_map, selected, sum_area):
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

            for height in range(min_height, max_height + 1):
                for width in range(min_width, max_width + 1):
                    rect = (min_row - height, min_col - width, max_row + height, max_col + width)

                    cells_in_col = (max_row + height) - (min_row - height) + 1

                    first_col = (rect[0], rect[1], rect[2], rect[1])
                    dense_first_col = dense_cells_rectangle(sum_area, first_col)
                    non_dense_first_col = cells_in_col - dense_first_col

                    last_col = (rect[0], rect[3], rect[2], rect[3])
                    dense_last_col = dense_cells_rectangle(sum_area, last_col)
                    non_dense_last_col = cells_in_col - dense_last_col

                    if 4 + 2 * dense_first_col <= 2 * non_dense_first_col or 4 + 2 * dense_last_col <= 2 * non_dense_last_col:
                        break

                    rect = Rectangle(min_row - height, min_col - width, max_row + height, max_col + width, sum_area)
                    if rect.respect_constraints():
                        selected.append(rect)


def generate_rectangles(matrix, sum_area):
    dense_cells = set()
    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            if matrix[row][col] == 1:
                dense_cells.add((row, col))

    cell_to_upbound = {}
    cell_to_lowbound = {}

    center_cells = cells_for_centers(sum_area, dense_cells, cell_to_upbound, cell_to_lowbound)

    candidates = list()

    generate_from_center(matrix, cell_to_lowbound, cell_to_upbound, center_cells, center_one_cell, candidates, sum_area)
    generate_from_center(matrix, cell_to_lowbound, cell_to_upbound, center_cells, center_two_cells_row, candidates,
                         sum_area)
    generate_from_center(matrix, cell_to_lowbound, cell_to_upbound, center_cells, center_two_cells_col, candidates,
                         sum_area)
    generate_from_center(matrix, cell_to_lowbound, cell_to_upbound, center_cells, center_four_cells, candidates,
                         sum_area)
    return candidates
