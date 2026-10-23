from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = dict(jumps)
    destination = [0] * (n + 1)

    for cell in range(n + 1):
        end = cell
        while end in jump:
            end = jump[end]
        destination[cell] = end

    # Build the reachable transition graph, counting die outcomes.
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
            end = destination[landing]
            counts[end] = counts.get(end, 0) + 1

        transitions[cell] = counts
        for end in counts:
            reverse[end].append(cell)
            if end not in reachable:
                reachable.add(end)
                pending.append(end)

    # In a finite chain, termination is almost sure exactly when every
    # reachable state has a path to the terminal state.
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

    # m * E[cell] - sum(count[end] * E[end]) = m, with E[n] = 0.
    matrix = [[0] * (size + 1) for _ in range(size)]
    for cell, i in index.items():
        matrix[i][i] = m
        matrix[i][size] = m
        for end, count in transitions[cell].items():
            if end != n:
                matrix[i][index[end]] -= count

    # Fraction-free Gaussian elimination (Bareiss algorithm).
    previous_pivot = 1
    for k in range(size - 1):
        if matrix[k][k] == 0:
            pivot_row = next(
                i for i in range(k + 1, size) if matrix[i][k] != 0
            )
            matrix[k], matrix[pivot_row] = matrix[pivot_row], matrix[k]

        pivot_row = matrix[k]
        pivot = pivot_row[k]
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
            value -= matrix[i][j] * expectation[j]
        expectation[i] = value / matrix[i][i]

    answer = expectation[index[0]]
    return [answer.numerator, answer.denominator]
