from collections import deque


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build the trie of banned strings.
    goto = [{}]
    bad = [False]
    for word in banned:
        cur = 0
        for ch in word:
            if ch not in goto[cur]:
                goto[cur][ch] = len(goto)
                goto.append({})
                bad.append(False)
            cur = goto[cur][ch]
        bad[cur] = True

    # Aho-Corasick failure links, computed breadth-first.
    fail = [0] * len(goto)
    queue = deque()
    for nxt in goto[0].values():
        queue.append(nxt)
    while queue:
        u = queue.popleft()
        bad[u] = bad[u] or bad[fail[u]]
        for ch, v in goto[u].items():
            f = fail[u]
            while f and ch not in goto[f]:
                f = fail[f]
            fail[v] = goto[f].get(ch, 0)
            queue.append(v)

    def step(u, ch):
        while u and ch not in goto[u]:
            u = fail[u]
        return goto[u].get(ch, 0)

    # Keep only states that do not contain a banned substring.
    good = [i for i in range(len(goto)) if not bad[i]]
    index = {s: k for k, s in enumerate(good)}
    k = len(good)

    # Transition matrix over safe states.
    M = [[0] * k for _ in range(k)]
    for s in good:
        for ch in alphabet:
            t = step(s, ch)
            if not bad[t]:
                M[index[s]][index[t]] += 1

    def mat_mul(A, B):
        C = [[0] * k for _ in range(k)]
        for i in range(k):
            Ai = A[i]
            Ci = C[i]
            for p in range(k):
                a = Ai[p]
                if a:
                    Bp = B[p]
                    for j in range(k):
                        Ci[j] += a * Bp[j]
            for j in range(k):
                Ci[j] %= MOD
        return C

    # Compute M^n by fast exponentiation.
    result = [[int(i == j) for j in range(k)] for i in range(k)]
    base = M
    e = n
    while e:
        if e & 1:
            result = mat_mul(result, base)
        base = mat_mul(base, base)
        e >>= 1

    # Start from the root (index 0) and sum over all end states.
    return sum(result[index[0]]) % MOD
