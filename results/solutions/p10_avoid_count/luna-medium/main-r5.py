def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie, ignoring duplicates and patterns extending an already
    # forbidden prefix.
    children = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        skip = False
        for ch in word:
            if terminal[node]:
                skip = True
                break
            nxt = children[node].get(ch)
            if nxt is None:
                nxt = len(children)
                children[node][ch] = nxt
                children.append({})
                terminal.append(False)
            node = nxt
        if not skip:
            terminal[node] = True

    # Aho-Corasick failure links, with forbidden status propagated.
    failure = [0] * len(children)
    queue = []
    for ch, node in children[0].items():
        queue.append(node)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        if terminal[failure[node]]:
            terminal[node] = True
        for ch, nxt in children[node].items():
            f = failure[node]
            while f and ch not in children[f]:
                f = failure[f]
            failure[nxt] = children[f].get(ch, 0)
            queue.append(nxt)

    # Keep only non-forbidden states and build transitions between them.
    states = [i for i in range(len(children)) if not terminal[i]]
    index = {node: i for i, node in enumerate(states)}
    transitions = []
    for node in states:
        row = []
        for ch in alphabet:
            cur = node
            while cur and ch not in children[cur]:
                cur = failure[cur]
            nxt = children[cur].get(ch, 0)
            row.append(index.get(nxt, -1))
        transitions.append(row)

    size = len(states)
    vec = [0] * size
    vec[index[0]] = 1
    matrix = [[0] * size for _ in range(size)]
    for i, row in enumerate(transitions):
        for j in row:
            if j >= 0:
                matrix[i][j] = (matrix[i][j] + 1) % MOD

    def multiply_vec(v, m):
        out = [0] * size
        for i, x in enumerate(v):
            if x:
                for j, y in enumerate(m[i]):
                    if y:
                        out[j] = (out[j] + x * y) % MOD
        return out

    def square(m):
        out = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, x in enumerate(m[i]):
                if x:
                    for j, y in enumerate(m[k]):
                        if y:
                            out[i][j] = (out[i][j] + x * y) % MOD
        return out

    while n:
        if n & 1:
            vec = multiply_vec(vec, matrix)
        n >>= 1
        if n:
            matrix = square(matrix)

    return sum(vec) % MOD
