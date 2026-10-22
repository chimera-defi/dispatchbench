from fractions import Fraction
from collections import deque


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def land(x: int) -> int:
        while x in jump:
            x = jump[x]
        return x

    # Transitions from each live cell 0..n-1; each roll has probability 1/m.
    trans = {}
    for p in range(n):
        targets = []
        for r in range(1, m + 1):
            t = p + r if p + r <= n else 2 * n - p - r
            targets.append(land(t))
        trans[p] = targets

    # Cells reachable from the start (0), without passing through n.
    reach = {0}
    q = deque([0])
    while q:
        p = q.popleft()
        for t in trans[p]:
            if t < n and t not in reach:
                reach.add(t)
                q.append(t)

    # Cells that can reach n (reverse BFS from n).
    rev = {p: [] for p in range(n)}
    for p in range(n):
        for t in trans[p]:
            if t < n:
                rev[t].append(p)
    can_end = set()
    q = deque()
    for p in range(n):
        if n in trans[p]:
            can_end.add(p)
            q.append(p)
    while q:
        t = q.popleft()
        for p in rev[t]:
            if p not in can_end:
                can_end.add(p)
                q.append(p)

    # If some reachable cell cannot reach n, the game may never end.
    if any(p not in can_end for p in reach):
        return None

    # Solve E[p] = 1 + (1/m) * sum E[t] over the reachable (closed) set.
    states = sorted(reach)
    idx = {p: i for i, p in enumerate(states)}
    k = len(states)
    inv_m = Fraction(1, m)
    A = [[Fraction(0)] * k for _ in range(k)]
    b = [Fraction(1)] * k
    for p in states:
        i = idx[p]
        A[i][i] += 1
        for t in trans[p]:
            if t < n:
                A[i][idx[t]] -= inv_m

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
