"""Scalable inputs for the quality measurements (empirical time growth and memory).

Each problem gets `sized(pid, rng, n)`, returning one argument tuple whose work scales with ONE size parameter n,
valid under the problem's statement constraints at n up to MAX_N[pid] (asserted). The measurement uses
n0, 2*n0, 4*n0, 8*n0, so 8*n0 <= MAX_N. These generators are written for this measurement; they are not part of
the pre-registered tests and are not the grader's cases.

n0 was chosen from the constraints first (8*n0 <= max), then so that the reference `ref` takes about 50-300 ms at
n0 and at most a couple of seconds at 8*n0 where the constraint allows. "capped" = the statement's own maximum
limits n, so ref at n0 is faster than 50 ms.

| problem | n means | n0 | max | note |
|---|---|---|---|---|
| p01 | number of meetings; k = n // 300 | 12500 | 1e5 | capped |
| p02 | string length | 25000 | 2e5 | capped |
| p03 | number of ops; accounts = max(40, n // 10) | 2500 | 2e4 | capped |
| p04 | queue length; window k = n // 2 | 25000 | 2e5 | |
| p05 | nodes; edges = 5 n; 50 stations, 4 zones | 250 | 2000 | capped |
| p06 | expression length in characters | 1250 | 1e4 | capped |
| p07 | tree nodes, random tree | 25000 | 2e5 | |
| p08 | K in `WEEKLY K MO,TH`, count 50, from 1900-01-01 (a day-by-day scanner walks ~ 343 K days) | 130 | 1100 | capped (dates stop at 3000) |
| p09 | number of jobs, k = 4, heavy overlap | 37 | 300 | capped |
| p10 | length L of ONE banned string over ACGT, n = 10^18 - 1 (an automaton has L+1 states; "last L-1 chars" states have 4^(L-1)) | 2 | 20 | capped; log-n, so n is not the knob |
| p11 | array length; k = n // 20 | 12500 | 1e5 | capped |
| p12 | cells = 26 * rows (rows 12..96), range formulas | 312 | 2574 | capped |
| p13 | ring length n, 6 offsets in +-1e9, t = 2^59 - 1 (log t is fixed) | 600 | 5000 | |
| p14 | board size n, m = 6, n // 4 jumps; boards where the game cannot end are rejected | 10 | 80 | capped |
| p15 | number of ops, coordinates up to 1e9, NOT the strip length: n/2 single high-colour cells then n/2 full-width low paints (the known worst case for interval maps) | 12500 | 1e5 | capped |
"""
import random

from bench import problems

N0 = {"p01_overlap_minutes": 12500, "p02_squash": 25000, "p03_ledger": 2500, "p04_taller_within": 25000, "p05_pass_route": 250,
      "p06_calc": 1250, "p07_weighted_distance_sums": 25000, "p08_recur": 130, "p09_k_machine_schedule": 37, "p10_avoid_count": 2,
      "p11_best_average": 12500, "p12_sheet": 312, "p13_xor_ring": 600, "p14_bounce_board": 10, "p15_paint_erase": 12500}
MAX_N = {"p01_overlap_minutes": 10**5, "p02_squash": 2 * 10**5, "p03_ledger": 20000, "p04_taller_within": 2 * 10**5, "p05_pass_route": 2000,
         "p06_calc": 10000, "p07_weighted_distance_sums": 2 * 10**5, "p08_recur": 1100, "p09_k_machine_schedule": 300, "p10_avoid_count": 20,
         "p11_best_average": 10**5, "p12_sheet": 2574, "p13_xor_ring": 5000, "p14_bounce_board": 80, "p15_paint_erase": 10**5}
SIZE_PARAM = {
    "p01_overlap_minutes": "number of meetings (k = n // 300, coordinates up to 1e9)",
    "p02_squash": "string length (runs of 1-30 over 'ab1\\')",
    "p03_ledger": "number of operations (accounts = max(40, n // 10), so per-op full-state copies scale)",
    "p04_taller_within": "queue length (window k = n // 2, so O(n*k) differs from O(n log n))",
    "p05_pass_route": "number of stops (edges = 5 n, 50 stations, 4 zones)",
    "p06_calc": "expression length in characters",
    "p07_weighted_distance_sums": "number of tree nodes (random tree)",
    "p08_recur": "K in 'WEEKLY K MO,TH' with count 50 from 1900-01-01: days a day-by-day scanner must walk is about 343*K",
    "p09_k_machine_schedule": "number of jobs (k = 4, concurrency far above k)",
    "p10_avoid_count": "length L of one banned string over ACGT (n fixed at 10^18 - 1): automaton states L+1 vs 4^(L-1) for last-chars states",
    "p11_best_average": "array length (k = n // 20)",
    "p12_sheet": "number of cells (26 columns x rows), each a MAX/MIN range formula",
    "p13_xor_ring": "ring length n (t = 2^59 - 1 fixed, 6 random offsets)",
    "p14_bounce_board": "board size n (m = 6, n // 4 jumps; boards that never end are rejected)",
    "p15_paint_erase": "number of ops, coordinates up to 1e9 (comb: n/2 single high-colour cells, then n/2 full-width paints)",
}


