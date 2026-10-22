from fractions import Fraction

def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jm = {a: b for a, b in jumps}

    def resolve(c):
        while c in jm:
            c = jm[c]
        return c

    trans = {}
    for p in range(n):
        if p in jm:
            continue
        lst = []
        for r in range(1, m + 1):
            q = p + r
            if q > n:
                q = 2 * n - q
            lst.append(resolve(q))
        trans[p] = lst

    # reachable states from 0
    start = resolve(0)
    seen = {start}
    stack = [start]
    while stack:
        p = stack.pop()
        if p == n:
            continue
        for q in trans[p]:
            if q not in seen:
                seen.add(q)
                stack.append(q)

    # states that can reach n
    rev = {}
    for p in seen:
        if p == n:
            continue
        for q in trans[p]:
            rev.setdefault(q, set()).add(p)
    good = {n}
    stack = [n]
    while stack:
        q = stack.pop()
        for p in rev.get(q, ()):
            if p not in good:
                good.add(p)
                stack.append(p)
    if any(p not in good for p in seen):
        return None
    if start == n:
        return [0, 1]

    states = sorted(p for p in seen if p != n)
    idx = {p: i for i, p in enumerate(states)}
    k = len(states)
    A = [[Fraction(0)] * (k + 1) for _ in range(k)]
    for p in states:
        i = idx[p]
        A[i][i] += 1
        A[i][k] = Fraction(1)
        for q in trans[p]:
            if q != n:
                A[i][idx[q]] -= Fraction(1, m)

    for c in range(k):
        piv = next(r for r in range(c, k) if A[r][c] != 0)
        A[c], A[piv] = A[piv], A[c]
        pv = A[c][c]
        A[c] = [x / pv for x in A[c]]
        for r in range(k):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                rowc = A[c]
                A[r] = [x - f * y for x, y in zip(A[r], rowc)]

    res = A[idx[start]][k]
    return [res.numerator, res.denominator]
