from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = dict(jumps)
    destination = list(range(n + 1))
    for cell in range(n + 1):
        current = cell
        while current in jump:
            current = jump[current]
        destination[cell] = current

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
            target = destination[landing]
            counts[target] = counts.get(target, 0) + 1

        transitions[cell] = counts
        for target in counts:
            reverse[target].append(cell)
            if target not in reachable:
                reachable.add(target)
                pending.append(target)

    if n not in reachable:
        return None

    can_finish = {n}
    pending = [n]
    while pending:
        target = pending.pop()
        for cell in reverse[target]:
            if cell not in can_finish:
                can_finish.add(cell)
                pending.append(cell)

    if reachable - can_finish:
        return None

    states = sorted(reachable - {n})
    index = {cell: i for i, cell in enumerate(states)}
    size = len(states)

    # m * E[cell] - sum(count * E[target]) = m.
    matrix = [[0] * (size + 1) for _ in range(size)]
    for cell in states:
        i = index[cell]
        matrix[i][i] = m
        matrix[i][size] = m
        for target, count in transitions[cell].items():
            if target != n:
                matrix[i][index[target]] -= count

    # Fraction-free Gaussian elimination (Bareiss).
    previous_pivot = 1
    for k in range(size - 1):
        if matrix[k][k] == 0:
            pivot_row = next(
                i for i in range(k + 1, size) if matrix[i][k] != 0
            )
            matrix[k], matrix[pivot_row] = matrix[pivot_row], matrix[k]

        pivot = matrix[k][k]
        for i in range(k + 1, size):
            factor = matrix[i][k]
            for j in range(k + 1, size + 1):
                matrix[i][j] = (
                    pivot * matrix[i][j] - factor * matrix[k][j]
                ) // previous_pivot
            matrix[i][k] = 0
        previous_pivot = pivot

    expectation = [Fraction(0) for _ in range(size)]
    for i in range(size - 1, -1, -1):
        value = Fraction(matrix[i][size])
        for j in range(i + 1, size):
            value -= matrix[i][j] * expectation[j]
        expectation[i] = value / matrix[i][i]

    answer = expectation[index[0]]
    return [answer.numerator, answer.denominator]
