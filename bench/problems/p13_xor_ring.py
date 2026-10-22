RUNG = 7
FUNC = "evolve"
SIGNATURE = "def evolve(state: str, offsets: list[int], t: int) -> str:"
STATEMENT = """\
`n` lamps stand in a ring, numbered `0` to `n - 1`. `state[i]` is `'1'` if lamp `i` is on and `'0'` if it is off.

Every second all lamps change at once. The new value of lamp `i` is the XOR of the old values of lamps `(i + d) mod n`, one term for each `d` in `offsets`, in the order given. An offset that appears twice contributes two terms, and those two terms cancel. Offsets may be negative, zero, or larger than `n`.

Return the state after `t` seconds, as a string in the same format.

Examples:
- `evolve("0100", [1], 1)` returns `"1000"`: each lamp copies its right-hand neighbour.
- `evolve("0100", [-1, 1], 1)` returns `"1010"`.
- `evolve("110", [5], 2)` returns `"101"`.
- `evolve("1", [0, 0], 5)` returns `"0"`.
- `evolve("1011", [2, 7], 0)` returns `"1011"`.

Constraints: `1 <= n <= 5000`, `1 <= len(offsets) <= 6`, `-10**9 <= offsets[j] <= 10**9`, `0 <= t <= 10**18`."""


def ref(state, offsets, t):
    # The update is multiplication by P(x) = sum x^(-d) over GF(2)[x]/(x^n - 1). In characteristic 2,
    # P(x)^(2^k) = P(x^(2^k)), so P^t applies one Frobenius-scaled operator per set bit of t.
    n = len(state); mask = (1 << n) - 1
    x = sum(1 << i for i, ch in enumerate(state) if ch == "1")

    def step(x, ds):
        y = 0
        for d in ds:
            s = d % n
            y ^= ((x >> s) | (x << (n - s))) & mask  # new bit i = old bit (i + s) mod n
        return y
    k = 0
    while t >> k:
        if (t >> k) & 1:
            x = step(x, [d * pow(2, k, n) for d in offsets])
        k += 1
    return "".join("1" if (x >> i) & 1 else "0" for i in range(n))


def brute(state, offsets, t):
    # Direct simulation with cycle detection on the full state.
    n = len(state); cur = tuple(int(c) for c in state); seen = {cur: 0}; hist = [cur]; i = 0
    while i < t:
        nxt = tuple(sum(cur[(j + d) % n] for d in offsets) % 2 for j in range(n)); i += 1
        if nxt in seen:
            start = seen[nxt]; period = i - start
            cur = hist[start + (t - start) % period]
            return "".join(map(str, cur))
        seen[nxt] = i; hist.append(nxt); cur = nxt
    return "".join(map(str, cur))


def small(rng):
    n = rng.randint(1, 12)
    state = "".join(rng.choice("01") for _ in range(n))
    m = rng.randint(1, 4)
    offs = [rng.randint(-15, 15) for _ in range(m)]
    if rng.random() < 0.25: offs.append(rng.choice(offs))  # a repeated offset cancels
    if rng.random() < 0.15: offs.append(rng.choice(offs) + n * rng.randint(-3, 3))  # same residue, different value
    t = rng.choice([rng.randint(0, 40), rng.randint(0, 10**18), 2**rng.randint(0, 60), 2**rng.randint(1, 60) - 1])
    return (state, offs[:6], t)


def fixed():
    return [a for a, _ in EXAMPLES] + [("1", [3], 10**18), ("10", [1, -1], 7), ("1000000", [0], 10**18), ("0110100", [1, 2, 4], 123456789),
                                       ("101", [10**9, -10**9], 3), ("1100", [1, 1, 2], 2**59)]


def big(rng):
    def st(n): return "".join(rng.choice("01") for _ in range(n))
    return [(st(5000), [rng.randint(-10**9, 10**9) for _ in range(6)], rng.randint(10**17, 10**18)),
            (st(4999), [1, -1, 3], 10**18),
            (st(4096), [7, 7, 11, -5, 12345678, 0], 2**60 - 1),
            (st(4997), [rng.randint(-50, 50) for _ in range(5)], 999999999999999989),
            ("1" + "0" * 4999, [-2, 1, 1000], 10**18 - 1)]


EXAMPLES = [(("0100", [1], 1), "1000"), (("0100", [-1, 1], 1), "1010"), (("110", [5], 2), "101"), (("1", [0, 0], 5), "0"),
            (("1011", [2, 7], 0), "1011")]

WRONG = {
    "simulate_with_cycle_detection": """
def evolve(state, offsets, t):
    n = len(state); cur = tuple(int(c) for c in state); seen = {cur: 0}; hist = [cur]; i = 0
    while i < t:
        nxt = tuple(sum(cur[(j + d) % n] for d in offsets) % 2 for j in range(n)); i += 1
        if nxt in seen:
            s = seen[nxt]; cur = hist[s + (t - s) % (i - s)]
            return "".join(map(str, cur))
        seen[nxt] = i; hist.append(nxt); cur = nxt
    return "".join(map(str, cur))
""",
    "offsets_as_set": """
def evolve(state, offsets, t):
    n = len(state); mask = (1 << n) - 1
    x = sum(1 << i for i, ch in enumerate(state) if ch == "1")
    offs = sorted(set(offsets)); k = 0
    while t >> k:
        if (t >> k) & 1:
            y = 0
            for d in offs:
                s = (d * pow(2, k, n)) % n
                y ^= ((x >> s) | (x << (n - s))) & mask
            x = y
        k += 1
    return "".join("1" if (x >> i) & 1 else "0" for i in range(n))
""",
    "wrong_direction": """
def evolve(state, offsets, t):
    n = len(state); mask = (1 << n) - 1
    x = sum(1 << i for i, ch in enumerate(state) if ch == "1"); k = 0
    while t >> k:
        if (t >> k) & 1:
            y = 0
            for d in offsets:
                s = (d * pow(2, k, n)) % n
                y ^= ((x << s) | (x >> (n - s))) & mask
            x = y
        k += 1
    return "".join("1" if (x >> i) & 1 else "0" for i in range(n))
""",
    "assumes_period_2n": """
def evolve(state, offsets, t):
    n = len(state); cur = [int(c) for c in state]
    for _ in range(t % (2 * n) if t >= 2 * n else t):
        cur = [sum(cur[(j + d) % n] for d in offsets) % 2 for j in range(n)]
    return "".join(map(str, cur))
""",
}
