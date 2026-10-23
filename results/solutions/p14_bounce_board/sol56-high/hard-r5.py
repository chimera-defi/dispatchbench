from collections import Counter, defaultdict, deque
from fractions import Fraction


def expected_turns(
    n: int, m: int, jumps: list[list[int]]
) -> list[int] | None:
    jump = dict(jumps)
    resolved: dict[int, int] = {}

    def resolve(cell: int) -> int:
        if cell in resolved:
            return resolved[cell]

        path = []
        while cell in jump and cell not in resolved:
            path.append(cell)
            cell = jump[cell]

        destination = resolved.get(cell, cell)
        for start in path:
            resolved[start] = destination
        return destination

    transition_cache: dict[int, Counter[int]] = {}

    def transitions(cell: int) -> Counter[int]:
        if cell not in transition_cache:
            destinations = Counter()
            for roll in range(1, m + 1):
                landing = cell + roll
                if landing > n:
                    landing = 2 * n - landing
                destinations[resolve(landing)] += 1
            transition_cache[cell] = destinations
        return transition_cache[cell]

    reachable = {0}
    reverse_edges: dict[int, set[int]] = defaultdict(set)
    queue = deque([0])

    while queue:
        cell = queue.popleft()
        if cell == n:
            continue

        for destination in transitions(cell):
            reverse_edges[destination].add(cell)
            if destination not in reachable:
                reachable.add(destination)
                queue.append(destination)

    can_reach_end = {n}
    queue = deque([n])
    while queue:
        cell = queue.popleft()
        for predecessor in reverse_edges[cell]:
            if predecessor not in can_reach_end:
                can_reach_end.add(predecessor)
                queue.append(predecessor)

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

        for destination, count in transitions(cell).items():
            if destination != n:
                matrix[row][index[destination]] -= count

    for column in range(size):
        pivot_row = next(
            row for row in range(column, size)
            if matrix[row][column] != 0
        )
        matrix[column], matrix[pivot_row] = (
            matrix[pivot_row],
            matrix[column],
        )

        pivot = matrix[column][column]
        for row in range(column + 1, size):
            if matrix[row][column] == 0:
                continue
            factor = matrix[row][column] / pivot
            for col in range(column, size + 1):
                matrix[row][col] -= factor * matrix[column][col]

    solution = [Fraction(0) for _ in range(size)]
    for row in range(size - 1, -1, -1):
        value = matrix[row][size]
        for col in range(row + 1, size):
            value -= matrix[row][col] * solution[col]
        solution[row] = value / matrix[row][row]

    answer = solution[index[0]]
    return [answer.numerator, answer.denominator]
