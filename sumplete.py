"""Solve Sumplete Puzzle using DLX."""
from itertools import combinations

from pydlx import create_network, search
from pydlx.link import Link


def read_puzzle(filename: str) -> list[list[int]]:
    """Read a sudoku puzzle and return as a list of strings."""
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.read().splitlines()
    return [[int(c) for c in l.split()] for l in lines]

def puzzle_to_matrix(mat: list[list[int]]) -> list[list[int]]:
    """Convert puzzle into an exact cover matrix."""
    retval = []

    # add a line for each combination in row
    size = len(mat[0]) - 1   # size of the puzzle
    for i, row in enumerate(mat[:-1]):
        for k in range(0, size + 1):
            # prepare a new row for the matrix
            row_template = [0] * size**2
            new_list = [0] * size
            new_list[i] = 1
            for _ in range(size):
                row_template.extend(new_list)

            for combo in combinations(enumerate(row[:-1]), k):
                if sum(val for (_, val) in combo) == row[-1]:
                    new_row = row_template.copy()
                    for (j, _) in combo:
                        new_row[i*size + j] = 1
                        new_row[size**2 + j*size + i] = 0
                    retval.append(new_row)

    # add a line for each combination in column
    transposed = list(zip(*mat))
    for j, col in enumerate(transposed):
        for k in range(0, size + 1):
            # prepare a new row for the matrix
            new_list = [0] * size
            new_list[j] = 1
            row_template = []
            for _ in range(size):
                row_template.extend(new_list)
            row_template.extend([0] * size**2)

            for combo in combinations(enumerate(col[:-1]), k):
                if sum(val for (_, val) in combo) == col[-1]:
                    new_row = row_template.copy()
                    for (i, _) in combo:
                        new_row[size**2 + i + j*size] = 1
                        new_row[i*size + j] = 0
                    retval.append(new_row)

    return retval

def is_row(root: Link, size: int) -> bool:
    """Return True if the solution is for a row, or False otherwise."""
    indices = []

    link = root
    indices.append(int(link.column.name))
    link = link.right
    while link != root:
        indices.append(int(link.column.name))
        link = link.right

    row_div = {i // size for i in indices if i < size**2}
    col_div = {i // size for i in indices if i >= size**2}
    row_mod = [i % size for i in indices if i < size**2]

    return (len(col_div) > 1 or (len(row_div) == 1 and len(row_mod) > 1),
            indices)

def solution_to_matrix(solution: list[Link]) -> list[list[int]]:
    """Convert a dlx solution into Sumplete solution.

    >>> puzzle = [[6, 6, 1, 6],
    ...           [2, 7, 9, 9],
    ...           [9, 4, 7, 0],
    ...           [2, 13, 0]]
    >>> matrix = puzzle_to_matrix(puzzle)
    >>> network = create_network(matrix)
    >>> for solution in search(network):
    ...     solution_mat = solution_to_matrix(solution)
    >>> target = [[0, 1, 0],
    ...           [1, 1, 0],
    ...           [0, 0, 0]]
    >>> all(i == j for i, j in zip(solution_mat, target))
    True
    """
    size = len(solution) // 2
    mat = [[0] * size for _ in range(size)]
    for root in solution:
        truth, indices = is_row(root, size)
        if truth:
            for i in indices:
                if i < size**2:
                    row, col = divmod(i, size)
                    mat[row][col % size] = 1
    return mat


if __name__ == "__main__":
    import sys

    puzzle = read_puzzle(sys.argv[1])
    matrix = puzzle_to_matrix(puzzle)
    network = create_network(matrix)

    for sol in search(network):
        sol_mat = solution_to_matrix(sol)
        for _ in sol_mat:
            print(_)
        print()
        break
