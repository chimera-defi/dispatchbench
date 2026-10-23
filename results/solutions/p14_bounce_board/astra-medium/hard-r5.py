from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = dict(jumps)

    # Resolve each cell to where its entire jump chain ends.
    resolved = [None if cell in jump else cell for cell in range(n + 1)]
    for cell in range(n + 1):
        if resolved[cell] is not None:
            continue
        path = []
        current = cell
        while resolved[current] is None:
            path.append(current)
            current = jump[current]
        destination = resolved[current]
        for current in path:
            resolved[current] = destination

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
        for previous in reverse[cell]:
            if previous not in can_finish:
                can_finish.add(previous)
                stack.append(previous)

    # In a finite chain, absorption is certain iff every reachable
    # state has a path to the absorbing state.
    if not reachable.issubset(can_finish):
        return None

    states = sorted(reachable - {n})
    index = {cell: i for i, cell in enumerate(states)}
    size = len(states)

    # m * E[cell] - sum(count * E[destination]) = m.
    matrix = [[0] * (size + 1) for _ in range(size)]
    for i, cell in enumerate(states):
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
