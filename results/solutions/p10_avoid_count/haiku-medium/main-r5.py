from collections import deque


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build the Aho-Corasick trie over the banned strings.
    goto = [{}]
    bad = [False]
    for w in banned:
        cur = 0
        for ch in w:
            if ch not in goto[cur]:
                goto.append({})
                bad.append(False)
                goto[cur][ch] = len(goto) - 1
            cur = goto[cur][ch]
        bad[cur] = True

    m = len(goto)
    fail = [0] * m
    trans = [{} for _ in range(m)]
    q = deque()

    # Depth-1 nodes and root transitions.
    for ch in alphabet:
        if ch in goto[0]:
            c = goto[0][ch]
            fail[c] = 0
            trans[0][ch] = c
            q.append(c)
        else:
            trans[0][ch] = 0

    # BFS to build failure links and the full transition function.
    while q:
        u = q.popleft()
        # fail[u] is shallower, so its bad flag is already final.
        bad[u] = bad[u] or bad[fail[u]]
        for ch in alphabet:
            if ch in goto[u]:
                v = goto[u][ch]
                fail[v] = trans[fail[u]][ch]
                trans[u][ch] = v
                q.append(v)
            else:
                trans[u][ch] = trans[fail[u]][ch]

    # Transition matrix over automaton states, never entering a bad state.
    M = [[0] * m for _ in range(m)]
    for i in range(m):
        if bad[i]:
            continue
        for ch in alphabet:
            j = trans[i][ch]
            if not bad[j]:
                M[i][j] += 1

    def mat_mul(A, B):
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

    def vec_mat_mul(v, A):
        size = len(v)
        res = [0] * size
        for i in range(size):
            vi = v[i]
            if vi:
                Ai = A[i]
                for j in range(size):
                    res[j] += vi * Ai[j]
        return [x % MOD for x in res]

    # Vector-matrix binary exponentiation: v = e_0 * M^n.
    v = [0] * m
    v[0] = 1
    e = n
    P = M
    while e:
        if e & 1:
            v = vec_mat_mul(v, P)
        e >>= 1
        if e:
            P = mat_mul(P, P)

    return sum(v) % MOD
