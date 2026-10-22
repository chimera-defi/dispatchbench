from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jm = {a: b for a, b in jumps}

    def settle(c):
        while c in jm:
            c = jm[c]
        return c

    trans = {}
    for p in range(n):
        cnt = {}
        for r in range(1, m + 1):
            q = p + r
            if q > n:
                q = 2 * n - q
            q = settle(q)
            cnt[q] = cnt.get(q, 0) + 1
        trans[p] = cnt

    # reachable states from 0
    reach = {0}
    stack = [0]
    while stack:
        s = stack.pop()
        if s == n:
            continue
        for t in trans[s]:
            if t not in reach:
                reach.add(t)
                stack.append(t)
    if n not in reach:
        return None

    # every reachable state must be able to reach n
    rev = {}
    for s in reach:
        if s == n:
            continue
        for t in trans[s]:
            rev.setdefault(t, []).append(s)
    good = {n}
    stack = [n]
    while stack:
        t = stack.pop()
        for s in rev.get(t, []):
            if s not in good:
                good.add(s)
                stack.append(s)
    if any(s not in good for s in reach):
        return None

    states = sorted(s for s in reach if s != n)
    idx = {s: i for i, s in enumerate(states)}
    k = len(states)
    A = [[Fraction(0)] * (k + 1) for _ in range(k)]
    for s in states:
        i = idx[s]
        A[i][i] += m
        for t, c in trans[s].items():
            if t != n:
                A[i][idx[t]] -= c
        A[i][k] = Fraction(m)

    for col in range(k):
        piv = None
        for r in range(col, k):
            if A[r][col] != 0:
                piv = r
                break
        if piv is None:
            return None
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [x / pv for x in A[col]]
        for r in range(k):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                rowc = A[col]
                A[r] = [x - f * y for x, y in zip(A[r], rowc)]

    res = A[idx[0]][k]
    return [res.numerator, res.denominator]
