from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def settle(cell: int) -> int:
        while cell in jump:
            cell = jump[cell]
        return cell

    transitions = {}
    graph = {i: set() for i in range(n + 1)}
    reverse = {i: set() for i in range(n + 1)}

    for pos in range(n):
        counts = {}
        for roll in range(1, m + 1):
            landing = pos + roll
            if landing > n:
                landing = 2 * n - landing
            dest = settle(landing)
            counts[dest] = counts.get(dest, 0) + 1
            graph[pos].add(dest)
            reverse[dest].add(pos)
        transitions[pos] = counts

    reachable = set()
    stack = [0]
    while stack:
        pos = stack.pop()
        if pos in reachable:
            continue
        reachable.add(pos)
        stack.extend(graph[pos] - reachable)

    can_reach_end = {n}
    stack = [n]
    while stack:
        pos = stack.pop()
        for prev in reverse[pos]:
            if prev not in can_reach_end:
                can_reach_end.add(prev)
                stack.append(prev)

    if any(pos not in can_reach_end for pos in reachable if pos != n):
        return None

    states = sorted(pos for pos in reachable if pos != n)
    index = {pos: i for i, pos in enumerate(states)}
    size = len(states)

    # Integer system: (mI - transition_counts) E = m.
    matrix = [[0] * (size + 1) for _ in range(size)]
    for pos, i in index.items():
        matrix[i][i] = m
        for dest, count in transitions[pos].items():
            if dest != n:
                matrix[i][index[dest]] -= count
        matrix[i][size] = m

    # Fraction-free Gaussian elimination.
    previous_pivot = 1
    for col in range(size - 1):
        pivot_row = next(
            (row for row in range(col, size) if matrix[row][col] != 0),
            None,
        )
        if pivot_row is None:
            return None
        if pivot_row != col:
            matrix[col], matrix[pivot_row] = matrix[pivot_row], matrix[col]

        pivot = matrix[col][col]
        for row in range(col + 1, size):
            factor = matrix[row][col]
            for j in range(col + 1, size + 1):
                value = matrix[row][j] * pivot - factor * matrix[col][j]
                matrix[row][j] = value // previous_pivot
            matrix[row][col] = 0
        previous_pivot = pivot

    if size and matrix[size - 1][size - 1] == 0:
        return None

    solution = [Fraction(0) for _ in range(size)]
    for row in range(size - 1, -1, -1):
        rhs = Fraction(matrix[row][size])
        for col in range(row + 1, size):
            rhs -= matrix[row][col] * solution[col]
        solution[row] = rhs / matrix[row][row]

    result = solution[index[0]]
    return [result.numerator, result.denominator]
