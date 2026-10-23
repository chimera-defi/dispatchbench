from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = dict(jumps)
    resolved = {cell: cell for cell in range(n + 1) if cell not in jump}

    for start in jump:
        path = []
        cell = start
        while cell not in resolved:
            path.append(cell)
            cell = jump[cell]
        destination = resolved[cell]
        for cell in path:
            resolved[cell] = destination

    # Build the transition graph reachable from the initial cell.
    transitions = {}
    reverse = {}
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
            destination = resolved[landing]
            counts[destination] = counts.get(destination, 0) + 1

        transitions[cell] = counts
        for destination in counts:
            reverse.setdefault(destination, []).append(cell)
            if destination not in reachable:
                reachable.add(destination)
                pending.append(destination)

    # In a finite chain, absorption is almost sure exactly when every
    # reachable state has a path to the terminal state.
    can_finish = {n}
    pending = [n]
    while pending:
        cell = pending.pop()
        for predecessor in reverse.get(cell, ()):
            if predecessor not in can_finish:
                can_finish.add(predecessor)
                pending.append(predecessor)

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
            multiplier = row[k]
            for j in range(k + 1, size + 1):
                row[j] = (
                    pivot * row[j] - multiplier * pivot_row[j]
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
