import sys
import os
from typing import List, Tuple, Dict, Set
from collections import defaultdict, deque

def parse_input(file_path: str) -> List[List[int]]:
    grid = []
    with open(file_path, 'r') as f:
        for line in f.read().strip().split('\n'):
            row = [int(num) for num in line.split()]
            if len(row) != 9:
                raise ValueError(f"Invalid row length in {file_path}. Expected 9, got {len(row)}.")
            grid.append(row)
    if len(grid) != 9:
        raise ValueError(f"Invalid grid height in {file_path}. Expected 9, got {len(grid)}.")
    return grid

def print_grid(grid: List[List[int]]) -> None:
    for row in grid:
        print(' '.join(map(str, row)))

def find_empty(grid: List[List[int]]) -> Tuple[int, int]:
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return i, j
    return -1, -1

def is_valid(grid: List[List[int]], row: int, col: int, num: int) -> bool:
    for i in range(9):
        if grid[row][i] == num or grid[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if grid[start_row + i][start_col + j] == num:
                return False
    return True

def ac3(grid: List[List[int]], domains: Dict[Tuple[int, int], Set[int]]) -> bool:
    queue = deque([(row, col) for row in range(9) for col in range(9) if grid[row][col] == 0])
    while queue:
        row, col = queue.popleft()
        if revise(grid, domains, row, col):
            if not domains[(row, col)]:
                return False
            for i in range(9):
                if i != col:
                    queue.append((row, i))
                if i != row:
                    queue.append((i, col))
    return True

def revise(grid: List[List[int]], domains: Dict[Tuple[int, int], Set[int]], row: int, col: int) -> bool:
    revised = False
    for value in list(domains[(row, col)]):
        if not is_valid(grid, row, col, value):
            domains[(row, col)].remove(value)
            revised = True
    return revised

def backtracking_search(grid: List[List[int]], domains: Dict[Tuple[int, int], Set[int]]) -> bool:
    row, col = find_empty(grid)
    if row == -1 and col == -1:
        return True
    for value in sorted(domains[(row, col)], key=lambda v: len(domains[(row, col)])):
        if is_valid(grid, row, col, value):
            grid[row][col] = value
            if backtracking_search(grid, domains):
                return True
            grid[row][col] = 0
    return False

def initialize_domains(grid: List[List[int]]) -> Dict[Tuple[int, int], Set[int]]:
    domains = defaultdict(lambda: set(range(1, 10)))
    for row in range(9):
        for col in range(9):
            if grid[row][col] != 0:
                domains[(row, col)] = {grid[row][col]}
            else:
                for num in range(1, 10):
                    if not is_valid(grid, row, col, num):
                        domains[(row, col)].discard(num)
    return domains

if __name__ == '__main__':
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
    for file_path in txt_files:
        try:
            grid = parse_input(file_path)
            print(f"Solving {file_path}:")
            domains = initialize_domains(grid)
            if ac3(grid, domains) and backtracking_search(grid, domains):
                print_grid(grid)
            else:
                print("No solution.")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        print("\n")
