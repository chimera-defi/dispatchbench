from collections import deque


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie of the banned strings.
    goto = [dict()]
    bad = [False]
    for s in banned:
        cur = 0
        for ch in s:
            if ch not in goto[cur]:
                goto[cur][ch] = len(goto)
                goto.append(dict())
                bad.append(False)
            cur = goto[cur][ch]
        bad[cur] = True

    # Aho-Corasick failure links, computed by BFS.
    fail = [0] * len(goto)
    q = deque()
    for ch in alphabet:
        if ch in goto[0]:
            q.append(goto[0][ch])
    while q:
        u = q.popleft()
        bad[u] = bad[u] or bad[fail[u]]
        for ch, v in goto[u].items():
            f = fail[u]
            while f and ch not in goto[f]:
                f = fail[f]
            fail[v] = goto[f].get(ch, 0)
            q.append(v)

    def step(s, ch):
        while s and ch not in goto[s]:
            s = fail[s]
        return goto[s].get(ch, 0)

    # Live states: automaton states that do not contain a banned substring.
    live = [s for s in range(len(goto)) if not bad[s]]
    idx = {s: i for i, s in enumerate(live)}
    k = len(live)

    M = [[0] * k for _ in range(k)]
    for s in live:
        for ch in alphabet:
            t = step(s, ch)
            if not bad[t]:
                M[idx[s]][idx[t]] += 1

    def mat_mul(A, B):
        C = [[0] * k for _ in range(k)]
        for i in range(k):
            Ai = A[i]
            Ci = C[i]
            for m in range(k):
                a = Ai[m]
                if a:
                    Bm = B[m]
                    for j in range(k):
                        Ci[j] += a * Bm[j]
            for j in range(k):
                Ci[j] %= MOD
        return C

    # Compute M^n by binary exponentiation (identity when n = 0).
    P = [[int(i == j) for j in range(k)] for i in range(k)]
    base = M
    e = n
    while e:
        if e & 1:
            P = mat_mul(P, base)
        base = mat_mul(base, base)
        e >>= 1

    # Sum over all end states reachable from the root in n steps.
    return sum(P[idx[0]]) % MOD
