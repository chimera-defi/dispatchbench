def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie of forbidden strings, marking terminal nodes as unsafe.
    children = [{}]
    terminal = [False]
    for word in banned:
        node = 0
        for ch in word:
            nxt = children[node].get(ch)
            if nxt is None:
                nxt = len(children)
                children[node][ch] = nxt
                children.append({})
                terminal.append(False)
            node = nxt
        terminal[node] = True

    # Aho–Corasick failure links; propagate unsafe status through suffixes.
    fail = [0] * len(children)
    queue = []
    for ch in alphabet:
        nxt = children[0].get(ch)
        if nxt is not None:
            queue.append(nxt)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        terminal[node] = terminal[node] or terminal[fail[node]]
        for ch in alphabet:
            nxt = children[node].get(ch)
            if nxt is not None:
                f = fail[node]
                while f and ch not in children[f]:
                    f = fail[f]
                fail[nxt] = children[f].get(ch, 0)
                queue.append(nxt)

    # Keep only safe trie states and construct their transitions.
    states = [i for i in range(len(children)) if not terminal[i]]
    index = {node: i for i, node in enumerate(states)}
    size = len(states)
    trans = [[-1] * len(alphabet) for _ in range(size)]

    for i, node in enumerate(states):
        for j, ch in enumerate(alphabet):
            cur = node
            while cur and ch not in children[cur]:
                cur = fail[cur]
            nxt = children[cur].get(ch, 0)
            if not terminal[nxt]:
                trans[i][j] = index[nxt]

    # Count walks of length n in the safe-state automaton using matrix powers.
    mat = [[0] * size for _ in range(size)]
    for i in range(size):
        for nxt in trans[i]:
            if nxt >= 0:
                mat[i][nxt] = (mat[i][nxt] + 1) % MOD

    vec = [0] * size
    vec[index[0]] = 1

    def multiply_matrix(a, b):
        out = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, value in enumerate(a[i]):
                if value:
                    for j, other in enumerate(b[k]):
                        if other:
                            out[i][j] = (out[i][j] + value * other) % MOD
        return out

    def multiply_vector(v, a):
        out = [0] * size
        for i, value in enumerate(v):
            if value:
                for j, other in enumerate(a[i]):
                    if other:
                        out[j] = (out[j] + value * other) % MOD
        return out

    while n:
        if n & 1:
            vec = multiply_vector(vec, mat)
        n >>= 1
        if n:
            mat = multiply_matrix(mat, mat)

    return sum(vec) % MOD