def _load(pid):
    return problems.load(pid)


def p01(rng, n):
    ms = []
    for _ in range(n):
        s = rng.randint(0, 10**9 - 1); ms.append([s, min(10**9, s + rng.randint(0, 10**7))])
    return (ms, max(1, n // 300))


def p02(rng, n):
    s = []; ln = 0
    while ln < n:
        r = rng.choice("ab1\\") * rng.randint(1, 30); s.append(r); ln += len(r)
    return ("".join(s)[:n],)


def p03(rng, n):
    return (_load("p03_ledger")._gen(rng, n, [f"u{i}" for i in range(max(40, n // 10))]),)


def p04(rng, n):
    return ([rng.randint(-10**9, 10**9) for _ in range(n)], n // 2)


def p05(rng, n):
    edges = [[i, i + 1, rng.randint(0, 10**6), rng.choice([-1, 0, 1, 2, 3])] for i in range(n - 1)]
    while len(edges) < 5 * n:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v: edges.append([u, v, rng.randint(0, 10**6), rng.choice([-1, 0, 1, 2, 3])])
    return (n, edges, [[rng.randrange(n), rng.randrange(4)] for _ in range(50)], [rng.randint(0, 10**6) for _ in range(4)])


def p06(rng, n):
    m = _load("p06_calc"); e = "0"
    while True:
        part = m._expr(rng, 4, big=True)
        if m.ref(part) == "error": continue
        nxt = e + " - (" + part + ")"
        if len(nxt) > n: break
        e = nxt
    return (e,)


def p07(rng, n):
    return (n, _load("p07_weighted_distance_sums")._tree(rng, n), [rng.randint(0, 10**9) for _ in range(n)])


def p08(rng, n):
    return ("1900-01-01", f"WEEKLY {n} MO,TH", 50)


def p09(rng, n):
    jobs = []
    for _ in range(n):
        s = rng.randint(0, 10**9 - 1); jobs.append([s, min(10**9, s + rng.randint(1, 3 * 10**8)), rng.randint(1, 10**6)])
    return (jobs, 4)


def p10(rng, n):
    return (10**18 - 1, "ACGT", ["".join(rng.choice("ACGT") for _ in range(n))])


def p11(rng, n):
    return ([rng.randint(0, 10**9) for _ in range(n)], max(1, n // 20))


def p12(rng, n):
    m = _load("p12_sheet"); rows = n // 26; assert rows * 26 == n
    grid = {}
    for r in range(1, rows + 1):
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if r == rows or c == "Z":
                grid[c + str(r)] = str(rng.randint(-50, 50)); continue
            c2 = chr(min(ord("Z"), ord(c) + rng.randint(1, 2))); r2 = min(rows, r + rng.randint(1, 2))
            grid[c + str(r)] = f"=MAX({c}{r + 1}:{c2}{r2}) - MIN({chr(ord(c) + 1)}{r}, {c2}{r2}) + {rng.randint(0, 3)}"
    return (dict(rng.sample(sorted(grid.items()), len(grid))),)


def p13(rng, n):
    return ("".join(rng.choice("01") for _ in range(n)), [rng.randint(-10**9, 10**9) for _ in range(6)], 2**59 - 1)


def p14(rng, n):
    m = _load("p14_bounce_board")
    while True:
        a = m._board(rng, n, min(6, n), max(1, n // 4), 0.3)
        if m.ref(*a) is not None: return a


def p15(rng, n):
    big = 10**9; h = n // 2
    return (big, [[1, 2 * i + 2, 2 * i + 2, big] for i in range(h)] + [[1, 1, big, 1 + i % 7] for i in range(n - h)])


SIZED = {"p01_overlap_minutes": p01, "p02_squash": p02, "p03_ledger": p03, "p04_taller_within": p04, "p05_pass_route": p05,
         "p06_calc": p06, "p07_weighted_distance_sums": p07, "p08_recur": p08, "p09_k_machine_schedule": p09, "p10_avoid_count": p10,
         "p11_best_average": p11, "p12_sheet": p12, "p13_xor_ring": p13, "p14_bounce_board": p14, "p15_paint_erase": p15}
assert set(SIZED) == set(problems.IDS) == set(N0) == set(MAX_N) == set(SIZE_PARAM)
for _p in N0: assert 8 * N0[_p] <= MAX_N[_p], _p


def sizes(pid):
    return [N0[pid] * f for f in (1, 2, 4, 8)]


def sized(pid, rng, n):
    assert n <= MAX_N[pid], (pid, n)
    return SIZED[pid](rng, n)


def rng_for(pid, n):
    return random.Random(f"{pid}-quality-{n}")
