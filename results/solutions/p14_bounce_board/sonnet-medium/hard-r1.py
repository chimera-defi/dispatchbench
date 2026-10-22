from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jmp = {a: b for a, b in jumps}

    def land(c):
        while c in jmp:
            c = jmp[c]
        return c

    def moves(p):
        res = []
        for r in range(1, m + 1):
            q = p + r
            if q > n:
                q = 2 * n - q
            res.append(land(q))
        return res

    # reachable states from 0
    reach = {0}
    stack = [0]
    adj = {}
    while stack:
        p = stack.pop()
        if p == n:
            adj[p] = []
            continue
        mv = moves(p)
        adj[p] = mv
        for q in mv:
            if q not in reach:
                reach.add(q)
                stack.append(q)

    if n not in reach:
        return None

    # every reachable state must be able to reach n
    radj = {s: [] for s in reach}
    for p, mv in adj.items():
        for q in mv:
            radj[q].append(p)
    good = {n}
    stack = [n]
    while stack:
        q = stack.pop()
        for p in radj[q]:
            if p not in good:
                good.add(p)
                stack.append(p)
    if good != reach:
        return None

    states = sorted(s for s in reach if s != n)
    idx = {s: i for i, s in enumerate(states)}
    k = len(states)
    A = [[Fraction(0)] * (k + 1) for _ in range(k)]
    inv = Fraction(1, m)
    for s in states:
        i = idx[s]
        A[i][i] += 1
        A[i][k] = Fraction(1)
        for q in adj[s]:
            if q != n:
                A[i][idx[q]] -= inv

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
        row = [x / pv for x in A[c]]
        A[c] = row
        for r in range(k):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                Ar = A[r]
                A[r] = [Ar[j] - f * row[j] for j in range(k + 1)]

    ans = A[idx[0]][k]
    return [ans.numerator, ans.denominator]
