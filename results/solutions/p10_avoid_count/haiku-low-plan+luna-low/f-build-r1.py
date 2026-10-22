def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    if n == 0:
        return 1

    char_index = {ch: i for i, ch in enumerate(alphabet)}
    sigma = len(alphabet)

    # Trie nodes: transitions, failure link, and whether the node is terminal.
    edges = [[-1] * sigma]
    fail = [0]
    dead = [False]

    for word in banned:
        node = 0
        for ch in word:
            c = char_index[ch]
            nxt = edges[node][c]
            if nxt == -1:
                nxt = len(edges)
                edges[node][c] = nxt
                edges.append([-1] * sigma)
                fail.append(0)
                dead.append(False)
            node = nxt
        dead[node] = True

    # Build failure links and propagate terminal status.
    queue = []
    for c in range(sigma):
        child = edges[0][c]
        if child != -1:
            queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        dead[node] = dead[node] or dead[fail[node]]

        for c in range(sigma):
            child = edges[node][c]
            if child != -1:
                fail[child] = edges[fail[node]][c]
                queue.append(child)

    # Complete missing transitions using failure links.
    for c in range(sigma):
        if edges[0][c] == -1:
            edges[0][c] = 0

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        for c in range(sigma):
            if edges[node][c] == -1:
                edges[node][c] = edges[fail[node]][c]

    live_nodes = [i for i in range(len(edges)) if not dead[i]]
    compact = {node: i for i, node in enumerate(live_nodes)}
    m = len(live_nodes)

    matrix = [[0] * m for _ in range(m)]
    for node in live_nodes:
        u = compact[node]
        for c in range(sigma):
            nxt = edges[node][c]
            if not dead[nxt]:
                matrix[u][compact[nxt]] += 1

    def multiply(a, b):
        size = len(a)
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, aik in enumerate(a[i]):
                if aik:
                    for j, bkj in enumerate(b[k]):
                        if bkj:
                            result[i][j] = (result[i][j] + aik * bkj) % MOD
        return result

    power = n
    while power:
        if power & 1:
            # Keep a row vector for the root state.
            if 'vector' not in locals():
                vector = [0] * m
                vector[compact[0]] = 1
            new_vector = [0] * m
            for i, value in enumerate(vector):
                if value:
                    for j, ways in enumerate(matrix[i]):
                        if ways:
                            new_vector[j] = (new_vector[j] + value * ways) % MOD
            vector = new_vector
        power >>= 1
        if power:
            matrix = multiply(matrix, matrix)

    if 'vector' not in locals():
        return 1
    return sum(vector) % MOD
