from fractions import Fraction
from functools import lru_cache


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = dict(jumps)

    @lru_cache(None)
    def resolve(cell):
        if cell in jump:
            return resolve(jump[cell])
        return cell

    transitions = [{} for _ in range(n + 1)]
    reverse = [[] for _ in range(n + 1)]

    for cell in range(n):
        counts = transitions[cell]
        for roll in range(1, m + 1):
            landing = cell + roll
            if landing > n:
                landing = 2 * n - landing
            destination = resolve(landing)
            counts[destination] = counts.get(destination, 0) + 1

        for destination in counts:
            reverse[destination].append(cell)

    reachable = {0}
    stack = [0]
    while stack:
        cell = stack.pop()
        for destination in transitions[cell]:
            if destination not in reachable:
                reachable.add(destination)
                stack.append(destination)

    can_finish = {n}
    stack = [n]
    while stack:
        cell = stack.pop()
        for predecessor in reverse[cell]:
            if predecessor not in can_finish:
                can_finish.add(predecessor)
                stack.append(predecessor)

    if not reachable.issubset(can_finish):
        return None

    states = sorted(reachable - {n})
    index = {cell: i for i, cell in enumerate(states)}
    size = len(states)

    # Multiply the expectation equations by m to keep integer coefficients.
    matrix = [[0] * (size + 1) for _ in range(size)]
    for i, cell in enumerate(states):
        matrix[i][i] = m
        matrix[i][size] = m
        for destination, count in transitions[cell].items():
            if destination != n:
                matrix[i][index[destination]] -= count

    # Bareiss elimination preserves exact integer arithmetic.
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
            coefficient = row[k]
            for j in range(k + 1, size + 1):
                row[j] = (
                    pivot * row[j] - coefficient * pivot_row[j]
                ) // previous_pivot
            row[k] = 0
        previous_pivot = pivot

    expectations = [Fraction(0) for _ in range(size)]
    for i in range(size - 1, -1, -1):
        value = Fraction(matrix[i][size])
        for j in range(i + 1, size):
            value -= matrix[i][j] * expectations[j]
        expectations[i] = value / matrix[i][i]

    answer = expectations[index[0]]
    return [answer.numerator, answer.denominator]
