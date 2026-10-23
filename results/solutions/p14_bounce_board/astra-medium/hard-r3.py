def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    from fractions import Fraction

    jump = dict(jumps)
    destination = [-1] * (n + 1)

    for start in range(n + 1):
        path = []
        cell = start
        while destination[cell] == -1 and cell in jump:
            path.append(cell)
            cell = jump[cell]

        if destination[cell] == -1:
            destination[cell] = cell

        end = destination[cell]
        for cell in path:
            destination[cell] = end

    transitions = [{} for _ in range(n + 1)]
    reverse = [[] for _ in range(n + 1)]

    for cell in range(n):
        counts = transitions[cell]
        for roll in range(1, m + 1):
            landing = cell + roll
            if landing > n:
                landing = 2 * n - landing
            target = destination[landing]
            counts[target] = counts.get(target, 0) + 1

        for target in counts:
            reverse[target].append(cell)

    reachable = {0}
    stack = [0]
    while stack:
        cell = stack.pop()
        for target in transitions[cell]:
            if target not in reachable:
                reachable.add(target)
                stack.append(target)

    can_finish = {n}
    stack = [n]
    while stack:
        cell = stack.pop()
        for previous in reverse[cell]:
            if previous not in can_finish:
                can_finish.add(previous)
                stack.append(previous)

    # A reachable state without a path to n implies nontermination
    # with positive probability.
    if not reachable <= can_finish:
        return None

    states = sorted(reachable - {n})
    index = {cell: i for i, cell in enumerate(states)}
    size = len(states)

    # m * E[cell] - sum(count * E[target]) = m, with E[n] = 0.
    matrix = [[0] * (size + 1) for _ in range(size)]
    for i, cell in enumerate(states):
        matrix[i][i] = m
        matrix[i][size] = m
        for target, count in transitions[cell].items():
            if target != n:
                matrix[i][index[target]] -= count

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

    expected = [Fraction(0) for _ in range(size)]
    for i in range(size - 1, -1, -1):
        value = Fraction(matrix[i][size])
        for j in range(i + 1, size):
            value -= matrix[i][j] * expected[j]
        expected[i] = value / matrix[i][i]

    answer = expected[index[0]]
    return [answer.numerator, answer.denominator]
