from collections import deque
import copy
import sys

def print_grid(sudoku_grid):
    for row in sudoku_grid:
        print(" ".join(map(str, row)))
def initialize_domains(sudoku_grid):
    domains = {}
    for row in range(9):
        for column in range(9):
            if sudoku_grid[row][column] != 0: domains[(row, column)] = [sudoku_grid[row][column]]
            else:
                possible = list(range(1, 10))
                for i in range(9):
                    if sudoku_grid[row][i] in possible: possible.remove(sudoku_grid[row][i])
                    if sudoku_grid[i][column] in possible: possible.remove(sudoku_grid[i][column])
                box_row, box_column = 3 * (row // 3), 3 * (column // 3)
                for i in range(3):
                    for j in range(3):
                        value = sudoku_grid[box_row + i][box_column + j]
                        if value in possible: possible.remove(value)
                domains[(row, column)] = possible
    return domains
def get_neighbors():
    neighbors = {}
    for row in range(9):
        for column in range(9):
            cell_neighbors = []
            for i in range(9):
                if i != column and (row, i) not in cell_neighbors: cell_neighbors.append((row, i))
                if i != row and (i, column) not in cell_neighbors: cell_neighbors.append((i, column))
            box_row, box_column = 3 * (row // 3), 3 * (column // 3)
            for i in range(3):
                for j in range(3):
                    neighbor_row, neighbor_column = box_row + i, box_column + j
                    if (neighbor_row, neighbor_column) != (row, column) and (neighbor_row, neighbor_column) not in cell_neighbors:
                        cell_neighbors.append((neighbor_row, neighbor_column))
            neighbors[(row, column)] = cell_neighbors
    return neighbors
def ac3(domains, neighbors):
    queue_list = []
    for cell in domains:
        for neighbor in neighbors[cell]:
            queue_list.append((cell, neighbor))
    queue = deque(queue_list)
    while queue:
        current_cell, neighbor_cell = queue.popleft()
        if revise(domains, current_cell, neighbor_cell):
            if len(domains[current_cell]) == 0: return False
            for neighbor in neighbors[current_cell]:
                if neighbor != neighbor_cell: queue.append((neighbor, current_cell))
    return True
def revise(domains, target_cell, neighbor_cell):
    domain_changed = False
    for target_value in list(domains[target_cell]):
        alternative_found = False
        for neighbor_value in domains[neighbor_cell]:
            if target_value != neighbor_value:
                alternative_found = True
                break
        if not alternative_found:
            domains[target_cell].remove(target_value)
            domain_changed = True
    return domain_changed
def fill_single_candidates(sudoku_grid, domains, neighbors):
    while True:
        updated = False
        for (row, column), candidates in list(domains.items()):
            if sudoku_grid[row][column] == 0 and len(candidates) == 1:
                value = candidates[0]
                sudoku_grid[row][column] = value
                for n_row, n_col in neighbors[(row, column)]:
                    if value in domains[(n_row, n_col)]:
                        domains[(n_row, n_col)].remove(value)
                        if not domains[(n_row, n_col)]: return False
                updated = True
        if not updated: break
        result = ac3(domains, neighbors)
        if not result: return False
    return True

def select_unassigned_variable(sudoku_grid, domains, neighbors):
    min_size = 10
    chosen_cell = None
    max_degree = -1
    for row in range(9):
        for column in range(9):
            if sudoku_grid[row][column] == 0:
                domain_size = len(domains[(row, column)])
                degree = 0
                for (n_row, n_column) in neighbors[(row, column)]:
                    if sudoku_grid[n_row][n_column] == 0: degree += 1
                if domain_size < min_size or (domain_size == min_size and degree > max_degree):
                    min_size = domain_size
                    max_degree = degree
                    chosen_cell = (row, column)
    return chosen_cell

def order_domain_values(cell, domains, neighbors):
    def sort_key(value):
        count = 0
        for neighbor in neighbors[cell]:
            if value in domains[neighbor]: count += 1
        return count
    return sorted(domains[cell], key=sort_key)


def backtracking_search(sudoku_grid, domains, neighbors):
    if all(sudoku_grid[row][col] != 0 for row in range(9) for col in range(9)): return True
    cell = select_unassigned_variable(sudoku_grid, domains, neighbors)
    if cell is None: return False
    row, col = cell
    for value in order_domain_values(cell, domains, neighbors):
        if value in domains[(row, col)]:
            sudoku_grid[row][col] = value
            new_domains = copy.deepcopy(domains)
            new_domains[(row, col)] = [value]
            if ac3(new_domains, neighbors) and backtracking_search(sudoku_grid, new_domains, neighbors): return True
            sudoku_grid[row][col] = 0

    return False

def solve_sudoku(sudoku_grid):
    domains = initialize_domains(sudoku_grid)
    neighbors = get_neighbors()
    if not ac3(domains, neighbors):
        print("No solution.")
        return
    if not fill_single_candidates(sudoku_grid, domains, neighbors):
        print("No solution.")
        return
    if backtracking_search(sudoku_grid, domains, neighbors): print_grid(sudoku_grid)
    else:
        print("No solution.")

if __name__ == '__main__':
    try:
        filename = sys.argv[1]
        with open(filename, 'r') as f:
            grid = [list(map(int, line.split())) for line in f if line.strip()]
    except IndexError:
        grid = [list(map(int, input().split())) for _ in range(9)]
    solve_sudoku(grid)
