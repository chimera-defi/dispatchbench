RUNG = 6
FUNC = "best_average"
SIGNATURE = "def best_average(a: list[int], k: int) -> list[int]:"
STATEMENT = """\
Among all contiguous subarrays of `a` with at least `k` elements, find the largest average (sum divided by length).

Return it as an exact fraction `[p, q]` in lowest terms with `q >= 1`.

Examples:
- `best_average([1, 12, 0, 6, 50, 3], 5)` returns `[71, 5]`: the subarray `[12, 0, 6, 50, 3]`.
- `best_average([5, 5], 1)` returns `[5, 1]`.
- `best_average([0, 0, 0], 2)` returns `[0, 1]`.

Constraints: `1 <= k <= len(a) <= 10**5`, `0 <= a[i] <= 10**9`. Answers are compared exactly. Some tests contain subarrays whose averages differ from the best one by less than `10**-9`."""


def ref(a, k):
    # Dinkelbach iteration with exact integer arithmetic. For the current ratio p/q, find the subarray (length >= k)
    # maximising q*sum - p*len; if that is positive, its average is a strictly better ratio. Terminates at the optimum.
    from math import gcd
    n = len(a); pre = [0] * (n + 1)
    for i, x in enumerate(a):
        pre[i + 1] = pre[i] + x
    p, q = pre[k], k
    while True:
        best = 0; arg = None; lo_i = 0; lo_v = 0  # lo_v = min over i <= j-k of q*pre[i] - p*i
        for j in range(k, n + 1):
            i = j - k; v = q * pre[i] - p * i
            if i == 0 or v < lo_v:
                lo_v, lo_i = v, i
            cur = q * pre[j] - p * j - lo_v
            if cur > best:
                best, arg = cur, (lo_i, j)
        if arg is None:
            g = gcd(p, q)
            return [p // g, q // g]
        i, j = arg; p, q = pre[j] - pre[i], j - i


def brute(a, k):
    from fractions import Fraction
    best = None
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]
            if j - i + 1 >= k:
                f = Fraction(s, j - i + 1)
                if best is None or f > best: best = f
    return [best.numerator, best.denominator]


def small(rng):
    n = rng.randint(1, 12)
    pool = rng.choice([[0, 1, 2], list(range(10)), [10**9, 10**9 - 1, 10**9 - 2, 0]])
    a = [rng.choice(pool) if rng.random() < 0.8 else rng.randint(0, 10**9) for _ in range(n)]
    return (a, rng.randint(1, n))


def fixed():
    return [a for a, _ in EXAMPLES] + [([7], 1), ([3, 1, 4, 1, 5, 9, 2, 6], 8), ([0, 10**9], 1), ([2, 1, 2], 2), ([1, 2, 1, 2, 1], 3)]


def _near_tie(rng, k, a_first):
    # Block A (length k, sum j*k + 1) beats block B (length k+1, sum j*(k+1) + 1) by exactly 1/(k*(k+1)).
    # B's endpoints are j+1 and one interior element is j-1, so no length-k window inside B beats B as a whole.
    j = 10**9 - 1
    A = [j + 1] + [j] * (k - 1)
    B = [j + 1] + [j] * (k - 1) + [j + 1]; B[k // 2] = j - 1
    gap = [0] * 50
    blocks = A + gap + B if a_first else B + gap + A
    rest = 10**5 - len(blocks)
    left = rng.randint(0, rest - 100)
    noise = lambda m: [rng.randint(0, 4 * 10**8) for _ in range(m)]
    return (noise(left) + gap + blocks + gap + noise(rest - left - 100), k)


def big(rng):
    n = 10**5
    return [([rng.randint(0, 10**9) for _ in range(n)], 1000),
            ([rng.randint(10**9 - 3, 10**9) for _ in range(n)], 30000),
            _near_tie(rng, 30000, True), _near_tie(rng, 40000, False), _near_tie(rng, 7, True)]


EXAMPLES = [(([1, 12, 0, 6, 50, 3], 5), [71, 5]), (([5, 5], 1), [5, 1]), (([0, 0, 0], 2), [0, 1])]

WRONG = {
    "float_bisect_limit_denominator": """
from fractions import Fraction
def best_average(a, k):
    lo, hi = float(min(a)), float(max(a))
    def ok(m):
        pre = [0.0]
        for x in a: pre.append(pre[-1] + x - m)
        mn = float("inf")
        for j in range(k, len(a) + 1):
            mn = min(mn, pre[j - k])
            if pre[j] - mn >= 0: return True
        return False
    for _ in range(100):
        mid = (lo + hi) / 2
        if ok(mid): lo = mid
        else: hi = mid
    f = Fraction(lo).limit_denominator(len(a))
    return [f.numerator, f.denominator]
""",
    "float_bisect_segment": """
from math import gcd
def best_average(a, k):
    lo, hi = float(min(a)), float(max(a)); seg = (0, k)
    pre_i = [0]
    for x in a: pre_i.append(pre_i[-1] + x)
    def find(m):
        pre = [0.0]
        for x in a: pre.append(pre[-1] + x - m)
        mn, mi = float("inf"), 0
        for j in range(k, len(a) + 1):
            if pre[j - k] < mn: mn, mi = pre[j - k], j - k
            if pre[j] - mn >= 0: return (mi, j)
        return None
    for _ in range(100):
        mid = (lo + hi) / 2; s = find(mid)
        if s: lo, seg = mid, s
        else: hi = mid
    p, q = pre_i[seg[1]] - pre_i[seg[0]], seg[1] - seg[0]; g = gcd(p, q)
    return [p // g, q // g]
""",
    "length_exactly_k": """
from math import gcd
def best_average(a, k):
    s = sum(a[:k]); best = s
    for i in range(k, len(a)):
        s += a[i] - a[i - k]; best = max(best, s)
    g = gcd(best, k)
    return [best // g, k // g]
""",
    "quadratic_exact": """
from fractions import Fraction
def best_average(a, k):
    best = None
    pre = [0]
    for x in a: pre.append(pre[-1] + x)
    for i in range(len(a)):
        for j in range(i + k, len(a) + 1):
            f = Fraction(pre[j] - pre[i], j - i)
            if best is None or f > best: best = f
    return [best.numerator, best.denominator]
""",
}
