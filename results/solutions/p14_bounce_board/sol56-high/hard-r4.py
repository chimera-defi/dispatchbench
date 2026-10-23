from fractions import Fraction


def expected_turns(
    n: int, m: int, jumps: list[list[int]]
) -> list[int] | None:
    jump = {a: b for a, b in jumps}
    resolved: dict[int, int] = {}

    def resolve(cell: int) -> int:
        path = []
        while cell in jump and cell not in resolved:
            path.append(cell)
            cell = jump[cell]

        destination = resolved.get(cell, cell)
        for start in reversed(path):
            resolved[start] = destination
        return destination

    transitions: list[dict[int, int]] = []
    reverse_edges = [[] for _ in range(n + 1)]

    for cell in range(n):
        counts: dict[int, int] = {}
        for roll in range(1, m + 1):
            destination = cell + roll
            if destination > n:
                destination = 2 * n - destination
            destination = resolve(destination)
            counts[destination] = counts.get(destination, 0) + 1

        transitions.append(counts)
        for destination in counts:
            reverse_edges[destination].append(cell)

    reachable = {0}
    stack = [0]
    while stack:
        cell = stack.pop()
        for destination in transitions[cell]:
            if destination not in reachable:
                reachable.add(destination)
                if destination != n:
                    stack.append(destination)

    can_reach_end = {n}
    stack = [n]
    while stack:
        cell = stack.pop()
        for predecessor in reverse_edges[cell]:
            if predecessor not in can_reach_end:
                can_reach_end.add(predecessor)
                stack.append(predecessor)

    if not reachable.issubset(can_reach_end):
        return None

    states = sorted(reachable - {n})
    index = {cell: i for i, cell in enumerate(states)}
    size = len(states)

    matrix = [
        [Fraction(0) for _ in range(size + 1)]
        for _ in range(size)
    ]

    for cell in states:
        row = index[cell]
        matrix[row][row] = m
        matrix[row][size] = m

        for destination, count in transitions[cell].items():
            if destination != n:
                matrix[row][index[destination]] -= count

    for column in range(size):
        pivot = next(
            row
            for row in range(column, size)
            if matrix[row][column] != 0
        )
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]

        divisor = matrix[column][column]
        for j in range(column, size + 1):
            matrix[column][j] /= divisor

        for row in range(column + 1, size):
            factor = matrix[row][column]
            if factor == 0:
                continue
            matrix[row][column] = Fraction(0)
            for j in range(column + 1, size + 1):
                matrix[row][j] -= factor * matrix[column][j]

    solution = [Fraction(0) for _ in range(size)]
    for row in range(size - 1, -1, -1):
        value = matrix[row][size]
        for column in range(row + 1, size):
            value -= matrix[row][column] * solution[column]
        solution[row] = value

    result = solution[index[0]]
    return [result.numerator, result.denominator]
