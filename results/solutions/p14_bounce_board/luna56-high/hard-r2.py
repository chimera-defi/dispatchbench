from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def settle(x: int) -> int:
        while x in jump:
            x = jump[x]
        return x

    states = [x for x in range(n) if x not in jump]
    transitions = {}

    for p in states:
        outcomes = []
        for r in range(1, m + 1):
            landing = p + r
            if landing > n:
                landing = 2 * n - landing
            outcomes.append(settle(landing))
        transitions[p] = outcomes

    reachable = {0}
    stack = [0]
    while stack:
        p = stack.pop()
        for q in transitions[p]:
            if q != n and q not in reachable:
                reachable.add(q)
                stack.append(q)

    reverse = {p: [] for p in states}
    good = set()

    for p in states:
        for q in transitions[p]:
            if q == n:
                good.add(p)
            else:
                reverse[q].append(p)

    stack = list(good)
    while stack:
        p = stack.pop()
        for prev in reverse[p]:
            if prev not in good:
                good.add(prev)
                stack.append(prev)

    if any(p not in good for p in reachable):
        return None

    ordered = list(reachable)
    index = {p: i for i, p in enumerate(ordered)}
    size = len(ordered)

    matrix = [
        [Fraction(0) for _ in range(size + 1)]
        for _ in range(size)
    ]

    for p in ordered:
        i = index[p]
        matrix[i][i] = Fraction(m)
        matrix[i][size] = Fraction(m)

        for q in transitions[p]:
            if q != n:
                matrix[i][index[q]] -= 1

    for col in range(size):
        pivot = next(row for row in range(col, size) if matrix[row][col])
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]

        divisor = matrix[col][col]
        for j in range(col, size + 1):
            matrix[col][j] /= divisor

        for row in range(size):
            if row == col:
                continue
            factor = matrix[row][col]
            if factor:
                for j in range(col, size + 1):
                    matrix[row][j] -= factor * matrix[col][j]

    result = matrix[index[0]][size]
    return [result.numerator, result.denominator]
