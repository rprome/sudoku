
from typing import List, Tuple

def parse_input(file_path: str) -> List[List[int]]:
    grid = []
    with open(file_path, 'r') as f:
        for line in f.readlines():
            grid.append([int(num) for num in line.split()])
    return grid

def print_grid(grid: List[List[int]]) -> None:
    for row in grid:
        print(' '.join(map(str, row)))

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

def find_empty(grid: List[List[int]]) -> Tuple[int, int]:
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return i, j
    return -1, -1

def solve_sudoku(grid: List[List[int]]) -> bool:
    row, col = find_empty(grid)
    if row == -1 and col == -1:
        return True

    for num in range(1, 10):
        if is_valid(grid, row, col, num):
            grid[row][col] = num
            if solve_sudoku(grid):
                return True
            grid[row][col] = 0

    return False

if __name__ == '__main__':
    grid = parse_input('1.txt')
    if solve_sudoku(grid):
        print_grid(grid)
    else:
        print("No solution.")
