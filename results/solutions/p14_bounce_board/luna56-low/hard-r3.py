from fractions import Fraction
from collections import deque


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def resolve(pos: int) -> int:
        seen = set()
        while pos in jump:
            if pos in seen:
                return pos
            seen.add(pos)
            pos = jump[pos]
        return pos

    transitions = [[] for _ in range(n)]
    reverse = [[] for _ in range(n + 1)]

    for p in range(n):
        for r in range(1, m + 1):
            landing = p + r if p + r <= n else 2 * n - p - r
            landing = resolve(landing)
            transitions[p].append(landing)
            reverse[landing].append(p)

    reachable = set()
    stack = [0]
    while stack:
        p = stack.pop()
        if p in reachable:
            continue
        reachable.add(p)
        for nxt in transitions[p]:
            if nxt < n:
                stack.append(nxt)

    can_reach_end = {n}
    queue = deque([n])
    while queue:
        p = queue.popleft()
        for prev in reverse[p]:
            if prev not in can_reach_end:
                can_reach_end.add(prev)
                queue.append(prev)

    if any(p not in can_reach_end for p in reachable):
        return None

    states = sorted(reachable)
    index = {p: i for i, p in enumerate(states)}
    size = len(states)

    matrix = [
        [Fraction(0) for _ in range(size + 1)]
        for _ in range(size)
    ]

    for p in states:
        i = index[p]
        matrix[i][i] = Fraction(1)
        matrix[i][size] = Fraction(1)

        for nxt in transitions[p]:
            if nxt < n:
                matrix[i][index[nxt]] -= Fraction(1, m)

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
