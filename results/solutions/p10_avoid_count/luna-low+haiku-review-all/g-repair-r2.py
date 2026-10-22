def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie, collapsing duplicates and ignoring strings that have
    # an already-banned string as a prefix.
    children = [{}]
    terminal = [False]
    for word in banned:
        node = 0
        blocked = False
        for ch in word:
            if terminal[node]:
                blocked = True
                break
            nxt = children[node].get(ch)
            if nxt is None:
                nxt = len(children)
                children[node][ch] = nxt
                children.append({})
                terminal.append(False)
            node = nxt
        if not blocked:
            terminal[node] = True

    # Aho-Corasick failure links.
    fail = [0] * len(children)
    queue = []
    for ch, node in children[0].items():
        queue.append(node)

    head = 0
    while head < len(queue):
        v = queue[head]
        head += 1
        if terminal[fail[v]]:
            terminal[v] = True
        for ch, u in children[v].items():
            f = fail[v]
            while f and ch not in children[f]:
                f = fail[f]
            fail[u] = children[f].get(ch, 0)
            queue.append(u)

    # Keep only non-terminal automaton states.
    states = [v for v in range(len(children)) if not terminal[v]]
    index = {v: i for i, v in enumerate(states)}
    m = len(states)
    if m == 0:
        return 1 if n == 0 else 0

    # Transition counts, including multiple alphabet characters leading
    # to the same state.
    matrix = [[0] * m for _ in range(m)]
    for v in states:
        i = index[v]
        for ch in alphabet:
            u = v
            while u and ch not in children[u]:
                u = fail[u]
            u = children[u].get(ch, 0)
            if not terminal[u]:
                j = index[u]
                matrix[i][j] = (matrix[i][j] + 1) % MOD

    vec = [0] * m
    vec[index[0]] = 1

    def multiply(a, b):
        size = len(a)
        out = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, x in enumerate(a[i]):
                if x:
                    for j, y in enumerate(b[k]):
                        if y:
                            out[i][j] = (out[i][j] + x * y) % MOD
        return out

    def apply(vec, mat):
        size = len(vec)
        out = [0] * size
        for i, x in enumerate(vec):
            if x:
                for j, y in enumerate(mat[i]):
                    if y:
                        out[j] = (out[j] + x * y) % MOD
        return out

    while n:
        if n & 1:
            vec = apply(vec, matrix)
        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(vec) % MOD
