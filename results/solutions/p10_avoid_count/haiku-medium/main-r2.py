from collections import deque

MOD = 1_000_000_007


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    idx = {ch: i for i, ch in enumerate(alphabet)}
    k = len(alphabet)

    # Build the trie of banned strings.
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

    # Aho-Corasick failure links and full transition table.
    fail = [0] * len(goto)
    queue = deque()
    for c in range(k):
        child = goto[0][c]
        if child == -1:
            goto[0][c] = 0
        else:
            fail[child] = 0
            queue.append(child)
    while queue:
        u = queue.popleft()
        bad[u] = bad[u] or bad[fail[u]]
        for c in range(k):
            v = goto[u][c]
            if v == -1:
                goto[u][c] = goto[fail[u]][c]
            else:
                fail[v] = goto[fail[u]][c]
                queue.append(v)

    # Transition matrix over the non-banned automaton states.
    states = [s for s in range(len(goto)) if not bad[s]]
    pos = {s: i for i, s in enumerate(states)}
    m = len(states)
    M = [[0] * m for _ in range(m)]
    for s in states:
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
            for l in range(size):
                a = Ai[l]
                if a:
                    Bl = B[l]
                    for j in range(size):
                        Ci[j] += a * Bl[j]
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

    # Row vector starts at the root state; count all paths of length n.
    v = [0] * m
    v[pos[0]] = 1
    e = n
    while e:
        if e & 1:
            v = vec_mul(v, M)
        e >>= 1
        if e:
            M = mat_mul(M, M)
    return sum(v) % MOD
