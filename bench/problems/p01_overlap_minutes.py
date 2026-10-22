RUNG = 1
FUNC = "overlap_minutes"
SIGNATURE = "def overlap_minutes(meetings: list[list[int]], k: int) -> int:"
STATEMENT = """\
A room log lists meetings as `[start, end]` pairs of minute timestamps. A meeting occupies the half-open interval `[start, end)`: it covers minute `start` up to, but not including, minute `end`. A meeting with `start == end` covers nothing.

Return the total number of minutes during which at least `k` meetings are in progress at the same time.

Examples:
- `overlap_minutes([[0, 10], [5, 15]], 2)` returns `5`. Minutes 5 to 9 are shared.
- `overlap_minutes([[0, 5], [5, 10]], 2)` returns `0`. The meetings only touch at minute 5.
- `overlap_minutes([[1, 4], [2, 3], [2, 6]], 1)` returns `5`.

Constraints: `0 <= len(meetings) <= 100000`, `0 <= start <= end <= 10**9`, `1 <= k <= 100000`."""


def ref(meetings, k):
    ev = []
    for s, e in meetings:
        if s < e:
            ev.append((s, 1)); ev.append((e, -1))
    ev.sort()
    total = cur = 0; prev = None
    for t, d in ev:
        if prev is not None and cur >= k:
            total += t - prev
        cur += d; prev = t
    return total


def brute(meetings, k):
    hi = max((e for _, e in meetings), default=0)
    return sum(1 for m in range(hi) if sum(s <= m < e for s, e in meetings) >= k)


def small(rng):
    n = rng.randint(0, 8)
    ms = []
    for _ in range(n):
        s = rng.randint(0, 30); ms.append([s, s + rng.choice([0, rng.randint(0, 12)])])
    return (ms, rng.randint(1, 4))


def fixed():
    return [([[0, 10], [5, 15]], 2), ([[0, 5], [5, 10]], 2), ([[1, 4], [2, 3], [2, 6]], 1), ([], 1),
            ([[3, 3], [3, 3]], 1), ([[0, 10]] * 3, 3), ([[0, 10]] * 3, 4), ([[0, 10**9]], 1)]


def big(rng):
    out = []
    for n, k in [(100000, 1), (100000, 50), (100000, 100000)]:
        ms = []
        for _ in range(n):
            s = rng.randint(0, 10**9 - 1); ms.append([s, min(10**9, s + rng.randint(0, 10**7))])
        out.append((ms, k))
    return out


WRONG = {
    "inclusive_end": """
def overlap_minutes(meetings, k):
    ev = []
    for s, e in meetings:
        if s < e: ev += [(s, 1), (e + 1, -1)]
    ev.sort(); total = cur = 0; prev = None
    for t, d in ev:
        if prev is not None and cur >= k: total += t - prev
        cur += d; prev = t
    return total
""",
    "strictly_more": """
def overlap_minutes(meetings, k):
    ev = []
    for s, e in meetings:
        if s < e: ev += [(s, 1), (e, -1)]
    ev.sort(); total = cur = 0; prev = None
    for t, d in ev:
        if prev is not None and cur > k: total += t - prev
        cur += d; prev = t
    return total
""",
    "per_minute": """
def overlap_minutes(meetings, k):
    from collections import Counter
    c = Counter()
    for s, e in meetings:
        for m in range(s, e): c[m] += 1
    return sum(1 for v in c.values() if v >= k)
""",
}

EXAMPLES = [(([[0, 10], [5, 15]], 2), 5), (([[0, 5], [5, 10]], 2), 0), (([[1, 4], [2, 3], [2, 6]], 1), 5)]
