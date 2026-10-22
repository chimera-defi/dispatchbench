def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    chars = list(dict.fromkeys(alphabet))
    nxt = [{}]
    bad = [False]
    for w in set(banned):
        cur = 0
        for c in w:
            if c not in nxt[cur]:
                nxt[cur][c] = len(nxt)
                nxt.append({})
                bad.append(False)
            cur = nxt[cur][c]
        bad[cur] = True
    S = len(nxt)
    fail = [0] * S
    go = [dict() for _ in range(S)]
    from collections import deque
    q = deque()
    for c in chars:
        if c in nxt[0]:
            t = nxt[0][c]
            go[0][c] = t
            fail[t] = 0
            q.append(t)
        else:
            go[0][c] = 0
    while q:
        s = q.popleft()
        if bad[fail[s]]:
            bad[s] = True
        for c in chars:
            if c in nxt[s]:
                t = nxt[s][c]
                fail[t] = go[fail[s]][c]
                go[s][c] = t
                q.append(t)
            else:
                go[s][c] = go[fail[s]][c]
    if bad[0]:
        return 0
    M = [[0] * S for _ in range(S)]
    for s in range(S):
        if bad[s]:
            continue
        for c in chars:
            t = go[s][c]
            if not bad[t]:
                M[s][t] += 1

    def mul(A, B):
        R = [[0] * S for _ in range(S)]
        for i in range(S):
            Ai = A[i]
            Ri = R[i]
            for k in range(S):
                a = Ai[k]
                if a:
                    Bk = B[k]
                    for j in range(S):
                        if Bk[j]:
                            Ri[j] = (Ri[j] + a * Bk[j]) % MOD
        return R

    v = [0] * S
    v[0] = 1
    e = n
    while e:
        if e & 1:
            nv = [0] * S
            for i in range(S):
                if v[i]:
                    Mi = M[i]
                    for j in range(S):
                        if Mi[j]:
                            nv[j] = (nv[j] + v[i] * Mi[j]) % MOD
            v = nv
        e >>= 1
        if e:
            M = mul(M, M)
    return sum(v) % MOD
