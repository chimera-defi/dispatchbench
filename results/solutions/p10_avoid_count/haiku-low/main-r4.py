from collections import deque

MOD = 1_000_000_007


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    index = {c: i for i, c in enumerate(alphabet)}
    k = len(alphabet)

    # Build the trie of banned strings.
    goto = [[-1] * k]
    bad = [False]
    for word in banned:
        node = 0
        for ch in word:
            j = index[ch]
            if goto[node][j] == -1:
                goto[node][j] = len(goto)
                goto.append([-1] * k)
                bad.append(False)
            node = goto[node][j]
        bad[node] = True

    # Build the Aho-Corasick automaton (BFS over failure links).
    fail = [0] * len(goto)
    queue = deque()
    for j in range(k):
        v = goto[0][j]
        if v == -1:
            goto[0][j] = 0
        else:
            fail[v] = 0
            queue.append(v)
    while queue:
        u = queue.popleft()
        bad[u] = bad[u] or bad[fail[u]]
        for j in range(k):
            v = goto[u][j]
            if v == -1:
                goto[u][j] = goto[fail[u]][j]
            else:
                fail[v] = goto[fail[u]][j]
                queue.append(v)

    # Transition matrix over safe states only.
    size = len(goto)
    M = [[0] * size for _ in range(size)]
    for u in range(size):
        if bad[u]:
            continue
        for j in range(k):
            v = goto[u][j]
            if not bad[v]:
                M[u][v] += 1

    def mul(A, B):
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

    # Compute M^n by fast exponentiation.
    result = [[int(i == j) for j in range(size)] for i in range(size)]
    base = M
    e = n
    while e:
        if e & 1:
            result = mul(result, base)
        base = mul(base, base)
        e >>= 1

    return sum(result[0]) % MOD
