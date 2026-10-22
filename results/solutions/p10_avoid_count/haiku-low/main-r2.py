from collections import deque


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build the trie of banned strings.
    goto = [dict()]
    bad = [False]
    for w in banned:
        node = 0
        for ch in w:
            if ch not in goto[node]:
                goto[node][ch] = len(goto)
                goto.append({})
                bad.append(False)
            node = goto[node][ch]
        bad[node] = True

    m = len(goto)
    k = len(alphabet)

    # Aho-Corasick: failure links and a full DFA transition table.
    fail = [0] * m
    trans = [[0] * k for _ in range(m)]
    q = deque()
    for i, c in enumerate(alphabet):
        if c in goto[0]:
            v = goto[0][c]
            trans[0][i] = v
            fail[v] = 0
            q.append(v)
        else:
            trans[0][i] = 0

    while q:
        u = q.popleft()
        # Fail target is shallower, so its bad flag is already final.
        bad[u] = bad[u] or bad[fail[u]]
        for i, c in enumerate(alphabet):
            if c in goto[u]:
                v = goto[u][c]
                fail[v] = trans[fail[u]][i]
                trans[u][i] = v
                q.append(v)
            else:
                trans[u][i] = trans[fail[u]][i]

    # Keep only states that do not contain a banned substring.
    live = [s for s in range(m) if not bad[s]]
    index = {s: j for j, s in enumerate(live)}
    size = len(live)

    M = [[0] * size for _ in range(size)]
    for s in live:
        for i in range(k):
            t = trans[s][i]
            if not bad[t]:
                M[index[s]][index[t]] += 1

    def mat_mul(A, B):
        C = [[0] * size for _ in range(size)]
        for i in range(size):
            Ai = A[i]
            Ci = C[i]
            for kk in range(size):
                a = Ai[kk]
                if a == 0:
                    continue
                Bk = B[kk]
                for j in range(size):
                    Ci[j] += a * Bk[j]
            for j in range(size):
                Ci[j] %= MOD
        return C

    # Compute M^n by binary exponentiation.
    result = [[int(i == j) for j in range(size)] for i in range(size)]
    base = M
    e = n
    while e > 0:
        if e & 1:
            result = mat_mul(result, base)
        base = mat_mul(base, base)
        e >>= 1

    # Start at the root (always live, since banned strings are non-empty).
    start = index[0]
    return sum(result[start]) % MOD
