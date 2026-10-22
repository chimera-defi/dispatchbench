from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = dict(jumps)
    destination = list(range(n + 1))

    for start in range(n + 1):
        cell = start
        while cell in jump:
            cell = jump[cell]
        destination[start] = cell

    transitions = {}
    reverse = [[] for _ in range(n + 1)]
    reachable = {0}
    pending = [0]

    while pending:
        cell = pending.pop()
        if cell == n:
            continue

        counts = {}
        for roll in range(1, m + 1):
            landing = cell + roll
            if landing > n:
                landing = 2 * n - landing
            landing = destination[landing]
            counts[landing] = counts.get(landing, 0) + 1

        transitions[cell] = counts
        for landing in counts:
            reverse[landing].append(cell)
            if landing not in reachable:
                reachable.add(landing)
                pending.append(landing)

    can_finish = {n}
    pending = [n]
    while pending:
        cell = pending.pop()
        for previous in reverse[cell]:
            if previous not in can_finish:
                can_finish.add(previous)
                pending.append(previous)

    if not reachable.issubset(can_finish):
        return None

    states = sorted(reachable - {n})
    index = {cell: i for i, cell in enumerate(states)}
    size = len(states)
    matrix = [[0] * (size + 1) for _ in range(size)]

    for cell in states:
        i = index[cell]
        matrix[i][i] = m
        matrix[i][size] = m
        for landing, count in transitions[cell].items():
            if landing != n:
                matrix[i][index[landing]] -= count

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
