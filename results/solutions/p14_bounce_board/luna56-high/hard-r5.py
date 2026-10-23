from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def resolve(cell: int) -> int:
        while cell in jump:
            cell = jump[cell]
        return cell

    def move(pos: int, roll: int) -> int:
        landing = pos + roll
        if landing > n:
            landing = 2 * n - landing
        return resolve(landing)

    transitions = {
        pos: [move(pos, roll) for roll in range(1, m + 1)]
        for pos in range(n)
    }

    reachable = set()
    stack = [0]
    while stack:
        pos = stack.pop()
        if pos in reachable:
            continue
        reachable.add(pos)
        for nxt in transitions[pos]:
            if nxt < n:
                stack.append(nxt)

    reverse = {pos: [] for pos in reachable}
    reverse[n] = []

    for pos in reachable:
        for nxt in transitions[pos]:
            reverse.setdefault(nxt, []).append(pos)

    can_reach_end = {n}
    stack = [n]
    while stack:
        pos = stack.pop()
        for prev in reverse.get(pos, []):
            if prev not in can_reach_end:
                can_reach_end.add(prev)
                stack.append(prev)

    if any(pos not in can_reach_end for pos in reachable):
        return None

    states = sorted(reachable)
    index = {state: i for i, state in enumerate(states)}
    size = len(states)

    matrix = [[Fraction(0) for _ in range(size + 1)] for _ in range(size)]

    for state, row in index.items():
        matrix[row][row] = m
        matrix[row][size] = m
        for nxt in transitions[state]:
            if nxt < n:
                matrix[row][index[nxt]] -= 1

    for col in range(size):
        pivot = next(row for row in range(col, size) if matrix[row][col])
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]

        pivot_value = matrix[col][col]
        for j in range(col, size + 1):
            matrix[col][j] /= pivot_value

        for row in range(size):
            if row == col:
                continue
            factor = matrix[row][col]
            if factor:
                for j in range(col, size + 1):
                    matrix[row][j] -= factor * matrix[col][j]

    result = matrix[index[0]][size]
    return [result.numerator, result.denominator]
