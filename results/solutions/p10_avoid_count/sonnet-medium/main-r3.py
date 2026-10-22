def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    banned = list(set(banned))
    alpha = list(dict.fromkeys(alphabet))

    # Build Aho-Corasick automaton
    goto = [{}]
    fail = [0]
    bad = [False]
    for w in banned:
        cur = 0
        for ch in w:
            if ch not in goto[cur]:
                goto.append({})
                fail.append(0)
                bad.append(False)
                goto[cur][ch] = len(goto) - 1
            cur = goto[cur][ch]
        bad[cur] = True

    from collections import deque
    q = deque()
    for ch in alpha:
        if ch in goto[0]:
            q.append(goto[0][ch])
    while q:
        u = q.popleft()
        bad[u] = bad[u] or bad[fail[u]]
        for ch in alpha:
            if ch in goto[u]:
                v = goto[u][ch]
                f = fail[u]
                while f and ch not in goto[f]:
                    f = fail[f]
                fv = goto[f][ch] if ch in goto[f] and goto[f][ch] != v else 0
                fail[v] = fv
                q.append(v)

    S = len(goto)
    # full transition table
    def step(s, ch):
        while s and ch not in goto[s]:
            s = fail[s]
        return goto[s][ch] if ch in goto[s] else 0

    good = [i for i in range(S) if not bad[i]]
    if bad[0]:
        return 1 if n == 0 else 0
    idx = {s: i for i, s in enumerate(good)}
    m = len(good)
    M = [[0] * m for _ in range(m)]
    for s in good:
        for ch in alpha:
            t = step(s, ch)
            if not bad[t]:
                M[idx[s]][idx[t]] += 1

    def mul(A, B):
        size = len(A)
        C = [[0] * size for _ in range(size)]
        for i in range(size):
            Ai = A[i]
            Ci = C[i]
            for k in range(size):
                a = Ai[k]
                if a:
                    Bk = B[k]
                    for j in range(size):
                        Ci[j] += a * Bk[j]
            for j in range(size):
                Ci[j] %= MOD
        return C

    # vector times matrix power
    vec = [0] * m
    vec[idx[0]] = 1
    e = n
    P = M
    while e:
        if e & 1:
            vec = [sum(vec[i] * P[i][j] for i in range(m)) % MOD for j in range(m)]
        e >>= 1
        if e:
            P = mul(P, P)
    return sum(vec) % MOD
