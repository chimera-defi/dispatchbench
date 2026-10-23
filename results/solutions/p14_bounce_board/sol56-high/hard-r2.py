from fractions import Fraction


def expected_turns(
    n: int, m: int, jumps: list[list[int]]
) -> list[int] | None:
    jump_to = {a: b for a, b in jumps}

    def settle(cell: int) -> int:
        while cell in jump_to:
            cell = jump_to[cell]
        return cell

    transitions: list[list[int]] = [[] for _ in range(n)]
    reverse: list[list[int]] = [[] for _ in range(n + 1)]

    for cell in range(n):
        for roll in range(1, m + 1):
            landing = cell + roll
            if landing > n:
                landing = 2 * n - landing
            landing = settle(landing)
            transitions[cell].append(landing)
            reverse[landing].append(cell)

    reachable = {0}
    stack = [0]
    while stack:
        cell = stack.pop()
        if cell == n:
            continue
        for nxt in transitions[cell]:
            if nxt not in reachable:
                reachable.add(nxt)
                stack.append(nxt)

    can_reach_end = {n}
    stack = [n]
    while stack:
        cell = stack.pop()
        for prev in reverse[cell]:
            if prev not in can_reach_end:
                can_reach_end.add(prev)
                stack.append(prev)

    if not reachable.issubset(can_reach_end):
        return None

    states = sorted(cell for cell in reachable if cell != n)
    index = {cell: i for i, cell in enumerate(states)}
    size = len(states)

    # Augmented system:
    # m * E[cell] - sum(E[next]) = m
    matrix = [[0] * (size + 1) for _ in range(size)]
    for cell, i in index.items():
        matrix[i][i] = m
        matrix[i][size] = m
        for nxt in transitions[cell]:
            if nxt != n:
                matrix[i][index[nxt]] -= 1

    # Fraction-free Bareiss elimination.
    previous_pivot = 1
    for col in range(size - 1):
        pivot_row = next(
            row for row in range(col, size) if matrix[row][col] != 0
        )
        if pivot_row != col:
            matrix[col], matrix[pivot_row] = matrix[pivot_row], matrix[col]

        pivot = matrix[col][col]
        for row in range(col + 1, size):
            leading = matrix[row][col]
            for j in range(col + 1, size + 1):
                matrix[row][j] = (
                    matrix[row][j] * pivot
                    - leading * matrix[col][j]
                ) // previous_pivot
            matrix[row][col] = 0
        previous_pivot = pivot

    solution = [Fraction(0) for _ in range(size)]
    for i in range(size - 1, -1, -1):
        rhs = Fraction(matrix[i][size])
        for j in range(i + 1, size):
            rhs -= matrix[i][j] * solution[j]
        solution[i] = rhs / matrix[i][i]

    answer = solution[index[0]]
    return [answer.numerator, answer.denominator]
