from fractions import Fraction

def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def settle(pos: int) -> int:
        while pos in jump:
            pos = jump[pos]
        return pos

    transitions = [[] for _ in range(n)]

    for pos in range(n):
        for roll in range(1, m + 1):
            landing = pos + roll
            if landing > n:
                landing = 2 * n - landing
            transitions[pos].append(settle(landing))

    reachable = {0}
    stack = [0]
    while stack:
        pos = stack.pop()
        for nxt in transitions[pos]:
            if nxt != n and nxt not in reachable:
                reachable.add(nxt)
                stack.append(nxt)

    can_finish = set()
    changed = True
    while changed:
        changed = False
        for pos in reachable - can_finish:
            if any(nxt == n or nxt in can_finish for nxt in transitions[pos]):
                can_finish.add(pos)
                changed = True

    if can_finish != reachable:
        return None

    states = sorted(reachable)
    index = {state: i for i, state in enumerate(states)}
    size = len(states)

    matrix = [
        [Fraction(0) for _ in range(size + 1)]
        for _ in range(size)
    ]

    for state, row in index.items():
        matrix[row][row] = Fraction(1)
        matrix[row][size] = Fraction(1)
        for nxt in transitions[state]:
            if nxt != n:
                matrix[row][index[nxt]] -= Fraction(1, m)

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

    result = matrix[index[0]][size]
    return [result.numerator, result.denominator]
