from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = dict(jumps)
    resolved = [-1 if cell in jump else cell for cell in range(n + 1)]

    for start in jump:
        if resolved[start] != -1:
            continue
        path = []
        cell = start
        while resolved[cell] == -1:
            path.append(cell)
            cell = jump[cell]
        destination = resolved[cell]
        for cell in path:
            resolved[cell] = destination

    transitions = [{} for _ in range(n + 1)]
    reverse = [[] for _ in range(n + 1)]

    for cell in range(n):
        counts = transitions[cell]
        for roll in range(1, m + 1):
            landing = cell + roll
            if landing > n:
                landing = 2 * n - landing
            destination = resolved[landing]
            counts[destination] = counts.get(destination, 0) + 1
        for destination in counts:
            reverse[destination].append(cell)

    reachable = {0}
    queue = [0]
    for cell in queue:
        for destination in transitions[cell]:
            if destination not in reachable:
                reachable.add(destination)
                queue.append(destination)

    can_finish = {n}
    queue = [n]
    for cell in queue:
        for previous in reverse[cell]:
            if previous not in can_finish:
                can_finish.add(previous)
                queue.append(previous)

    if not reachable.issubset(can_finish):
        return None

    states = sorted(reachable - {n})
    index = {cell: i for i, cell in enumerate(states)}
    size = len(states)

    # m * E[cell] - sum(count * E[destination]) = m.
    matrix = [[0] * (size + 1) for _ in range(size)]
    for cell, i in index.items():
        matrix[i][i] = m
        matrix[i][size] = m
        for destination, count in transitions[cell].items():
            if destination != n:
                matrix[i][index[destination]] -= count

    # Fraction-free Gaussian elimination (Bareiss algorithm).
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
            if matrix[i][j]:
                value -= matrix[i][j] * expectations[j]
        expectations[i] = value / matrix[i][i]

    answer = expectations[index[0]]
    return [answer.numerator, answer.denominator]
