import sys
from typing import List, Tuple, Dict, Set
from collections import deque

def parse_input(file_path: str) -> List[List[int]]:
    grid = []
    with open(file_path, 'r') as f:
        for line in f.read().strip().splitlines():
            if line.strip() == "":
                continue
            row = [int(num) for num in line.split()]
            if len(row) != 9:
                raise ValueError(f"Invalid row length in {file_path}. Expected 9, got {len(row)}.")
            grid.append(row)
    if len(grid) != 9:
        raise ValueError(f"Invalid grid height in {file_path}. Expected 9, got {len(grid)}.")
    return grid

def print_grid(grid: List[List[int]]) -> None:
    output = '\n'.join(' '.join(map(str, row)) for row in grid)
    print(output, end='')

def initialize_domains(grid: List[List[int]]) -> Dict[Tuple[int, int], Set[int]]:
    domains = {}
    for r in range(9):
        for c in range(9):
            if grid[r][c] != 0:
                domains[(r, c)] = {grid[r][c]}
            else:
                possible = set(range(1, 10))
                # Remove values already in the same row and column.
                for i in range(9):
                    possible.discard(grid[r][i])
                    possible.discard(grid[i][c])
                # Remove values already in the same 3x3 box.
                br, bc = 3 * (r // 3), 3 * (c // 3)
                for i in range(3):
                    for j in range(3):
                        possible.discard(grid[br + i][bc + j])
                domains[(r, c)] = possible
    return domains

def get_neighbors() -> Dict[Tuple[int, int], Set[Tuple[int, int]]]:
    neighbors = {}
    for r in range(9):
        for c in range(9):
            cell_neighbors = set()
            # Same row and column.
            for i in range(9):
                if i != c:
                    cell_neighbors.add((r, i))
                if i != r:
                    cell_neighbors.add((i, c))
            # Same 3x3 box.
            br, bc = 3 * (r // 3), 3 * (c // 3)
            for i in range(3):
                for j in range(3):
                    nr, nc = br + i, bc + j
                    if (nr, nc) != (r, c):
                        cell_neighbors.add((nr, nc))
            neighbors[(r, c)] = cell_neighbors
    return neighbors

def ac3(domains: Dict[Tuple[int, int], Set[int]],
        neighbors: Dict[Tuple[int, int], Set[Tuple[int, int]]]) -> bool:
    queue = deque([(xi, xj) for xi in domains for xj in neighbors[xi]])
    while queue:
        xi, xj = queue.popleft()
        if revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False
            for xk in neighbors[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True

def revise(domains: Dict[Tuple[int, int], Set[int]],
           xi: Tuple[int, int],
           xj: Tuple[int, int]) -> bool:
    revised = False
    # For sudoku, the binary constraint is that two neighbors must have different values.
    # If xj is already assigned (i.e. its domain is a singleton),
    # then remove that value from xi’s domain.
    if len(domains[xj]) == 1:
        val = next(iter(domains[xj]))
        if val in domains[xi]:
            # Only remove if xi has other options.
            if len(domains[xi]) > 1:
                domains[xi].discard(val)
                revised = True
    return revised

def select_unassigned_variable(grid: List[List[int]],
                               domains: Dict[Tuple[int, int], Set[int]]) -> Tuple[int, int]:
    # Use the Minimum Remaining Values (MRV) heuristic.
    min_size = 10
    chosen = None
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                if len(domains[(r, c)]) < min_size:
                    min_size = len(domains[(r, c)])
                    chosen = (r, c)
    return chosen

def is_complete(grid: List[List[int]]) -> bool:
    return all(grid[r][c] != 0 for r in range(9) for c in range(9))

def is_valid_assignment(grid: List[List[int]], row: int, col: int, num: int) -> bool:
    # Check row and column.
    for i in range(9):
        if grid[row][i] == num or grid[i][col] == num:
            return False
    # Check the 3x3 box.
    br, bc = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if grid[br + i][bc + j] == num:
                return False
    return True

def backtracking_search(grid: List[List[int]],
                        domains: Dict[Tuple[int, int], Set[int]],
                        neighbors: Dict[Tuple[int, int], Set[Tuple[int, int]]]) -> bool:
    if is_complete(grid):
        return True

    cell = select_unassigned_variable(grid, domains)
    if cell is None:
        return False
    r, c = cell

    # Try each possible value in the cell's domain.
    for value in sorted(domains[cell]):
        if is_valid_assignment(grid, r, c, value):
            # Create deep copies for the new state.
            new_grid = [row[:] for row in grid]
            new_grid[r][c] = value
            new_domains = {cell_key: set(vals) for cell_key, vals in domains.items()}
            new_domains[(r, c)] = {value}

            # Forward checking: remove 'value' from all neighbors.
            failure = False
            for neighbor in neighbors[(r, c)]:
                if value in new_domains[neighbor]:
                    new_domains[neighbor].discard(value)
                    if not new_domains[neighbor]:
                        failure = True
                        break
            if failure:
                continue

            # Propagate constraints.
            if ac3(new_domains, neighbors):
                if backtracking_search(new_grid, new_domains, neighbors):
                    # If a solution is found, update the original grid.
                    for i in range(9):
                        grid[i] = new_grid[i][:]
                    return True
    return False

def main():
    # Read input either from a file (if a filename is provided) or from standard input.
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        grid = parse_input(file_path)
    else:
        input_lines = sys.stdin.read().strip().splitlines()
        grid = []
        for line in input_lines:
            if line.strip() == "":
                continue
            row = [int(num) for num in line.split()]
            grid.append(row)
        if len(grid) != 9 or any(len(row) != 9 for row in grid):
            raise ValueError("Invalid input grid. Must be 9 rows of 9 numbers each.")

    domains = initialize_domains(grid)
    neighbors = get_neighbors()

    # First, run AC3 to propagate initial constraints.
    if not ac3(domains, neighbors):
        print("No solution.")
        return

    # Then, search for a complete assignment using backtracking with forward checking.
    if backtracking_search(grid, domains, neighbors):
        print_grid(grid)
    else:
        print("No solution.")

if __name__ == '__main__':
    main()
