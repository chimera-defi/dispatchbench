from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump = {a: b for a, b in jumps}

    def land(q):
        while q in jump:
            q = jump[q]
        return q

    # trans[p] lists the m equally likely landing cells from p (n is absorbing).
    trans = [[] for _ in range(n + 1)]
    for p in range(n):
        for r in range(1, m + 1):
            q = p + r if p + r <= n else 2 * n - p - r
            trans[p].append(land(q))

    # States reachable from 0 without passing through the absorbing cell n.
    reach = {0}
    stack = [0]
    while stack:
        p = stack.pop()
        for q in trans[p]:
            if q != n and q not in reach:
                reach.add(q)
                stack.append(q)

    # States that can reach n at all (reverse reachability from n).
    rev = [[] for _ in range(n + 1)]
    for p in range(n):
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

    # If any reachable state cannot reach n, the game may never end.
    if any(p not in good for p in reach):
        return None

    states = sorted(reach)
    idx = {s: i for i, s in enumerate(states)}
    k = len(states)

    # Equations: E[p] - (1/m) * sum E[q] = 1, with E[n] = 0.
    M = [[Fraction(0)] * (k + 1) for _ in range(k)]
    for p in states:
        i = idx[p]
        M[i][i] += 1
        for q in trans[p]:
            if q != n:
                M[i][idx[q]] -= Fraction(1, m)
        M[i][k] = Fraction(1)

    # Gauss-Jordan elimination with exact fractions.
    for c in range(k):
        piv = next(r for r in range(c, k) if M[r][c] != 0)
        M[c], M[piv] = M[piv], M[c]
        pv = M[c][c]
        M[c] = [v / pv for v in M[c]]
        for r in range(k):
            if r != c and M[r][c] != 0:
                f = M[r][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]

    ans = M[idx[0]][k]
    return [ans.numerator, ans.denominator]
