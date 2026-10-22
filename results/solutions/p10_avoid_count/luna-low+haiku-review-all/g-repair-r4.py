def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    chars = set(alphabet)

    # Build a trie, ignoring duplicates and patterns already covered by a
    # shorter banned pattern.
    patterns = sorted(set(banned), key=len)
    kept = []
    for pattern in patterns:
        if not any(short in pattern for short in kept):
            kept.append(pattern)

    children = [{}]
    terminal = [False]
    for pattern in kept:
        node = 0
        for ch in pattern:
            if ch not in children[node]:
                children[node][ch] = len(children)
                children.append({})
                terminal.append(False)
            node = children[node][ch]
        terminal[node] = True

    # Aho-Corasick failure links and transitions.
    size = len(children)
    fail = [0] * size
    queue = []
    for ch in alphabet:
        nxt = children[0].get(ch)
        if nxt is not None:
            queue.append(nxt)

    for node in queue:
        fail[node] = 0

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        terminal[node] |= terminal[fail[node]]
        for ch in alphabet:
            nxt = children[node].get(ch)
            if nxt is not None:
                f = fail[node]
                while f and ch not in children[f]:
                    f = fail[f]
                fail[nxt] = children[f].get(ch, 0)
                queue.append(nxt)

    safe_nodes = [i for i in range(size) if not terminal[i]]
    if len(safe_nodes) == 1 and terminal[0]:
        return 0

    index = {node: i for i, node in enumerate(safe_nodes)}
    m = len(safe_nodes)
    if m == 0:
        return 0

    matrix = [[0] * m for _ in range(m)]
    for node in safe_nodes:
        row = index[node]
        for ch in alphabet:
            nxt = node
            while nxt and ch not in children[nxt]:
                nxt = fail[nxt]
            nxt = children[nxt].get(ch, 0)
            if not terminal[nxt]:
                matrix[row][index[nxt]] += 1
        for j in range(m):
            matrix[row][j] %= MOD

    def multiply(a, b):
        out = [[0] * m for _ in range(m)]
        for i in range(m):
            for k, av in enumerate(a[i]):
                if av:
                    bk = b[k]
                    for j, bv in enumerate(bk):
                        if bv:
                            out[i][j] = (out[i][j] + av * bv) % MOD
        return out

    def apply(vec, mat):
        result = [0] * m
        for i, value in enumerate(vec):
            if value:
                row = mat[i]
                for j, entry in enumerate(row):
                    if entry:
                        result[j] = (result[j] + value * entry) % MOD
        return result

    vector = [0] * m
    vector[index[0]] = 1
    while n:
        if n & 1:
            vector = apply(vector, matrix)
        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(vector) % MOD
