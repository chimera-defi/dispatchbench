from fractions import Fraction


def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:
    jump_map = {a: b for a, b in jumps}

    def resolve(x: int) -> int:
        # Follow chained jumps until landing on a cell that starts no jump.
        while x in jump_map:
            x = jump_map[x]
        return x

    def targets(p: int) -> list[int]:
        # Resolved landing cell for each roll 1..m from cell p.
        res = []
        for r in range(1, m + 1):
            t = 2 * n - p - r if p + r > n else p + r
            res.append(resolve(t))
        return res

    # Explore the states reachable from 0 (cell n is absorbing, not expanded).
    reach = {0}
    stack = [0]
    trans = {}
    while stack:
        p = stack.pop()
        trans[p] = targets(p)
        for t in trans[p]:
            if t != n and t not in reach:
                reach.add(t)
                stack.append(t)

    # Reverse reachability: which reachable states can still reach n?
    rev = {s: [] for s in reach}
    for p in reach:
        for t in trans[p]:
            if t != n:
                rev[t].append(p)
    good = set()
    queue = [p for p in reach if n in trans[p]]
    good.update(queue)
    while queue:
        q = queue.pop()
        for p in rev[q]:
            if p not in good:
                good.add(p)
                queue.append(p)

    # If some reachable state cannot reach n, the game may never end.
    if any(s not in good for s in reach):
        return None

    # Every reachable state reaches n, so the expectation system is nonsingular.
    states = sorted(reach)
    idx = {s: i for i, s in enumerate(states)}
    k = len(states)

    # Augmented matrix for E[p] - (1/m) * sum E[t] = 1 over non-absorbing t.
    M = [[Fraction(0)] * (k + 1) for _ in range(k)]
    for p in states:
        i = idx[p]
        M[i][i] += 1
        M[i][k] = Fraction(1)
        for t in trans[p]:
            if t != n:
                M[i][idx[t]] -= Fraction(1, m)

    # Exact Gauss-Jordan elimination.
    for col in range(k):
        piv = next((r for r in range(col, k) if M[r][col] != 0), None)
        if piv is None:
            return None
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [v / pv for v in M[col]]
        for r in range(k):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [a - f * b for a, b in zip(M[r], M[col])]

    ans = M[idx[0]][k]
    return [ans.numerator, ans.denominator]
