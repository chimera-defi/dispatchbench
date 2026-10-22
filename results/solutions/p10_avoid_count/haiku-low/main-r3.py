from collections import deque


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build an Aho-Corasick automaton over the banned strings.
    goto = [{}]
    bad = [False]
    for word in banned:
        s = 0
        for ch in word:
            if ch not in goto[s]:
                goto.append({})
                bad.append(False)
                goto[s][ch] = len(goto) - 1
            s = goto[s][ch]
        bad[s] = True

    # Compute failure links and propagate "bad" along them (BFS order).
    fail = [0] * len(goto)
    q = deque()
    for ch, v in goto[0].items():
        fail[v] = 0
        q.append(v)
    while q:
        u = q.popleft()
        for ch, v in goto[u].items():
            f = fail[u]
            while f and ch not in goto[f]:
                f = fail[f]
            fail[v] = goto[f].get(ch, 0)
            bad[v] = bad[v] or bad[fail[v]]
            q.append(v)

    def delta(s, ch):
        while s and ch not in goto[s]:
            s = fail[s]
        return goto[s].get(ch, 0)

    # Keep only states that do not contain a banned substring.
    alive = [i for i in range(len(goto)) if not bad[i]]
    idx = {s: i for i, s in enumerate(alive)}
    k = len(alive)

    # Transition matrix among safe states.
    M = [[0] * k for _ in range(k)]
    for s in alive:
        for ch in alphabet:
            t = delta(s, ch)
            if not bad[t]:
                M[idx[s]][idx[t]] += 1

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

    # Compute M^n by fast exponentiation, starting from the identity.
    result = [[int(i == j) for j in range(k)] for i in range(k)]
    base = M
    e = n
    while e:
        if e & 1:
            result = mat_mul(result, base)
        base = mat_mul(base, base)
        e >>= 1

    # Start at the root (always safe, since banned strings are non-empty).
    return sum(result[idx[0]]) % MOD
