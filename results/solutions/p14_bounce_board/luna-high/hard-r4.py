from collections import deque
from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump_map = {a: b for a, b in jumps}

    def resolve(cell: int) -> int:
        while cell in jump_map:
            cell = jump_map[cell]
        return cell

    transitions = [[] for _ in range(n + 1)]
    reverse = [[] for _ in range(n + 1)]

    for pos in range(n):
        for roll in range(1, m + 1):
            landing = pos + roll
            if landing > n:
                landing = 2 * n - landing
            landing = resolve(landing)
            transitions[pos].append(landing)
            reverse[landing].append(pos)

    reachable = {0}
    queue = deque([0])
    while queue:
        pos = queue.popleft()
        for dest in transitions[pos]:
            if dest != n and dest not in reachable:
                reachable.add(dest)
                queue.append(dest)

    can_reach_end = {n}
    queue = deque([n])
    while queue:
        pos = queue.popleft()
        for prev in reverse[pos]:
            if prev not in can_reach_end:
                can_reach_end.add(prev)
                queue.append(prev)

    if not reachable.issubset(can_reach_end):
        return None

    states = sorted(reachable)
    index = {pos: i for i, pos in enumerate(states)}
    size = len(states)
    matrix = [[Fraction(0) for _ in range(size + 1)] for _ in range(size)]

    for pos in states:
        row = index[pos]
        matrix[row][row] = Fraction(m)
        matrix[row][size] = Fraction(m)
        for dest in transitions[pos]:
            if dest != n:
                matrix[row][index[dest]] -= 1

    for col in range(size):
        pivot = next(row for row in range(col, size) if matrix[row][col] != 0)
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]

        for row in range(col + 1, size):
            if matrix[row][col] == 0:
                continue
            factor = matrix[row][col] / matrix[col][col]
            for j in range(col, size + 1):
                matrix[row][j] -= factor * matrix[col][j]

    solution = [Fraction(0) for _ in range(size)]
    for row in range(size - 1, -1, -1):
        value = matrix[row][size]
        for col in range(row + 1, size):
            value -= matrix[row][col] * solution[col]
        solution[row] = value / matrix[row][row]

    answer = solution[index[0]]
    return [answer.numerator, answer.denominator]
