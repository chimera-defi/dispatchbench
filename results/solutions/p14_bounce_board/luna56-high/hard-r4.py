from fractions import Fraction
from collections import deque


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def resolve(pos: int) -> int:
        while pos in jump:
            pos = jump[pos]
        return pos

    transitions = [[] for _ in range(n)]

    for p in range(n):
        for r in range(1, m + 1):
            pos = p + r
            if pos > n:
                pos = 2 * n - pos
            pos = resolve(pos)
            transitions[p].append(pos)

    reachable = set([0])
    queue = deque([0])

    while queue:
        p = queue.popleft()
        for q in transitions[p]:
            if q != n and q not in reachable:
                reachable.add(q)
                queue.append(q)

    can_reach_end = {n}
    changed = True
    while changed:
        changed = False
        for p in reachable:
            if p not in can_reach_end and any(q in can_reach_end for q in transitions[p]):
                can_reach_end.add(p)
                changed = True

    if 0 not in can_reach_end:
        return None

    states = sorted(reachable)
    index = {state: i for i, state in enumerate(states)}
    size = len(states)

    matrix = [[Fraction(0) for _ in range(size + 1)] for _ in range(size)]

    for p in states:
        i = index[p]
        matrix[i][i] = 1
        matrix[i][size] = 1

        for q in transitions[p]:
            if q != n:
                matrix[i][index[q]] -= Fraction(1, m)

    for col in range(size):
        pivot = next(row for row in range(col, size) if matrix[row][col] != 0)
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
