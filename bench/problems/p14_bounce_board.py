RUNG = 7
FUNC = "expected_turns"
SIGNATURE = "def expected_turns(n: int, m: int, jumps: list[list[int]]) -> list[int] | None:"
STATEMENT = """\
A board has cells `0` to `n`. A token starts on cell `0`, and the game ends when the token rests on cell `n`.

Each turn, roll a fair die with faces `1` to `m` and move the token forward by the roll. If that would pass cell `n`, the token bounces: from cell `p` with roll `r` and `p + r > n`, it lands on `2n - p - r`.

`jumps` is a list of pairs `[a, b]`. When the token lands on cell `a`, it moves to cell `b` straight away, in the same turn. If `b` is also the start of a jump, it keeps moving, until it lands on a cell that starts no jump. These moves do not take extra turns.

Return the expected number of turns until the game ends, as an exact fraction `[p, q]` in lowest terms with `q >= 1`. If there is a positive probability that the game never ends, return `None`.

Examples:
- `expected_turns(1, 1, [])` returns `[1, 1]`.
- `expected_turns(2, 2, [])` returns `[2, 1]`: a roll of 2 ends the game; a roll of 1 reaches cell 1, from which a 1 ends it and a 2 bounces back to cell 1.
- `expected_turns(3, 2, [[1, 0], [2, 0]])` returns `None`: every roll from cell 0 sends the token back to cell 0.
- `expected_turns(3, 3, [[2, 0]])` returns `[3, 1]`.

Constraints: `1 <= m <= n <= 80`. Every jump has `1 <= a <= n - 1`, `0 <= b <= n` and `a != b`. Jump starts are distinct. Following jumps never loops forever."""


def _land(n, jumps, c):
    seen = 0
    while c in jumps:
        c = jumps[c]; seen += 1
        assert seen <= n + 1, "jump cycle"
    return c


def _moves(n, m, jumps, p):
    out = []
    for r in range(1, m + 1):
        c = p + r
        if c > n: c = 2 * n - c
        out.append(_land(n, jumps, c))
    return out


