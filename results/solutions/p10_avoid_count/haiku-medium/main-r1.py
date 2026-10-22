from collections import deque

MOD = 1_000_000_007


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    if n == 0:
        return 1

    # Build the trie of banned strings.
    children = [{}]
    bad = [False]
    for word in banned:
        node = 0
        for ch in word:
            if ch not in children[node]:
                children[node][ch] = len(children)
                children.append({})
                bad.append(False)
            node = children[node][ch]
        bad[node] = True

    # Aho-Corasick: failure links, full transition table, propagated bad flags.
    size = len(children)
    fail = [0] * size
    delta = [dict() for _ in range(size)]
    q = deque([0])
    while q:
        u = q.popleft()
        for ch in alphabet:
            if ch in children[u]:
                v = children[u][ch]
                fail[v] = 0 if u == 0 else delta[fail[u]][ch]
                bad[v] = bad[v] or bad[fail[v]]
                delta[u][ch] = v
                q.append(v)
            else:
                delta[u][ch] = 0 if u == 0 else delta[fail[u]][ch]

    # Transition matrix over safe states only (transitions into banned states dropped).
    M = [[0] * size for _ in range(size)]
    for u in range(size):
        if bad[u]:
            continue
        for ch in alphabet:
            v = delta[u][ch]
            if not bad[v]:
                M[u][v] += 1

    def mat_mul(A, B):
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

    def vec_mul(v, A):
        out = [0] * size
        for i in range(size):
            vi = v[i]
            if vi:
                Ai = A[i]
                for j in range(size):
                    out[j] += vi * Ai[j]
        return [x % MOD for x in out]

    # Compute start_vector * M^n via repeated squaring.
    vec = [0] * size
    vec[0] = 1
    base = M
    e = n
    while e:
        if e & 1:
            vec = vec_mul(vec, base)
        e >>= 1
        if e:
            base = mat_mul(base, base)

    return sum(vec) % MOD
