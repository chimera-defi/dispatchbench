from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def resolve(c: int) -> int:
        while c in jump:
            c = jump[c]
        return c

    # Transitions from each non-terminal cell, one entry per die face.
    trans = {}
    for s in range(n):
        dests = []
        for r in range(1, m + 1):
            p = s + r
            if p > n:
                p = 2 * n - s - r
            dests.append(resolve(p))
        trans[s] = dests

    # Cells reachable from the start (cell 0), stopping at the terminal cell n.
    reachable = {0}
    stack = [0]
    while stack:
        s = stack.pop()
        for d in trans[s]:
            if d < n and d not in reachable:
                reachable.add(d)
                stack.append(d)

    # Cells that can reach the terminal cell n with positive probability.
    good = set()
    changed = True
    while changed:
        changed = False
        for s in range(n):
            if s in good:
                continue
            if any(d == n or d in good for d in trans[s]):
                good.add(s)
                changed = True

    # If some reachable cell cannot finish, the game may never end.
    if any(s not in good for s in reachable):
        return None

    # Solve E[s] = 1 + (1/m) * sum E[d] over reachable cells, with E[n] = 0.
    states = sorted(reachable)
    idx = {s: i for i, s in enumerate(states)}
    k = len(states)
    inv_m = Fraction(1, m)

    A = [[Fraction(0)] * k for _ in range(k)]
    b = [Fraction(1)] * k
    for s in states:
        i = idx[s]
        A[i][i] += 1
        for d in trans[s]:
            if d < n:
                A[i][idx[d]] -= inv_m

    # Gauss-Jordan elimination with exact fractions.
    for col in range(k):
        piv = next(r for r in range(col, k) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        b[col], b[piv] = b[piv], b[col]

        pv = A[col][col]
        A[col] = [v / pv for v in A[col]]
        b[col] = b[col] / pv

        for r in range(k):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [x - f * y for x, y in zip(A[r], A[col])]
                b[r] -= f * b[col]

    ans = b[idx[0]]
    return [ans.numerator, ans.denominator]
