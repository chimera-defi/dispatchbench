from fractions import Fraction

def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def resolve(x: int) -> int:
        while x in jump:
            x = jump[x]
        return x

    transitions = {}

    def get_transitions(p: int):
        if p in transitions:
            return transitions[p]

        result = []
        for r in range(1, m + 1):
            x = p + r
            if x > n:
                x = 2 * n - x
            result.append(resolve(x))

        transitions[p] = result
        return result

    reachable = {0}
    stack = [0]

    while stack:
        p = stack.pop()
        for x in get_transitions(p):
            if x != n and x not in reachable:
                reachable.add(x)
                stack.append(x)

    can_finish = {n}
    changed = True
    while changed:
        changed = False
        for p in reachable:
            if p not in can_finish and any(x in can_finish for x in get_transitions(p)):
                can_finish.add(p)
                changed = True

    if 0 not in can_finish:
        return None

    states = sorted(reachable)
    index = {p: i for i, p in enumerate(states)}
    size = len(states)

    matrix = [[Fraction(0) for _ in range(size + 1)] for _ in range(size)]

    for p in states:
        i = index[p]
        matrix[i][i] = Fraction(1)
        matrix[i][size] = Fraction(1)

        for x in get_transitions(p):
            if x != n:
                matrix[i][index[x]] -= Fraction(1, m)

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

    answer = matrix[index[0]][size]
    return [answer.numerator, answer.denominator]
