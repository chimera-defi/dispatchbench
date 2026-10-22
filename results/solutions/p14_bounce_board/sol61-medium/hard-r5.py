from collections import deque
from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = dict(jumps)
    destination = [-1] * (n + 1)

    for cell in range(n + 1):
        if cell not in jump:
            destination[cell] = cell

    for cell in range(n + 1):
        path = []
        current = cell
        while destination[current] == -1:
            path.append(current)
            current = jump[current]
        end = destination[current]
        for current in path:
            destination[current] = end

    transitions = [{} for _ in range(n + 1)]
    reverse = [[] for _ in range(n + 1)]
    reachable = {0}
    queue = deque([0])

    while queue:
        cell = queue.popleft()
        if cell == n:
            continue

        counts = transitions[cell]
        for roll in range(1, m + 1):
            landing = cell + roll
            if landing > n:
                landing = 2 * n - landing
            landing = destination[landing]
            counts[landing] = counts.get(landing, 0) + 1

        for landing in counts:
            reverse[landing].append(cell)
            if landing not in reachable:
                reachable.add(landing)
                queue.append(landing)

    can_finish = {n}
    queue = deque([n])
    while queue:
        cell = queue.popleft()
        for previous in reverse[cell]:
            if previous not in can_finish:
                can_finish.add(previous)
                queue.append(previous)

    if not reachable.issubset(can_finish):
        return None

    states = sorted(reachable - {n})
    index = {cell: i for i, cell in enumerate(states)}
    size = len(states)

    # Integer system: m * E[cell] - sum(count * E[next]) = m.
    matrix = [[0] * (size + 1) for _ in range(size)]
    for i, cell in enumerate(states):
        matrix[i][i] = m
        matrix[i][size] = m
        for landing, count in transitions[cell].items():
            if landing != n:
                matrix[i][index[landing]] -= count

    # Fraction-free Bareiss elimination.
    previous_pivot = 1
    for k in range(size - 1):
        if matrix[k][k] == 0:
            pivot_row = next(
                i for i in range(k + 1, size) if matrix[i][k] != 0
            )
            matrix[k], matrix[pivot_row] = matrix[pivot_row], matrix[k]

        pivot = matrix[k][k]
        pivot_row = matrix[k]
        for i in range(k + 1, size):
            row = matrix[i]
            factor = row[k]
            for j in range(k + 1, size + 1):
                row[j] = (
                    pivot * row[j] - factor * pivot_row[j]
                ) // previous_pivot
            row[k] = 0
        previous_pivot = pivot

    expectation = [Fraction(0) for _ in range(size)]
    for i in range(size - 1, -1, -1):
        value = Fraction(matrix[i][size])
        for j in range(i + 1, size):
            if matrix[i][j]:
                value -= matrix[i][j] * expectation[j]
        expectation[i] = value / matrix[i][i]

    answer = expectation[index[0]]
    return [answer.numerator, answer.denominator]
