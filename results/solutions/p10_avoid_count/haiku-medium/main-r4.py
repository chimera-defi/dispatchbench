MOD = 1_000_000_007


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    idx = {ch: i for i, ch in enumerate(alphabet)}
    k = len(alphabet)

    # Build a trie of the banned strings.
    goto = [[-1] * k]
    bad = [False]
    for word in banned:
        node = 0
        for ch in word:
            c = idx[ch]
            if goto[node][c] == -1:
                goto[node][c] = len(goto)
                goto.append([-1] * k)
                bad.append(False)
            node = goto[node][c]
        bad[node] = True

    # Build the Aho-Corasick automaton (failure links + full transitions).
    fail = [0] * len(goto)
    queue = []
    for c in range(k):
        child = goto[0][c]
        if child == -1:
            goto[0][c] = 0
        else:
            fail[child] = 0
            queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        # A state is bad if any suffix of it is a banned string.
        bad[node] = bad[node] or bad[fail[node]]
        for c in range(k):
            child = goto[node][c]
            if child == -1:
                goto[node][c] = goto[fail[node]][c]
            else:
                fail[child] = goto[fail[node]][c]
                queue.append(child)

    # Transition matrix over the live (non-banned) states only.
    live = [s for s in range(len(goto)) if not bad[s]]
    pos = {s: i for i, s in enumerate(live)}
    m = len(live)
    M = [[0] * m for _ in range(m)]
    for s in live:
        for c in range(k):
            t = goto[s][c]
            if not bad[t]:
                M[pos[s]][pos[t]] += 1

    def mat_mul(A, B):
        size = len(A)
        C = [[0] * size for _ in range(size)]
        for i in range(size):
            Ai = A[i]
            Ci = C[i]
            for t in range(size):
                a = Ai[t]
                if a:
                    Bt = B[t]
                    for j in range(size):
                        Ci[j] += a * Bt[j]
            for j in range(size):
                Ci[j] %= MOD
        return C

    def vec_mul(v, A):
        size = len(v)
        out = [0] * size
        for i in range(size):
            vi = v[i]
            if vi:
                Ai = A[i]
                for j in range(size):
                    out[j] += vi * Ai[j]
        return [x % MOD for x in out]

    # Compute (start vector) * M^n by binary exponentiation.
    v = [0] * m
    v[pos[0]] = 1
    P = M
    e = n
    while e:
        if e & 1:
            v = vec_mul(v, P)
        e >>= 1
        if e:
            P = mat_mul(P, P)

    return sum(v) % MOD
