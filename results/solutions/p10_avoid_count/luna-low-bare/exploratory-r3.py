def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie, omitting words that have a previously inserted banned
    # word as a prefix.
    children = [{}]
    terminal = [False]
    for word in sorted(set(banned), key=len):
        node = 0
        already_forbidden = False
        for ch in word:
            if terminal[node]:
                already_forbidden = True
                break
            if ch not in children[node]:
                children[node][ch] = len(children)
                children.append({})
                terminal.append(False)
            node = children[node][ch]
        if not already_forbidden:
            terminal[node] = True

    # Aho-Corasick failure links and transitions. Terminal states and states
    # whose failure target is terminal are forbidden.
    failure = [0] * len(children)
    queue = []
    for ch, nxt in children[0].items():
        queue.append(nxt)

    order = [0]
    head = 0
    while head < len(queue):
        v = queue[head]
        head += 1
        order.append(v)
        for ch, nxt in children[v].items():
            f = failure[v]
            while f and ch not in children[f]:
                f = failure[f]
            failure[nxt] = children[f].get(ch, 0)
            if terminal[failure[nxt]]:
                terminal[nxt] = True
            queue.append(nxt)

    states = [v for v in range(len(children)) if not terminal[v]]
    if not states:
        return 0

    idx = {v: i for i, v in enumerate(states)}
    m = len(states)
    matrix = [[0] * m for _ in range(m)]

    for v in states:
        i = idx[v]
        for ch in alphabet:
            u = v
            while u and ch not in children[u]:
                u = failure[u]
            u = children[u].get(ch, 0)
            if not terminal[u]:
                j = idx[u]
                matrix[i][j] = (matrix[i][j] + 1) % MOD

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

    def apply(vector, mat):
        out = [0] * len(vector)
        for i, x in enumerate(vector):
            if x:
                for j, y in enumerate(mat[i]):
                    if y:
                        out[j] = (out[j] + x * y) % MOD
        return out

    vector = [0] * m
    vector[idx[0]] = 1
    while n:
        if n & 1:
            vector = apply(vector, matrix)
        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(vector) % MOD
