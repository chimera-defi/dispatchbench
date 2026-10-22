from collections import deque


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie of banned words. A word that already has a banned prefix
    # is redundant, so it is skipped.
    children = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            if terminal[node]:
                break
            nxt = children[node].get(ch)
            if nxt is None:
                nxt = len(children)
                children[node][ch] = nxt
                children.append({})
                terminal.append(False)
            node = nxt
        else:
            terminal[node] = True

    # Aho-Corasick: failure links, and mark states that contain a banned word.
    size = len(children)
    fail = [0] * size
    bad = terminal[:]
    q = deque()

    for nxt in children[0].values():
        q.append(nxt)

    while q:
        v = q.popleft()
        bad[v] = bad[v] or bad[fail[v]]
        for ch, u in children[v].items():
            f = fail[v]
            while f and ch not in children[f]:
                f = fail[f]
            fail[u] = children[f].get(ch, 0) if children[f].get(ch, 0) != u else 0
            q.append(u)

    # Only states that do not contain a banned word are kept.
    safe_states = [s for s in range(size) if not bad[s]]
    index = {s: i for i, s in enumerate(safe_states)}
    m = len(safe_states)  # always >= 1, since the root is never terminal

    # Transition matrix over safe states: mat[i][j] = number of characters
    # moving state i to state j without entering a banned state.
    chars = list(alphabet)
    mat = [[0] * m for _ in range(m)]
    for state in safe_states:
        for ch in chars:
            cur = state
            while cur and ch not in children[cur]:
                cur = fail[cur]
            nxt = children[cur].get(ch, 0)
            if not bad[nxt]:
                mat[index[state]][index[nxt]] += 1

    # Row vector starting at the root; the result is vec * mat^n.
    vec = [0] * m
    vec[index[0]] = 1

    def vec_mul(v, matrix):
        out = [0] * m
        for i in range(m):
            if v[i]:
                vi = v[i]
                row = matrix[i]
                for j in range(m):
                    if row[j]:
                        out[j] = (out[j] + vi * row[j]) % MOD
        return out

    def mat_mul(a, b):
        out = [[0] * m for _ in range(m)]
        for i in range(m):
            for k in range(m):
                x = a[i][k]
                if x:
                    bk = b[k]
                    oi = out[i]
                    for j in range(m):
                        if bk[j]:
                            oi[j] = (oi[j] + x * bk[j]) % MOD
        return out

    power = n
    while power:
        if power & 1:
            vec = vec_mul(vec, mat)
        power >>= 1
        if power:
            mat = mat_mul(mat, mat)

    return sum(vec) % MOD
