from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jm = {a: b for a, b in jumps}

    def resolve(q):
        while q in jm:
            q = jm[q]
        return q

    trans = {}
    for p in range(n):
        d = []
        for r in range(1, m + 1):
            q = p + r
            if q > n:
                q = 2 * n - p - r
            d.append(resolve(q))
        trans[p] = d

    # reachable states from 0
    reach = {0}
    stack = [0]
    while stack:
        p = stack.pop()
        for q in trans[p]:
            if q != n and q not in reach:
                reach.add(q)
                stack.append(q)

    # every reachable state must be able to reach n
    rev = {p: [] for p in range(n + 1)}
    for p in reach:
        for q in trans[p]:
            rev[q].append(p)
    good = {n}
    stack = [n]
    while stack:
        q = stack.pop()
        for p in rev[q]:
            if p not in good:
                good.add(p)
                stack.append(p)
    if any(p not in good for p in reach):
        return None

    states = sorted(reach)
    idx = {s: i for i, s in enumerate(states)}
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
        piv = None
        for r in range(c, k):
            if A[r][c] != 0:
                piv = r
                break
        if piv is None:
            return None
        A[c], A[piv] = A[piv], A[c]
        pv = A[c][c]
        A[c] = [x / pv for x in A[c]]
        for r in range(k):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                rowc = A[c]
                A[r] = [x - f * y for x, y in zip(A[r], rowc)]

    res = A[idx[0]][k]
    return [res.numerator, res.denominator]
