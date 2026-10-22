from collections import deque


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build the Aho-Corasick trie over the banned strings.
    goto = [{}]
    bad = [False]
    for word in banned:
        s = 0
        for ch in word:
            if ch not in goto[s]:
                goto.append({})
                bad.append(False)
                goto[s][ch] = len(goto) - 1
            s = goto[s][ch]
        bad[s] = True

    # Compute failure links with BFS and propagate "bad" along them.
    fail = [0] * len(goto)
    q = deque()
    for v in goto[0].values():
        q.append(v)
    while q:
        u = q.popleft()
        if bad[fail[u]]:
            bad[u] = True
        for ch, v in goto[u].items():
            f = fail[u]
            while f and ch not in goto[f]:
                f = fail[f]
            fail[v] = goto[f][ch] if ch in goto[f] else 0
            q.append(v)

    # Keep only states that do not contain a banned string; root is index 0.
    alive = [s for s in range(len(goto)) if not bad[s]]
    idx = {s: i for i, s in enumerate(alive)}
    k = len(alive)

    # Transition counts between safe states.
    M = [[0] * k for _ in range(k)]
    for s in alive:
        for ch in alphabet:
            f = s
            while f and ch not in goto[f]:
                f = fail[f]
            t = goto[f].get(ch, 0)
            if not bad[t]:
                M[idx[s]][idx[t]] += 1

    def mat_mul(A, B):
        C = [[0] * k for _ in range(k)]
        for i in range(k):
            Ai = A[i]
            Ci = C[i]
            for l in range(k):
                a = Ai[l]
                if a:
                    Bl = B[l]
                    for j in range(k):
                        Ci[j] += a * Bl[j]
            for j in range(k):
                Ci[j] %= MOD
        return C

    # Matrix exponentiation: R = M^n.
    R = [[int(i == j) for j in range(k)] for i in range(k)]
    base = M
    e = n
    while e:
        if e & 1:
            R = mat_mul(R, base)
        base = mat_mul(base, base)
        e >>= 1

    # Sum of walks of length n starting at the root.
    return sum(R[0]) % MOD
