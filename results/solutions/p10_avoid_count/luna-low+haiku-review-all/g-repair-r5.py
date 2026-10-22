def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie, omitting words that already contain a banned word.
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

    # Aho-Corasick failure links and transitions.
    from collections import deque

    size = len(children)
    fail = [0] * size
    bad = terminal[:]
    q = deque()

    for nxt in children[0].values():
        q.append(nxt)

    while q:
        v = q.popleft()
        bad[v] |= bad[fail[v]]
        for ch, u in children[v].items():
            f = fail[v]
            while f and ch not in children[f]:
                f = fail[f]
            fail[u] = children[f].get(ch, 0)
            q.append(u)

    chars = list(alphabet)
    transitions = []
    safe_states = [i for i in range(size) if not bad[i]]
    index = {state: i for i, state in enumerate(safe_states)}

    for state in safe_states:
        row = []
        for ch in chars:
            cur = state
            while cur and ch not in children[cur]:
                cur = fail[cur]
            nxt = children[cur].get(ch, 0)
            row.append(index.get(nxt, -1))
        transitions.append(row)

    m = len(safe_states)
    if m == 0:
        return 0

    # mat[j][i] = number of ways to move from state i to state j in one step,
    # so that mat @ vec pushes counts forward from the root.
    mat = [[0] * m for _ in range(m)]
    for i, row in enumerate(transitions):
        for j in row:
            if j >= 0:
                mat[j][i] = (mat[j][i] + 1) % MOD

    vec = [0] * m
    vec[index[0]] = 1

    def mat_vec_mul(matrix, vector):
        out = [0] * m
        for i in range(m):
            total = 0
            for j, value in enumerate(matrix[i]):
                if value:
                    total += value * vector[j]
            out[i] = total % MOD
        return out

    def mat_mul(a, b):
        out = [[0] * m for _ in range(m)]
        for i in range(m):
            for k, x in enumerate(a[i]):
                if x:
                    for j, y in enumerate(b[k]):
                        if y:
                            out[i][j] = (out[i][j] + x * y) % MOD
        return out

    power = n
    while power:
        if power & 1:
            vec = mat_vec_mul(mat, vec)
        power >>= 1
        if power:
            mat = mat_mul(mat, mat)

    return sum(vec) % MOD
