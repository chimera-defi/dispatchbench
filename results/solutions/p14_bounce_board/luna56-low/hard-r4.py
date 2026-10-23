from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def resolve(cell: int) -> int:
        while cell in jump:
            cell = jump[cell]
        return cell

    transitions = [[] for _ in range(n)]

    for p in range(n):
        for r in range(1, m + 1):
            landing = p + r
            if landing > n:
                landing = 2 * n - landing
            transitions[p].append(resolve(landing))

    reverse = [[] for _ in range(n + 1)]
    for state in range(n):
        for nxt in transitions[state]:
            reverse[nxt].append(state)

    can_finish = {n}
    stack = [n]
    while stack:
        state = stack.pop()
        for prev in reverse[state]:
            if prev not in can_finish:
                can_finish.add(prev)
                stack.append(prev)

    if 0 not in can_finish:
        return None

    states = sorted(can_finish - {n})
    index = {state: i for i, state in enumerate(states)}
    size = len(states)

    matrix = [
        [Fraction(0) for _ in range(size + 1)]
        for _ in range(size)
    ]

    for state in states:
        i = index[state]
        matrix[i][i] = Fraction(1)
        matrix[i][size] = Fraction(1)

        for nxt in transitions[state]:
            if nxt != n:
                matrix[i][index[nxt]] -= Fraction(1, m)

    for col in range(size):
        pivot = col
        while pivot < size and matrix[pivot][col] == 0:
            pivot += 1

        if pivot == size:
            return None

        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]

        divisor = matrix[col][col]
        for j in range(col, size + 1):
            matrix[col][j] /= divisor

        for row in range(size):
            if row == col or matrix[row][col] == 0:
                continue
            factor = matrix[row][col]
            for j in range(col, size + 1):
                matrix[row][j] -= factor * matrix[col][j]

    result = matrix[index[0]][size]
    return [result.numerator, result.denominator]