def ref(n, m, jumps):
    from fractions import Fraction
    J = {a: b for a, b in jumps}
    # Reachable resting cells from 0 (cell 0 starts no jump), then which of them can reach n.
    reach = {0}; stack = [0]; adj = {}
    while stack:
        p = stack.pop()
        if p == n: continue
        adj[p] = _moves(n, m, J, p)
        for c in adj[p]:
            if c not in reach: reach.add(c); stack.append(c)
    if n not in reach: return None
    rev = {}
    for p, cs in adj.items():
        for c in cs: rev.setdefault(c, set()).add(p)
    good = {n}; stack = [n]
    while stack:
        c = stack.pop()
        for p in rev.get(c, ()):
            if p not in good: good.add(p); stack.append(p)
    if reach - good: return None
    # E[p] = 1 + (1/m) * sum E[c] over rolls, E[n] = 0, solved over the reachable non-final cells only.
    S = sorted(p for p in reach if p != n); idx = {p: i for i, p in enumerate(S)}; k = len(S)
    A = [[Fraction(0)] * (k + 1) for _ in range(k)]
    for p in S:
        i = idx[p]; A[i][i] += m; A[i][k] = Fraction(m)
        for c in adj[p]:
            if c != n: A[i][idx[c]] -= 1
    for col in range(k):
        piv = next(r for r in range(col, k) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [v / pv for v in A[col]]
        for r in range(k):
            if r != col and A[r][col] != 0:
                f = A[r][col]; A[r] = [a - f * b for a, b in zip(A[r], A[col])]
    e = A[idx[0]][k]
    return [e.numerator, e.denominator]


def brute(n, m, jumps):
    # Independent route: transitive closure by Floyd-Warshall over all cells, and Cramer's rule with
    # Leibniz determinants over the reachable non-final cells (only used on small boards).
    from fractions import Fraction
    from itertools import permutations
    J = dict((a, b) for a, b in jumps)

    def land(c):
        while c in J: c = J[c]
        return c
    cells = [c for c in range(n + 1) if c not in J]
    P = {p: [0] * (n + 1) for p in cells}
    for p in cells:
        if p == n: continue
        for r in range(1, m + 1):
            c = p + r if p + r <= n else 2 * n - p - r
            P[p][land(c)] += 1
    R = {p: {q: (p == q) or (p != n and P[p][q] > 0) for q in cells} for p in cells}
    for k in cells:
        for i in cells:
            if R[i][k]:
                for j in cells:
                    if R[k][j]: R[i][j] = True
    live = [p for p in cells if R[0][p]]
    if any(not R[p][n] for p in live): return None
    S = [p for p in live if p != n]; k = len(S)

    def det(M):
        tot = Fraction(0)
        for perm in permutations(range(len(M))):
            inv = sum(1 for i in range(len(perm)) for j in range(i + 1, len(perm)) if perm[i] > perm[j])
            prod = Fraction(1)
            for i, j in enumerate(perm): prod *= M[i][j]
            tot += -prod if inv % 2 else prod
        return tot
    M = [[Fraction(int(i == j)) - Fraction(P[S[i]][S[j]], m) for j in range(k)] for i in range(k)]
    D = det(M); i0 = S.index(0)
    Mi = [row[:i0] + [Fraction(1)] + row[i0 + 1:] for row in M]
    e = det(Mi) / D
    return [e.numerator, e.denominator]


def small(rng):
    # Leibniz determinants are k!: keep the board small enough for the brute force.
    n = rng.randint(1, 7); m = rng.randint(1, n)
    starts = list(range(1, n)); rng.shuffle(starts)
    jumps = []
    for a in starts[:rng.randint(0, min(4, len(starts)))]:
        b = rng.choice([x for x in range(0, n + 1) if x != a])
        jumps.append([a, b])
        J = dict(jumps); c = a; ok = True; steps = 0
        while c in J:
            c = J[c]; steps += 1
            if steps > n + 1: ok = False; break
        if not ok: jumps.pop()
    return (n, m, jumps)


def fixed():
    return [a for a, _ in EXAMPLES] + [(5, 1, []), (5, 5, [[4, 0]]), (4, 2, [[3, 1]]), (6, 2, [[5, 2], [3, 6]]), (6, 6, [[1, 5], [5, 0]]),
                                       (7, 3, [[6, 3], [4, 2], [5, 6]]), (4, 4, [[1, 4], [2, 4], [3, 4]]),
                                       (8, 2, [[4, 3], [5, 3], [1, 6]]), (12, 2, [[3, 9], [4, 9], [6, 5], [7, 5]])]


def _board(rng, n, m, k, back_bias):
    starts = rng.sample(range(1, n), k); jumps = []
    for a in starts:
        b = rng.randint(0, a - 1) if rng.random() < back_bias else rng.randint(a + 1, n)
        jumps.append([a, b])
        J = dict(jumps); c = a; steps = 0
        while c in J:
            c = J[c]; steps += 1
            if steps > n + 1: jumps.pop(); break
    return (n, m, jumps)


def big(rng):
    # A board where an unreachable trap would make a solve over all cells singular, and one that never finishes.
    trap = (60, 6, [[10, 30], [11, 30], [12, 30], [13, 30], [14, 30], [15, 30], [20, 2], [55, 40], [56, 41]])
    never = (40, 3, [[37, 5], [38, 5], [39, 5], [36, 5]])
    stuck = (60, 2, [[30, 29], [31, 29], [1, 40]])
    hidden = (80, 3, [[3, 70], [4, 70], [5, 70], [8, 6], [9, 6], [10, 6], [50, 2]])
    return [_board(rng, 80, 6, 20, 0.5), _board(rng, 80, 2, 30, 0.6), _board(rng, 75, 10, 25, 0.4), trap, never, stuck, hidden,
            (80, 80, []), _board(rng, 79, 4, 12, 0.9)]


EXAMPLES = [((1, 1, []), [1, 1]), ((2, 2, []), [2, 1]), ((3, 2, [[1, 0], [2, 0]]), None), ((3, 3, [[2, 0]]), [3, 1])]

WRONG = {
    "no_bounce_stay_put": """
from fractions import Fraction
def expected_turns(n, m, jumps):
    J = dict((a, b) for a, b in jumps)
    def land(c):
        while c in J: c = J[c]
        return c
    S = [c for c in range(n) if c not in J]; idx = {p: i for i, p in enumerate(S)}; k = len(S)
    A = [[Fraction(0)] * (k + 1) for _ in range(k)]
    for p in S:
        i = idx[p]; A[i][i] += m; A[i][k] = Fraction(m)
        for r in range(1, m + 1):
            c = land(p + r) if p + r <= n else p
            if c != n: A[i][idx[c]] -= 1
    for col in range(k):
        piv = next((r for r in range(col, k) if A[r][col] != 0), None)
        if piv is None: return None
        A[col], A[piv] = A[piv], A[col]; pv = A[col][col]; A[col] = [v / pv for v in A[col]]
        for r in range(k):
            if r != col and A[r][col] != 0:
                f = A[r][col]; A[r] = [a - f * b for a, b in zip(A[r], A[col])]
    e = A[idx[0]][k]
    return [e.numerator, e.denominator]
""",
    "solve_all_cells": """
from fractions import Fraction
def expected_turns(n, m, jumps):
    J = dict((a, b) for a, b in jumps)
    def land(c):
        while c in J: c = J[c]
        return c
    S = [c for c in range(n) if c not in J]; idx = {p: i for i, p in enumerate(S)}; k = len(S)
    A = [[Fraction(0)] * (k + 1) for _ in range(k)]
    for p in S:
        i = idx[p]; A[i][i] += m; A[i][k] = Fraction(m)
        for r in range(1, m + 1):
            c = land(p + r if p + r <= n else 2 * n - p - r)
            if c != n: A[i][idx[c]] -= 1
    for col in range(k):
        piv = next((r for r in range(col, k) if A[r][col] != 0), None)
        if piv is None: return None
        A[col], A[piv] = A[piv], A[col]; pv = A[col][col]; A[col] = [v / pv for v in A[col]]
        for r in range(k):
            if r != col and A[r][col] != 0:
                f = A[r][col]; A[r] = [a - f * b for a, b in zip(A[r], A[col])]
    e = A[idx[0]][k]
    return [e.numerator, e.denominator]
""",
    "single_jump_only": """
from fractions import Fraction
def expected_turns(n, m, jumps):
    J = dict((a, b) for a, b in jumps)
    reach = {0}; st = [0]; adj = {}
    while st:
        p = st.pop()
        if p == n: continue
        adj[p] = []
        for r in range(1, m + 1):
            c = p + r if p + r <= n else 2 * n - p - r
            c = J.get(c, c); adj[p].append(c)
            if c not in reach: reach.add(c); st.append(c)
    if n not in reach: return None
    S = sorted(p for p in reach if p != n); idx = {p: i for i, p in enumerate(S)}; k = len(S)
    A = [[Fraction(0)] * (k + 1) for _ in range(k)]
    for p in S:
        i = idx[p]; A[i][i] += m; A[i][k] = Fraction(m)
        for c in adj[p]:
            if c != n: A[i][idx[c]] -= 1
    for col in range(k):
        piv = next((r for r in range(col, k) if A[r][col] != 0), None)
        if piv is None: return None
        A[col], A[piv] = A[piv], A[col]; pv = A[col][col]; A[col] = [v / pv for v in A[col]]
        for r in range(k):
            if r != col and A[r][col] != 0:
                f = A[r][col]; A[r] = [a - f * b for a, b in zip(A[r], A[col])]
    e = A[idx[0]][k]
    return [e.numerator, e.denominator]
""",
    "float_solve_limit_denominator": """
from fractions import Fraction
def expected_turns(n, m, jumps):
    J = dict((a, b) for a, b in jumps)
    def land(c):
        while c in J: c = J[c]
        return c
    reach = {0}; st = [0]; adj = {}
    while st:
        p = st.pop()
        if p == n: continue
        adj[p] = [land(p + r if p + r <= n else 2 * n - p - r) for r in range(1, m + 1)]
        for c in adj[p]:
            if c not in reach: reach.add(c); st.append(c)
    if n not in reach: return None
    rev = {}
    for p, cs in adj.items():
        for c in cs: rev.setdefault(c, set()).add(p)
    good = {n}; st = [n]
    while st:
        c = st.pop()
        for p in rev.get(c, ()):
            if p not in good: good.add(p); st.append(p)
    if reach - good: return None
    S = sorted(p for p in reach if p != n); idx = {p: i for i, p in enumerate(S)}; k = len(S)
    A = [[0.0] * (k + 1) for _ in range(k)]
    for p in S:
        i = idx[p]; A[i][i] += m; A[i][k] = float(m)
        for c in adj[p]:
            if c != n: A[i][idx[c]] -= 1
    for col in range(k):
        piv = max(range(col, k), key=lambda r: abs(A[r][col]))
        A[col], A[piv] = A[piv], A[col]; pv = A[col][col]; A[col] = [v / pv for v in A[col]]
        for r in range(k):
            if r != col and A[r][col] != 0:
                f = A[r][col]; A[r] = [a - f * b for a, b in zip(A[r], A[col])]
    e = Fraction(A[idx[0]][k]).limit_denominator(10**9)
    return [e.numerator, e.denominator]
""",
}
