RUNG = 2
FUNC = "taller_within"
SIGNATURE = "def taller_within(a: list[int], k: int) -> list[int]:"
STATEMENT = """\
People stand in a queue with heights `a[0], a[1], ...`. For each position `i`, count how many of the (at most) `k` people directly in front of it are strictly taller. Those are the indices `j` with `i - k <= j < i` and `a[j] > a[i]`.

Return the list of counts, one per position.

Examples:
- `taller_within([5, 1, 4, 4, 9], 2)` returns `[0, 1, 1, 0, 0]`.
- `taller_within([3, 2, 1], 3)` returns `[0, 1, 2]`.
- `taller_within([7, 7], 0)` returns `[0, 0]`.

Constraints: `1 <= len(a) <= 200000`, `0 <= k <= len(a)`, `-10**9 <= a[i] <= 10**9`."""


def ref(a, k):
    vals = sorted(set(a)); idx = {v: i + 1 for i, v in enumerate(vals)}; m = len(vals)
    tree = [0] * (m + 1)
    def add(i, d):
        while i <= m: tree[i] += d; i += i & -i
    def pref(i):
        s = 0
        while i > 0: s += tree[i]; i -= i & -i
        return s
    out = []; inside = 0
    for i, x in enumerate(a):
        if k > 0 and i - k - 1 >= 0:
            add(idx[a[i - k - 1]], -1); inside -= 1
        out.append(inside - pref(idx[x]))
        if k > 0:
            add(idx[x], 1); inside += 1
    return out


def brute(a, k):
    return [sum(1 for j in range(max(0, i - k), i) if a[j] > a[i]) for i in range(len(a))]


def small(rng):
    n = rng.randint(1, 12)
    return ([rng.randint(-4, 4) for _ in range(n)], rng.randint(0, n))


def fixed():
    return [([5, 1, 4, 4, 9], 2), ([3, 2, 1], 3), ([7, 7], 0), ([1], 0), ([1], 1), ([2, 1], 1)]


def big(rng):
    n = 200000
    return [([rng.randint(-10**9, 10**9) for _ in range(n)], 100000),
            ([n - i for i in range(n)], n),
            ([rng.randint(0, 50) for _ in range(n)], 777)]


WRONG = {
    "greater_or_equal": """
def taller_within(a, k):
    return [sum(1 for j in range(max(0, i - k), i) if a[j] >= a[i]) for i in range(len(a))]
""",
    "window_off_by_one": """
def taller_within(a, k):
    return [sum(1 for j in range(max(0, i - k + 1), i) if a[j] > a[i]) for i in range(len(a))]
""",
    "quadratic": """
def taller_within(a, k):
    out = []
    for i in range(len(a)):
        c = 0
        for j in range(max(0, i - k), i):
            if a[j] > a[i]: c += 1
        out.append(c)
    return out
""",
}

EXAMPLES = [(([5, 1, 4, 4, 9], 2), [0, 1, 1, 0, 0]), (([3, 2, 1], 3), [0, 1, 2]), (([7, 7], 0), [0, 0])]
