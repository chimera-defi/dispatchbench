RUNG = 7
FUNC = "paint"
SIGNATURE = "def paint(n: int, ops: list[list[int]]) -> list[list[int]]:"
STATEMENT = """\
A strip has cells `1` to `n`, all blank at the start. Apply the operations in `ops` in order:

- `[1, l, r, c]` paints cells `l` to `r` inclusive with colour `c`. A cell that already holds a colour greater than `c` keeps it; any other cell, blank or not, takes colour `c`.
- `[0, l, r]` erases cells `l` to `r` inclusive: they become blank, whatever colour they held.

Return, for every colour held by at least one cell at the end, the pair `[colour, number of cells]`, sorted by colour. Blank cells are not reported.

Examples:
- `paint(10, [[1, 1, 5, 3], [1, 4, 8, 2]])` returns `[[2, 3], [3, 5]]`: cells 4 and 5 keep colour 3.
- `paint(10, [[1, 1, 10, 7], [0, 3, 4], [1, 1, 6, 5]])` returns `[[5, 2], [7, 8]]`: only the erased cells 3 and 4 take colour 5.
- `paint(5, [[0, 1, 5]])` returns `[]`.

Constraints: `1 <= n <= 10**9`, `1 <= len(ops) <= 10**5`, `1 <= l <= r <= n`, `1 <= c <= 10**9`."""


def ref(n, ops):
    # A cell's final colour is the largest colour painted on it after the last erase that covers it.
    # 1) Compress coordinates into elementary segments. 2) Last covering erase per segment: erases in reverse
    #    order with a "next unassigned segment" union-find. 3) Sweep segments by that erase time, newest first,
    #    adding paints newer than it into a max-tag segment tree (range chmax, point query, no push-down).
    import bisect
    pts = {1, n + 1}
    for op in ops:
        pts.add(op[1]); pts.add(op[2] + 1)
    xs = sorted(pts); k = len(xs) - 1
    seg = lambda l, r: (bisect.bisect_left(xs, l), bisect.bisect_left(xs, r + 1))  # [lo, hi) segment indices
    last_erase = [-1] * k; nxt = list(range(k + 1))

    def find(i):
        root = i
        while nxt[root] != root: root = nxt[root]
        while nxt[i] != root: nxt[i], i = root, nxt[i]
        return root
    for t in range(len(ops) - 1, -1, -1):
        if ops[t][0] == 0:
            lo, hi = seg(ops[t][1], ops[t][2]); i = find(lo)
            while i < hi:
                last_erase[i] = t; nxt[i] = i + 1; i = find(i + 1)
    size = 1
    while size < k: size *= 2
    tag = [0] * (2 * size)
    paints = [(t, op) for t, op in enumerate(ops) if op[0] == 1]
    order = sorted(range(k), key=lambda i: -last_erase[i])
    pi = len(paints) - 1; colour = [0] * k
    for i in order:
        while pi >= 0 and paints[pi][0] > last_erase[i]:
            _, (_, l, r, c) = paints[pi]; lo, hi = seg(l, r); lo += size; hi += size
            while lo < hi:
                if lo & 1:
                    if tag[lo] < c: tag[lo] = c
                    lo += 1
                if hi & 1:
                    hi -= 1
                    if tag[hi] < c: tag[hi] = c
                lo >>= 1; hi >>= 1
            pi -= 1
        j = i + size; best = 0
        while j:
            if tag[j] > best: best = tag[j]
            j >>= 1
        colour[i] = best
    tot = {}
    for i in range(k):
        if colour[i]: tot[colour[i]] = tot.get(colour[i], 0) + xs[i + 1] - xs[i]
    return [[c, tot[c]] for c in sorted(tot)]


def brute(n, ops):
    cells = [0] * (n + 1)
    for op in ops:
        if op[0] == 0:
            for x in range(op[1], op[2] + 1): cells[x] = 0
        else:
            for x in range(op[1], op[2] + 1): cells[x] = max(cells[x], op[3])
    tot = {}
    for x in range(1, n + 1):
        if cells[x]: tot[cells[x]] = tot.get(cells[x], 0) + 1
    return [[c, tot[c]] for c in sorted(tot)]


def small(rng):
    n = rng.randint(1, 30); ops = []
    for _ in range(rng.randint(1, 12)):
        l = rng.randint(1, n); r = rng.randint(l, min(n, l + rng.choice([0, 2, 8, 30])))
        ops.append([0, l, r] if rng.random() < 0.3 else [1, l, r, rng.choice([rng.randint(1, 4), rng.randint(1, 10**9)])])
    return (n, ops)


