def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    chars = list(dict.fromkeys(alphabet))

    # Build trie
    nxt = [{}]
    bad = [False]
    for w in banned:
        cur = 0
        for ch in w:
            if ch not in nxt[cur]:
                nxt.append({})
                bad.append(False)
                nxt[cur][ch] = len(nxt) - 1
            cur = nxt[cur][ch]
        bad[cur] = True

    m = len(nxt)
    fail = [0] * m
    go = [dict() for _ in range(m)]
    from collections import deque
    q = deque()
    for ch in chars:
        if ch in nxt[0]:
            v = nxt[0][ch]
            fail[v] = 0
            go[0][ch] = v
            q.append(v)
        else:
            go[0][ch] = 0
    while q:
        u = q.popleft()
        if bad[fail[u]]:
            bad[u] = True
        for ch in chars:
            if ch in nxt[u]:
                v = nxt[u][ch]
                fail[v] = go[fail[u]][ch]
                go[u][ch] = v
                q.append(v)
            else:
                go[u][ch] = go[fail[u]][ch]

    good = [i for i in range(m) if not bad[i]]
    if not good or bad[0]:
        return 1 if n == 0 and not bad[0] else 0
    idx = {s: i for i, s in enumerate(good)}
    k = len(good)
    M = [[0] * k for _ in range(k)]
    for s in good:
        for ch in chars:
            t = go[s][ch]
            if not bad[t]:
                M[idx[s]][idx[t]] += 1

    def mul(A, B):
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

    R = [[1 if i == j else 0 for j in range(k)] for i in range(k)]
    e = n
    while e:
        if e & 1:
            R = mul(R, M)
        M = mul(M, M)
        e >>= 1
    return sum(R[idx[0]]) % MOD
