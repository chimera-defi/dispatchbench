def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    banned = list(set(banned))
    # Aho-Corasick
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
    for ch in alphabet:
        if ch in goto[0]:
            q.append(goto[0][ch])
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        bad[u] = bad[u] or bad[fail[u]]
        for ch in alphabet:
            if ch in goto[u]:
                v = goto[u][ch]
                f = fail[u]
                while f and ch not in goto[f]:
                    f = fail[f]
                fail[v] = goto[f][ch] if ch in goto[f] and goto[f][ch] != v else 0
                q.append(v)
    # full transition
    S = len(goto)
    def step(u, ch):
        while u and ch not in goto[u]:
            u = fail[u]
        return goto[u].get(ch, 0)
    states = [i for i in range(S) if not bad[i]]
    idx = {s: i for i, s in enumerate(states)}
    m = len(states)
    if 0 not in idx:
        return 0
    T = [[0] * m for _ in range(m)]
    for s in states:
        for ch in alphabet:
            t = step(s, ch)
            if t in idx:
                T[idx[s]][idx[t]] += 1

    def mul(A, B):
        C = [[0] * m for _ in range(m)]
        for i in range(m):
            Ai = A[i]
            Ci = C[i]
            for k in range(m):
                a = Ai[k]
                if a:
                    Bk = B[k]
                    for j in range(m):
                        Ci[j] = (Ci[j] + a * Bk[j]) % MOD
        return C

    # vector times matrix power
    vec = [0] * m
    vec[idx[0]] = 1
    e = n
    P = T
    while e:
        if e & 1:
            nv = [0] * m
            for i in range(m):
                if vec[i]:
                    Pi = P[i]
                    for j in range(m):
                        nv[j] = (nv[j] + vec[i] * Pi[j]) % MOD
            vec = nv
        e >>= 1
        if e:
            P = mul(P, P)
    return sum(vec) % MOD