def fixed():
    return [a for a, _ in EXAMPLES] + [(1, [[1, 1, 1, 5], [1, 1, 1, 5]]), (3, [[1, 1, 3, 2], [0, 2, 2], [1, 2, 2, 1]]),
                                       (10**9, [[1, 1, 10**9, 10**9], [0, 10**9, 10**9]]), (6, [[0, 1, 6], [1, 6, 6, 1], [1, 1, 1, 1]])]


def big(rng):
    n = 10**9; m = 10**5
    rand = [[0, *sorted((rng.randint(1, n), rng.randint(1, n)))] if rng.random() < 0.2 else [1, *sorted((rng.randint(1, n), rng.randint(1, n))), rng.randint(1, 10**9)]
            for _ in range(m)]
    # Many single cells with a high colour, then many wide low paints: an interval map that walks every piece is quadratic.
    comb = [[1, 2 * i + 2, 2 * i + 2, 10**9] for i in range(m // 2)] + [[1, 1, n, 1 + i % 7] for i in range(m // 2)]
    layered = []
    for i in range(m):
        l = rng.randint(1, n - 10**6)
        layered.append([0, l, l + rng.randint(0, 10**6)] if i % 3 == 2 else [1, l, l + rng.randint(0, 10**6), rng.randint(1, 50)])
    return [(n, rand), (n, comb), (n, layered), (10**5, [[1, i + 1, 10**5, i + 1] for i in range(m)])]


EXAMPLES = [((10, [[1, 1, 5, 3], [1, 4, 8, 2]]), [[2, 3], [3, 5]]), ((10, [[1, 1, 10, 7], [0, 3, 4], [1, 1, 6, 5]]), [[5, 2], [7, 8]]),
            ((5, [[0, 1, 5]]), [])]

WRONG = {
    "last_paint_wins": """
def paint(n, ops):
    marks = sorted({1, n + 1} | {op[1] for op in ops} | {op[2] + 1 for op in ops})
    import bisect
    col = [0] * (len(marks) - 1)
    for op in ops:
        lo, hi = bisect.bisect_left(marks, op[1]), bisect.bisect_left(marks, op[2] + 1)
        for i in range(lo, hi): col[i] = 0 if op[0] == 0 else op[3]
    tot = {}
    for i, c in enumerate(col):
        if c: tot[c] = tot.get(c, 0) + marks[i + 1] - marks[i]
    return [[c, tot[c]] for c in sorted(tot)]
""",
    "erase_ignored_max_only": """
def paint(n, ops):
    ev = []
    for op in ops:
        if op[0] == 1: ev.append((op[1], 1, op[3])); ev.append((op[2] + 1, -1, op[3]))
    ev.sort()
    import heapq
    from collections import Counter
    live = Counter(); heap = []; tot = {}; prev = None
    for x, kind, c in ev:
        while heap and live[-heap[0]] == 0: heapq.heappop(heap)
        if prev is not None and heap and x > prev:
            top = -heap[0]; tot[top] = tot.get(top, 0) + x - prev
        prev = x
        if kind == 1: live[c] += 1; heapq.heappush(heap, -c)
        else: live[c] -= 1
    return [[c, tot[c]] for c in sorted(tot)]
""",
    "interval_map_walks_pieces": """
import bisect
def paint(n, ops):
    keys = [1, n + 1]; vals = [0, 0]
    def split(x):
        i = bisect.bisect_right(keys, x) - 1
        if keys[i] != x: keys.insert(i + 1, x); vals.insert(i + 1, vals[i]); return i + 1
        return i
    for op in ops:
        a = split(op[1]); b = split(op[2] + 1)
        if op[0] == 0:
            del keys[a + 1:b]; del vals[a + 1:b]; vals[a] = 0
        else:
            c = op[3]
            for i in range(a, b):
                if vals[i] < c: vals[i] = c
    tot = {}
    for i in range(len(keys) - 1):
        if vals[i]: tot[vals[i]] = tot.get(vals[i], 0) + keys[i + 1] - keys[i]
    return [[c, tot[c]] for c in sorted(tot)]
""",
    "exclusive_right_end": """
def paint(n, ops):
    import bisect
    marks = sorted({1, n + 1} | {op[1] for op in ops} | {op[2] for op in ops})
    col = [0] * (len(marks) - 1)
    for op in ops:
        lo, hi = bisect.bisect_left(marks, op[1]), bisect.bisect_left(marks, op[2])
        for i in range(lo, hi): col[i] = 0 if op[0] == 0 else max(col[i], op[3])
    tot = {}
    for i, c in enumerate(col):
        if c: tot[c] = tot.get(c, 0) + marks[i + 1] - marks[i]
    return [[c, tot[c]] for c in sorted(tot)]
""",
}
