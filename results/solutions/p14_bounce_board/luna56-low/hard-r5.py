from fractions import Fraction
from collections import deque


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def resolve(cell: int) -> int:
        seen = set()
        while cell in jump:
            if cell in seen:
                raise ValueError("Jump cycle")
            seen.add(cell)
            cell = jump[cell]
        return cell

    def move(pos: int, roll: int) -> int:
        landing = pos + roll
        if landing > n:
            landing = 2 * n - landing
        return resolve(landing)

    transitions = {}
    for pos in range(n):
        counts = {}
        for roll in range(1, m + 1):
            nxt = move(pos, roll)
            counts[nxt] = counts.get(nxt, 0) + 1
        transitions[pos] = counts

    reachable = set()
    queue = deque([0])
    while queue:
        state = queue.popleft()
        if state in reachable or state == n:
            continue
        reachable.add(state)
        for nxt in transitions[state]:
            if nxt != n and nxt not in reachable:
                queue.append(nxt)

    reverse = {state: [] for state in range(n + 1)}
    for state, counts in transitions.items():
        for nxt in counts:
            reverse[nxt].append(state)

    can_finish = {n}
    queue = deque([n])
    while queue:
        state = queue.popleft()
        for prev in reverse[state]:
            if prev not in can_finish:
                can_finish.add(prev)
                queue.append(prev)

    if any(state not in can_finish for state in reachable):
        return None

    states = sorted(reachable)
    index = {state: i for i, state in enumerate(states)}
    size = len(states)

    matrix = [[Fraction(0) for _ in range(size + 1)] for _ in range(size)]

    for state in states:
        row = index[state]
        matrix[row][row] = Fraction(1)
        matrix[row][size] = Fraction(1)
        for nxt, count in transitions[state].items():
            if nxt != n:
                matrix[row][index[nxt]] -= Fraction(count, m)

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
