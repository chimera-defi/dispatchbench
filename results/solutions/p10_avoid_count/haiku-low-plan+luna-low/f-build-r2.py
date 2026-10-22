def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    sigma = len(alphabet)
    char_id = {c: i for i, c in enumerate(alphabet)}

    # Trie nodes: transitions, failure links, and whether the node is terminal.
    go = [[-1] * sigma]
    fail = [0]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            c = char_id[ch]
            nxt = go[node][c]
            if nxt == -1:
                nxt = len(go)
                go[node][c] = nxt
                go.append([-1] * sigma)
                fail.append(0)
                terminal.append(False)
            node = nxt
        terminal[node] = True

    # Complete transitions and propagate terminal status through failure links.
    from collections import deque

    q = deque()
    for c in range(sigma):
        nxt = go[0][c]
        if nxt == -1:
            go[0][c] = 0
        else:
            fail[nxt] = 0
            q.append(nxt)

    while q:
        node = q.popleft()
        terminal[node] = terminal[node] or terminal[fail[node]]
        for c in range(sigma):
            nxt = go[node][c]
            if nxt == -1:
                go[node][c] = go[fail[node]][c]
            else:
                fail[nxt] = go[fail[node]][c]
                q.append(nxt)

    safe = [i for i in range(len(go)) if not terminal[i]]
    index = {node: i for i, node in enumerate(safe)}
    k = len(safe)

    if k == 0:
        return 0

    matrix = [[0] * k for _ in range(k)]
    for node in safe:
        i = index[node]
        for c in range(sigma):
            nxt = go[node][c]
            if not terminal[nxt]:
                j = index[nxt]
                matrix[i][j] = (matrix[i][j] + 1) % MOD

    vec = [0] * k
    vec[index[0]] = 1

    def vec_mul(v, mat):
        out = [0] * k
        for i, value in enumerate(v):
            if value:
                for j, weight in enumerate(mat[i]):
                    if weight:
                        out[j] = (out[j] + value * weight) % MOD
        return out

    def mat_mul(a, b):
        out = [[0] * k for _ in range(k)]
        for i in range(k):
            for mid, x in enumerate(a[i]):
                if x:
                    brow = b[mid]
                    for j, y in enumerate(brow):
                        if y:
                            out[i][j] = (out[i][j] + x * y) % MOD
        return out

    while n:
        if n & 1:
            vec = vec_mul(vec, matrix)
        n >>= 1
        if n:
            matrix = mat_mul(matrix, matrix)

    return sum(vec) % MOD
