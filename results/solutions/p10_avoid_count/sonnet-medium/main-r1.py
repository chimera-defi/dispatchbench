def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    words = list(set(banned))
    # Aho-Corasick automaton
    goto = [{}]
    fail = [0]
    bad = [False]
    for w in words:
        cur = 0
        for ch in w:
            if ch not in goto[cur]:
                goto[cur][ch] = len(goto)
                goto.append({})
                fail.append(0)
                bad.append(False)
            cur = goto[cur][ch]
        bad[cur] = True
    from collections import deque
    q = deque()
    for ch, v in goto[0].items():
        fail[v] = 0
        q.append(v)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        if bad[fail[u]]:
            bad[u] = True
        for ch, v in goto[u].items():
            f = fail[u]
            while f and ch not in goto[f]:
                f = fail[f]
            fail[v] = goto[f][ch] if ch in goto[f] and goto[f][ch] != v else 0
            q.append(v)
    S = len(goto)
    # full transitions
    def step(s, ch):
        while s and ch not in goto[s]:
            s = fail[s]
        return goto[s].get(ch, 0)
    states = [s for s in range(S) if not bad[s]]
    if bad[0]:
        return 0
    idx = {s: i for i, s in enumerate(states)}
    m = len(states)
    M = [[0] * m for _ in range(m)]
    for s in states:
        for ch in alphabet:
            t = step(s, ch)
            if not bad[t]:
                M[idx[s]][idx[t]] += 1

    def mul(A, B):
        n_ = len(A)
        C = [[0] * n_ for _ in range(n_)]
        for i in range(n_):
            Ai = A[i]
            Ci = C[i]
            for k in range(n_):
                a = Ai[k]
                if a:
                    Bk = B[k]
                    for j in range(n_):
                        Ci[j] += a * Bk[j]
            for j in range(n_):
                Ci[j] %= MOD
        return C

    # vector times matrix power
    vec = [0] * m
    vec[idx[0]] = 1
    e = n
    P = M
    while e:
        if e & 1:
            nv = [0] * m
            for i in range(m):
                if vec[i]:
                    vi = vec[i]
                    Pi = P[i]
                    for j in range(m):
                        nv[j] += vi * Pi[j]
            vec = [x % MOD for x in nv]
        e >>= 1
        if e:
            P = mul(P, P)
    return sum(vec) % MOD
