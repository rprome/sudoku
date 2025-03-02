"""
CSC 242 Project 2: Source Code
Authors: Rizouana Prome, Shafayet Fahim
Submission Date: March 3rd, 2025
Description: This .py file serves as the source code for a Sudoku solver.
Note: To run our program, use "python sudoku_solver.py <test_case.txt>"; it'll
detect the .txt file as the second argument (argv[1]).
"""

from collections import deque
import copy
import sys

def print_board(sudoku_board):
    for row in sudoku_board:
        print(" ".join(map(str, row)))
def initialize_domains(sudoku_board):
    domains = {}
    for row in range(9):
        for column in range(9):
            if sudoku_board[row][column] != 0: domains[(row, column)] = [sudoku_board[row][column]]
            else:
                possible = list(range(1, 10))
                for i in range(9):
                    if sudoku_board[row][i] in possible: possible.remove(sudoku_board[row][i])
                    if sudoku_board[i][column] in possible: possible.remove(sudoku_board[i][column])
                subgrid_row, subgrid_column = 3 * (row // 3), 3 * (column // 3)
                for i in range(3):
                    for j in range(3):
                        value = sudoku_board[subgrid_row + i][subgrid_column + j]
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
def fill_single_candidates(sudoku_board, domains, neighbors):
    while True:
        updated = False
        for (row, column), candidates in list(domains.items()):
            if sudoku_board[row][column] == 0 and len(candidates) == 1:
                value = candidates[0]
                sudoku_board[row][column] = value
                for neighbor_row, neighbor_column in neighbors[(row, column)]:
                    if value in domains[(neighbor_row, neighbor_column)]:
                        domains[(neighbor_row, neighbor_column)].remove(value)
                        if not domains[(neighbor_row, neighbor_column)]: return False
                updated = True
        if not updated: break
        result = ac3(domains, neighbors)
        if not result: return False
    return True
def select_unassigned_variable(sudoku_board, domains, neighbors):
    possible_values_count = 10
    chosen_cell = None
    unassigned_neighbors = -1
    for row in range(9):
        for column in range(9):
            if sudoku_board[row][column] == 0:
                domain_size = len(domains[(row, column)])
                degree = 0
                for (neighbor_row, neighbor_column) in neighbors[(row, column)]:
                    if sudoku_board[neighbor_row][neighbor_column] == 0: degree += 1
                if domain_size < possible_values_count or (domain_size == possible_values_count and degree > unassigned_neighbors):
                    possible_values_count = domain_size
                    unassigned_neighbors = degree
                    chosen_cell = (row, column)
    return chosen_cell
def order_domain_values(cell, domains, neighbors):
    conflict_counts = {}
    for value in domains[cell]:
        count = 0
        for neighbor in neighbors[cell]:
            if value in domains[neighbor]: count += 1
        conflict_counts[value] = count
    return sorted(domains[cell], key=conflict_counts.get)
def backtracking_search(sudoku_board, domains, neighbors):
    if all(sudoku_board[row][column] != 0 for row in range(9) for column in range(9)): return True
    cell = select_unassigned_variable(sudoku_board, domains, neighbors)
    if cell is None: return False
    row, column = cell
    for value in order_domain_values(cell, domains, neighbors):
        if value in domains[(row, column)]:
            sudoku_board[row][column] = value
            new_domains = copy.deepcopy(domains)
            new_domains[(row, column)] = [value]
            if ac3(new_domains, neighbors) and backtracking_search(sudoku_board, new_domains, neighbors): return True
            sudoku_board[row][column] = 0
    return False
def solve_sudoku(sudoku_board):
    domains = initialize_domains(sudoku_board)
    neighbors = get_neighbors()
    if not ac3(domains, neighbors):
        print("No solution.")
        return
    if not fill_single_candidates(sudoku_board, domains, neighbors):
        print("No solution.")
        return
    if backtracking_search(sudoku_board, domains, neighbors): print_board(sudoku_board)
    else:
        print("No solution.")
def read_sudoku_board(filename):
    with open(filename, 'r') as test_case:
        return [list(map(int, line.split())) for line in test_case if line.strip()]

sudoku_board_input = [list(map(int, line.split())) for line in sys.stdin if line.strip()]
solve_sudoku(sudoku_board_input)