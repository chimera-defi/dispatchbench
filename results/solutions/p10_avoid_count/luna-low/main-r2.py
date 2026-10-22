def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    if n == 0:
        return 1

    chars = list(alphabet)
    char_index = {ch: i for i, ch in enumerate(chars)}

    # Build a trie, merging duplicates and marking terminal nodes.
    children = [{}]
    terminal = [False]
    for word in banned:
        node = 0
        for ch in word:
            idx = char_index[ch]
            nxt = children[node].get(idx)
            if nxt is None:
                nxt = len(children)
                children[node][idx] = nxt
                children.append({})
                terminal.append(False)
            node = nxt
        terminal[node] = True

    # Aho-Corasick failure links; any node matching a banned word
    # (including via a suffix) is forbidden.
    fail = [0] * len(children)
    bad = terminal[:]
    queue = []
    for nxt in children[0].values():
        queue.append(nxt)

    head = 0
    while head < len(queue):
        v = queue[head]
        head += 1
        bad[v] = bad[v] or bad[fail[v]]
        for c, nxt in children[v].items():
            f = fail[v]
            while f and c not in children[f]:
                f = fail[f]
            fail[nxt] = children[f].get(c, 0)
            queue.append(nxt)

    # Keep only non-forbidden states reachable from the root.
    states = [0]
    state_id = {0: 0}
    transitions = []
    pos = 0
    while pos < len(states):
        v = states[pos]
        row = []
        for c in range(len(chars)):
            u = v
            while u and c not in children[u]:
                u = fail[u]
            u = children[u].get(c, 0)
            if not bad[u]:
                if u not in state_id:
                    state_id[u] = len(states)
                    states.append(u)
                row.append(state_id[u])
            else:
                row.append(-1)
        transitions.append(row)
        pos += 1

    size = len(states)
    matrix = [[0] * size for _ in range(size)]
    for i, row in enumerate(transitions):
        for j in row:
            if j >= 0:
                matrix[i][j] = (matrix[i][j] + 1) % MOD

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, x in enumerate(a[i]):
                if x:
                    bk = b[k]
                    for j, y in enumerate(bk):
                        if y:
                            result[i][j] = (result[i][j] + x * y) % MOD
        return result

    def apply(vec, mat):
        out = [0] * size
        for i, x in enumerate(vec):
            if x:
                for j, y in enumerate(mat[i]):
                    if y:
                        out[j] = (out[j] + x * y) % MOD
        return out

    vec = [0] * size
    vec[0] = 1
    while n:
        if n & 1:
            vec = apply(vec, matrix)
        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(vec) % MOD
