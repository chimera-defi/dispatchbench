def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    nexts = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            if ch not in nexts[node]:
                nexts[node][ch] = len(nexts)
                nexts.append({})
                terminal.append(False)
            node = nexts[node][ch]
        terminal[node] = True

    from collections import deque

    fail = [0] * len(nexts)
    q = deque()

    for ch in alphabet:
        if ch in nexts[0]:
            child = nexts[0][ch]
            q.append(child)
            fail[child] = 0
        else:
            nexts[0][ch] = 0

    while q:
        v = q.popleft()
        terminal[v] |= terminal[fail[v]]

        for ch in alphabet:
            if ch in nexts[v]:
                u = nexts[v][ch]
                fail[u] = nexts[fail[v]][ch]
                q.append(u)
            else:
                nexts[v][ch] = nexts[fail[v]][ch]

    valid = [i for i in range(len(nexts)) if not terminal[i]]
    index = {v: i for i, v in enumerate(valid)}
    size = len(valid)

    trans = [[0] * size for _ in range(size)]
    for v in valid:
        i = index[v]
        for ch in alphabet:
            u = nexts[v][ch]
            if not terminal[u]:
                trans[i][index[u]] += 1

    def mat_mul(a, b):
        m = len(a)
        c = [[0] * m for _ in range(m)]
        for i in range(m):
            for k in range(m):
                if a[i][k]:
                    aik = a[i][k]
                    for j in range(m):
                        c[i][j] = (c[i][j] + aik * b[k][j]) % MOD
        return c

    def vec_mul(v, m):
        result = [0] * size
        for i, value in enumerate(v):
            if value:
                for j in range(size):
                    result[j] = (result[j] + value * m[i][j]) % MOD
        return result

    result = [0] * size
    result[index[0]] = 1

    while n:
        if n & 1:
            result = vec_mul(result, trans)
        trans = mat_mul(trans, trans)
        n >>= 1

    return sum(result) % MOD
