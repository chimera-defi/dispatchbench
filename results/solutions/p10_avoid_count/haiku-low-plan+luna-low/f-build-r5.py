def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    char_to_idx = {ch: i for i, ch in enumerate(alphabet)}
    sigma = len(alphabet)

    # Trie nodes and terminal flags.
    children = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            c = char_to_idx[ch]
            if c not in children[node]:
                children[node][c] = len(children)
                children.append({})
                terminal.append(False)
            node = children[node][c]
        terminal[node] = True

    # Failure links and propagated dead flags.
    fail = [0] * len(children)
    dead = terminal[:]
    queue = []

    for c in range(sigma):
        child = children[0].get(c)
        if child is not None:
            queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        dead[node] = dead[node] or dead[fail[node]]

        for c, child in children[node].items():
            f = fail[node]
            while f and c not in children[f]:
                f = fail[f]
            fail[child] = children[f].get(c, 0)
            queue.append(child)

    # Build transitions only for live states.
    live_nodes = [i for i in range(len(children)) if not dead[i]]
    index = {node: i for i, node in enumerate(live_nodes)}
    size = len(live_nodes)
    matrix = [[0] * size for _ in range(size)]

    for node in live_nodes:
        i = index[node]
        for c in range(sigma):
            state = node
            while state and c not in children[state]:
                state = fail[state]
            nxt = children[state].get(c, 0)
            if not dead[nxt]:
                j = index[nxt]
                matrix[i][j] += 1

    # Vector-matrix product.
    def vec_mul(vec, mat):
        out = [0] * len(vec)
        for i, value in enumerate(vec):
            if value:
                for j, count in enumerate(mat[i]):
                    if count:
                        out[j] = (out[j] + value * count) % MOD
        return out

    # Matrix multiplication.
    def mat_mul(a, b):
        s = len(a)
        out = [[0] * s for _ in range(s)]
        for i in range(s):
            for k, x in enumerate(a[i]):
                if x:
                    for j, y in enumerate(b[k]):
                        if y:
                            out[i][j] = (out[i][j] + x * y) % MOD
        return out

    vector = [0] * size
    vector[index[0]] = 1
    power = matrix

    while n:
        if n & 1:
            vector = vec_mul(vector, power)
        n >>= 1
        if n:
            power = mat_mul(power, power)

    return sum(vector) % MOD
