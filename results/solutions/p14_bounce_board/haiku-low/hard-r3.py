from fractions import Fraction
from collections import deque


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jmap = {a: b for a, b in jumps}

    def resolve(x):
        while x in jmap:
            x = jmap[x]
        return x

    # Transitions from each non-terminal cell p in 0..n-1, one entry per die face
    trans = {}
    for p in range(n):
        dests = []
        for r in range(1, m + 1):
            q = p + r if p + r <= n else 2 * n - p - r
            dests.append(resolve(q))
        trans[p] = dests

    # Cells reachable from the start without passing through n
    reach = {0}
    dq = deque([0])
    while dq:
        p = dq.popleft()
        for q in trans[p]:
            if q != n and q not in reach:
                reach.add(q)
                dq.append(q)

    # Cells that can reach n (reverse BFS from n)
    rev = {i: [] for i in range(n)}
    for p in range(n):
        for q in trans[p]:
            if q != n:
                rev[q].append(p)
    can = set()
    dq = deque()
    for p in range(n):
        if n in trans[p]:
            can.add(p)
            dq.append(p)
    while dq:
        q = dq.popleft()
        for p in rev[q]:
            if p not in can:
                can.add(p)
                dq.append(p)

    # If some reachable cell can never reach n, the game may never end
    if any(p not in can for p in reach):
        return None

    # Every reachable cell reaches n, so the system below is nonsingular
    states = sorted(reach)
    idx = {s: i for i, s in enumerate(states)}
    k = len(states)

    # E[p] - (1/m) * sum E[q] = 1 for q != n
    A = [[Fraction(0)] * (k + 1) for _ in range(k)]
    inv_m = Fraction(1, m)
    for p in states:
        i = idx[p]
        A[i][i] += 1
        for q in trans[p]:
            if q != n:
                A[i][idx[q]] -= inv_m
        A[i][k] = Fraction(1)

    # Gauss-Jordan elimination with exact fractions
    for col in range(k):
        piv = next(r for r in range(col, k) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [x / pv for x in A[col]]
        for r in range(k):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * b for a, b in zip(A[r], A[col])]

    ans = A[idx[0]][k]
    return [ans.numerator, ans.denominator]
