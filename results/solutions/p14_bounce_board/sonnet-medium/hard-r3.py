from fractions import Fraction

def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jm = {a: b for a, b in jumps}

    def resolve(c):
        while c in jm:
            c = jm[c]
        return c

    def nxt(p):
        res = []
        for r in range(1, m + 1):
            q = p + r
            if q > n:
                q = 2 * n - p - r
            res.append(resolve(q))
        return res

    # reachable states from 0
    trans = {}
    stack = [0]
    seen = {0}
    while stack:
        p = stack.pop()
        if p == n:
            continue
        t = nxt(p)
        trans[p] = t
        for q in t:
            if q not in seen:
                seen.add(q)
                stack.append(q)

    # every reachable state must be able to reach n
    can = {n}
    changed = True
    while changed:
        changed = False
        for p, t in trans.items():
            if p not in can and any(q in can for q in t):
                can.add(p)
                changed = True
    if 0 not in can or any(p not in can for p in seen):
        return None

    states = sorted(p for p in seen if p != n)
    idx = {p: i for i, p in enumerate(states)}
    k = len(states)
    # (I - P) E = 1
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

    ans = A[idx[0]][k]
    return [ans.numerator, ans.denominator]
