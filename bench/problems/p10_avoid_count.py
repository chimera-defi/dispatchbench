RUNG = 5
FUNC = "avoid_count"
SIGNATURE = "def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:"
STATEMENT = """\
Count the strings of length `n` over the characters in `alphabet` that contain none of the strings in `banned` as a contiguous substring. Return the count modulo `1_000_000_007`.

`alphabet` has 2 to 4 distinct characters. Every banned string is non-empty and uses only characters from `alphabet`. `banned` may contain duplicates, or strings that contain other banned strings. The empty string (`n = 0`) counts as 1.

Examples:
- `avoid_count(3, "ab", ["aa"])` returns `5`: aba, abb, bab, bba, bbb.
- `avoid_count(2, "abc", ["abc"])` returns `9`.
- `avoid_count(10**18, "ab", ["a"])` returns `1`.

Constraints: `0 <= n <= 10**18`. The total length of all banned strings is at most 20."""

MOD = 1_000_000_007


def ref(n, alphabet, banned):
    # Aho-Corasick automaton over banned strings, then matrix power on the safe states.
    goto = [{}]; fail = [0]; bad = [False]
    for w in banned:
        u = 0
        for c in w:
            if c not in goto[u]:
                goto[u][c] = len(goto); goto.append({}); fail.append(0); bad.append(False)
            u = goto[u][c]
        bad[u] = True
    from collections import deque
    q = deque()
    for c in alphabet:
        if c in goto[0]: q.append(goto[0][c])
        else: goto[0][c] = 0
    while q:
        u = q.popleft(); bad[u] = bad[u] or bad[fail[u]]
        for c in alphabet:
            if c in goto[u]:
                v = goto[u][c]; fail[v] = goto[fail[u]][c] if u else 0; q.append(v)
            else:
                goto[u][c] = goto[fail[u]][c]
    safe = [u for u in range(len(goto)) if not bad[u]]; pos = {u: i for i, u in enumerate(safe)}; m = len(safe)
    if not bad[0]:
        M = [[0] * m for _ in range(m)]
        for u in safe:
            for c in alphabet:
                v = goto[u][c]
                if not bad[v]: M[pos[u]][pos[v]] += 1
    else:
        return 1 if n == 0 else 0

    def mul(A, B):
        return [[sum(a * b for a, b in zip(row, col)) % MOD for col in zip(*B)] for row in A]
    vec = [[1 if i == pos[0] else 0 for i in range(m)]]; e = n; P = M
    while e:
        if e & 1: vec = mul(vec, P)
        e >>= 1
        if e: P = mul(P, P)
    return sum(vec[0]) % MOD


def brute(n, alphabet, banned):
    # Independent: DP over the last (L-1) characters, L = longest banned string; exact enumeration when n is tiny.
    import itertools
    if n <= 6:
        return sum(1 for t in itertools.product(alphabet, repeat=n) if not any(b in "".join(t) for b in banned)) % MOD
    L = max(len(b) for b in banned); bs = set(banned)
    ok = lambda s: not any(s[i:j] in bs for i in range(len(s)) for j in range(i + 1, len(s) + 1))
    cur = {}
    for t in itertools.product(alphabet, repeat=min(n, L - 1) if L > 1 else 0):
        s = "".join(t)
        if ok(s): cur[s] = cur.get(s, 0) + 1
    if L == 1:
        return pow(sum(1 for c in alphabet if c not in bs), n, MOD)
    for _ in range(n - (L - 1)):
        nxt = {}
        for s, v in cur.items():
            for c in alphabet:
                w = s + c
                if not any(w[i:] in bs for i in range(len(w))):
                    k = w[1:]; nxt[k] = (nxt.get(k, 0) + v) % MOD
        cur = nxt
    return sum(cur.values()) % MOD


def _banned(rng, alphabet, total):
    out = []; left = total
    while left > 0:
        L = rng.randint(1, min(left, 4)); out.append("".join(rng.choice(alphabet) for _ in range(L))); left -= L
    if rng.random() < 0.3 and out: out.append(out[0])
    return out


def small(rng):
    al = rng.choice(["ab", "abc", "ACGT", "xy"])
    bn = _banned(rng, al, rng.randint(2, 7))
    if all(len(b) == 1 for b in bn) and len(set(bn)) >= len(al): bn = bn[:1]
    return (rng.choice([0, 1, 2, 3, 5, 6, rng.randint(7, 40)]), al, bn)


def fixed():
    return [a for a, _ in EXAMPLES] + [(0, "ab", ["a"]), (0, "ab", ["a", "b"]), (5, "ab", ["a", "b"]), (4, "ab", ["aba", "b"]),
                                       (12, "abc", ["abc", "bc", "bca"]), (7, "ab", ["aaaaaaaaaaaaaaaaaaaa"])]


def big(rng):
    out = []
    for al in ("ab", "ACGT", "abc", "ab"):
        bn = []
        while sum(map(len, bn)) <= 15:
            bn.append("".join(rng.choice(al) for _ in range(rng.randint(3, 5))))
        out.append((rng.randint(10**17, 10**18), al, bn))
    out.append((10**18, "ab", ["aa"]))
    return out


EXAMPLES = [((3, "ab", ["aa"]), 5), ((2, "abc", ["abc"]), 9), ((10**18, "ab", ["a"]), 1)]

WRONG = {
    "no_suffix_propagation": """
def avoid_count(n, alphabet, banned):
    MOD = 10**9 + 7
    from collections import deque
    goto = [{}]; fail = [0]; bad = [False]
    for w in banned:
        u = 0
        for c in w:
            if c not in goto[u]: goto[u][c] = len(goto); goto.append({}); fail.append(0); bad.append(False)
            u = goto[u][c]
        bad[u] = True
    q = deque()
    for c in alphabet:
        if c in goto[0]: q.append(goto[0][c])
        else: goto[0][c] = 0
    while q:
        u = q.popleft()
        for c in alphabet:
            if c in goto[u]: v = goto[u][c]; fail[v] = goto[fail[u]][c] if u else 0; q.append(v)
            else: goto[u][c] = goto[fail[u]][c]
    safe = [u for u in range(len(goto)) if not bad[u]]; pos = {u: i for i, u in enumerate(safe)}; m = len(safe)
    M = [[0] * m for _ in range(m)]
    for u in safe:
        for c in alphabet:
            v = goto[u][c]
            if not bad[v]: M[pos[u]][pos[v]] += 1
    mul = lambda A, B: [[sum(a * b for a, b in zip(r, c)) % MOD for c in zip(*B)] for r in A]
    vec = [[1 if i == pos[0] else 0 for i in range(m)]]; P = M
    while n:
        if n & 1: vec = mul(vec, P)
        n >>= 1; P = mul(P, P)
    return sum(vec[0]) % MOD
""",
    "linear_dp": """
def avoid_count(n, alphabet, banned):
    MOD = 10**9 + 7
    L = max(len(b) for b in banned); bs = set(banned)
    cur = {"": 1}
    for _ in range(n):
        nxt = {}
        for s, v in cur.items():
            for c in alphabet:
                w = s + c
                if any(w[i:] in bs for i in range(len(w))): continue
                k = w[-(L - 1):] if L > 1 else ""
                nxt[k] = (nxt.get(k, 0) + v) % MOD
        cur = nxt
    return sum(cur.values()) % MOD
""",
}
