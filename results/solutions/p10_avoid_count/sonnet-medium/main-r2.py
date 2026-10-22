def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    chars = list(dict.fromkeys(alphabet))

    goto = [{}]
    bad = [False]
    for w in banned:
        cur = 0
        for c in w:
            if c not in goto[cur]:
                goto[cur][c] = len(goto)
                goto.append({})
                bad.append(False)
            cur = goto[cur][c]
        bad[cur] = True

    S = len(goto)
    fail = [0] * S
    trans = [dict() for _ in range(S)]
    order = []
    queue = []
    for c in chars:
        if c in goto[0]:
            nx = goto[0][c]
            fail[nx] = 0
            trans[0][c] = nx
            queue.append(nx)
        else:
            trans[0][c] = 0
    qi = 0
    while qi < len(queue):
        u = queue[qi]
        qi += 1
        order.append(u)
        if bad[fail[u]]:
            bad[u] = True
        for c in chars:
            if c in goto[u]:
                nx = goto[u][c]
                fail[nx] = trans[fail[u]][c]
                trans[u][c] = nx
                queue.append(nx)
            else:
                trans[u][c] = trans[fail[u]][c]

    # bad propagation must follow BFS order (fail target is shallower, already finalized)
    if bad[0]:
        return 0

    M = [[0] * S for _ in range(S)]
    for u in range(S):
        if bad[u]:
            continue
        for c in chars:
            v = trans[u][c]
            if not bad[v]:
                M[u][v] += 1

    def mat_mul(A, B):
        R = [[0] * S for _ in range(S)]
        for i in range(S):
            Ai = A[i]
            Ri = R[i]
            for k in range(S):
                a = Ai[k]
                if a:
                    Bk = B[k]
                    for j in range(S):
                        Ri[j] += a * Bk[j]
            for j in range(S):
                Ri[j] %= MOD
        return R

    def vec_mul(v, A):
        r = [0] * S
        for k in range(S):
            x = v[k]
            if x:
                Ak = A[k]
                for j in range(S):
                    r[j] += x * Ak[j]
        return [x % MOD for x in r]

    vec = [0] * S
    vec[0] = 1
    while n:
        if n & 1:
            vec = vec_mul(vec, M)
        n >>= 1
        if n:
            M = mat_mul(M, M)
    return sum(vec) % MOD
