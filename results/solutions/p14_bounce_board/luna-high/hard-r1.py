from fractions import Fraction
from collections import deque

def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def resolve(pos: int) -> int:
        while pos in jump:
            pos = jump[pos]
        return pos

    transitions = {}
    for pos in range(n):
        counts = {}
        for roll in range(1, m + 1):
            landing = pos + roll
            if landing > n:
                landing = 2 * n - landing
            landing = resolve(landing)
            counts[landing] = counts.get(landing, 0) + 1
        transitions[pos] = counts

    reachable = {0}
    queue = deque([0])
    while queue:
        pos = queue.popleft()
        for dest in transitions[pos]:
            if dest != n and dest not in reachable:
                reachable.add(dest)
                queue.append(dest)

    reverse_edges = {pos: [] for pos in reachable}
    can_finish = set()
    queue = deque()
    for pos in reachable:
        if n in transitions[pos]:
            can_finish.add(pos)
            queue.append(pos)
        for dest in transitions[pos]:
            if dest != n and dest in reachable:
                reverse_edges[dest].append(pos)

    while queue:
        pos = queue.popleft()
        for prev in reverse_edges[pos]:
            if prev not in can_finish:
                can_finish.add(prev)
                queue.append(prev)

    if reachable - can_finish:
        return None

    states = sorted(reachable)
    index = {pos: i for i, pos in enumerate(states)}
    size = len(states)
    matrix = [[Fraction(0) for _ in range(size + 1)] for _ in range(size)]

    for pos in states:
        row = index[pos]
        matrix[row][row] = Fraction(m)
        matrix[row][size] = Fraction(m)
        for dest, count in transitions[pos].items():
            if dest != n:
                matrix[row][index[dest]] -= count

    for col in range(size):
        pivot = next(row for row in range(col, size) if matrix[row][col] != 0)
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]

        divisor = matrix[col][col]
        for j in range(col, size + 1):
            matrix[col][j] /= divisor

        for row in range(size):
            if row != col and matrix[row][col] != 0:
                factor = matrix[row][col]
                for j in range(col, size + 1):
                    matrix[row][j] -= factor * matrix[col][j]

    answer = matrix[index[0]][size]
    return [answer.numerator, answer.denominator]
