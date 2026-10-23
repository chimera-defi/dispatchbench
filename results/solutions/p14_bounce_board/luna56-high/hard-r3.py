from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def resolve(cell: int) -> int:
        while cell in jump:
            cell = jump[cell]
        return cell

    transitions = [[] for _ in range(n + 1)]

    for p in range(n):
        for r in range(1, m + 1):
            landing = p + r if p + r <= n else 2 * n - p - r
            transitions[p].append(resolve(landing))

    reachable = set()
    stack = [0]
    while stack:
        state = stack.pop()
        if state in reachable:
            continue
        reachable.add(state)
        for nxt in transitions[state]:
            if nxt != n:
                stack.append(nxt)

    reverse = [[] for _ in range(n + 1)]
    for state in range(n):
        for nxt in transitions[state]:
            reverse[nxt].append(state)

    can_finish = set()
    stack = [n]
    while stack:
        state = stack.pop()
        if state in can_finish:
            continue
        can_finish.add(state)
        stack.extend(reverse[state])

    if any(state not in can_finish for state in reachable):
        return None

    size = n
    matrix = [[Fraction(0) for _ in range(size + 1)] for _ in range(size)]

    for i in range(size):
        matrix[i][i] = Fraction(m)
        for nxt in transitions[i]:
            if nxt != n:
                matrix[i][nxt] -= Fraction(1)
        matrix[i][size] = Fraction(m)

    for col in range(size):
        pivot = next(row for row in range(col, size) if matrix[row][col])
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]

        divisor = matrix[col][col]
        for j in range(col, size + 1):
            matrix[col][j] /= divisor

        for row in range(size):
            if row == col or not matrix[row][col]:
                continue
            factor = matrix[row][col]
            for j in range(col, size + 1):
                matrix[row][j] -= factor * matrix[col][j]

    result = matrix[0][size]
    return [result.numerator, result.denominator]
