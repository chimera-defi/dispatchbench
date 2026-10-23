def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    from fractions import Fraction
    from collections import deque

    jump = {a: b for a, b in jumps}
    memo = {n: n}

    def settle(x: int) -> int:
        if x in memo:
            return memo[x]
        path = []
        while x in jump and x not in memo:
            path.append(x)
            x = jump[x]
        result = memo.get(x, x)
        for v in reversed(path):
            memo[v] = result
        return result

    def next_state(p: int, r: int) -> int:
        if p + r <= n:
            landing = p + r
        else:
            landing = 2 * n - p - r
        return settle(landing)

    transitions = {}
    reachable = {0}
    queue = deque([0])

    while queue:
        p = queue.popleft()
        outs = [next_state(p, r) for r in range(1, m + 1)]
        transitions[p] = outs
        for q in outs:
            if q != n and q not in reachable:
                reachable.add(q)
                queue.append(q)

    reverse = {x: [] for x in reachable}
    reverse[n] = []

    for p, outs in transitions.items():
        for q in outs:
            reverse.setdefault(q, []).append(p)

    can_finish = {n}
    queue = deque([n])
    while queue:
        x = queue.popleft()
        for p in reverse.get(x, []):
            if p not in can_finish:
                can_finish.add(p)
                queue.append(p)

    if 0 not in can_finish:
        return None

    states = [x for x in reachable if x != n]
    index = {x: i for i, x in enumerate(states)}
    size = len(states)

    matrix = [[Fraction(0) for _ in range(size + 1)] for _ in range(size)]

    for p in states:
        i = index[p]
        matrix[i][i] = Fraction(1)
        matrix[i][size] = Fraction(1)

        for q in transitions[p]:
            if q != n:
                matrix[i][index[q]] -= Fraction(1, m)

    for col in range(size):
        pivot = next(row for row in range(col, size) if matrix[row][col])
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]

        factor = matrix[col][col]
        for j in range(col, size + 1):
            matrix[col][j] /= factor

        for row in range(size):
            if row == col:
                continue
            factor = matrix[row][col]
            if factor:
                for j in range(col, size + 1):
                    matrix[row][j] -= factor * matrix[col][j]

    result = matrix[index[0]][size]
    return [result.numerator, result.denominator]
