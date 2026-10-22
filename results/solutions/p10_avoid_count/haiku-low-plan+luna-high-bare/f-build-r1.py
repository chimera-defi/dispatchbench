def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    if n == 0:
        return 1

    char_id = {ch: i for i, ch in enumerate(alphabet)}
    sigma = len(alphabet)

    edges = [[-1] * sigma]
    fail = [0]
    dead = [False]

    for word in banned:
        node = 0
        for ch in word:
            c = char_id[ch]
            nxt = edges[node][c]
            if nxt == -1:
                nxt = len(edges)
                edges[node][c] = nxt
                edges.append([-1] * sigma)
                fail.append(0)
                dead.append(False)
            node = nxt
        dead[node] = True

    queue = []
    for c in range(sigma):
        child = edges[0][c]
        if child == -1:
            edges[0][c] = 0
        else:
            fail[child] = 0
            queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        dead[node] = dead[node] or dead[fail[node]]

        for c in range(sigma):
            child = edges[node][c]
            if child == -1:
                edges[node][c] = edges[fail[node]][c]
            else:
                fail[child] = edges[fail[node]][c]
                queue.append(child)

    live_nodes = [i for i, is_dead in enumerate(dead) if not is_dead]
    index = {node: i for i, node in enumerate(live_nodes)}
    size = len(live_nodes)

    matrix = [[0] * size for _ in range(size)]
    for node in live_nodes:
        u = index[node]
        for c in range(sigma):
            nxt = edges[node][c]
            if not dead[nxt]:
                v = index[nxt]
                matrix[u][v] += 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            row = result[i]
            for k, value in enumerate(a[i]):
                if value:
                    brow = b[k]
                    for j in range(size):
                        row[j] += value * brow[j]
            for j in range(size):
                row[j] %= MOD
        return result

    result = [[int(i == j) for j in range(size)] for i in range(size)]
    exponent = n
    while exponent:
        if exponent & 1:
            result = multiply(result, matrix)
        exponent >>= 1
        if exponent:
            matrix = multiply(matrix, matrix)

    return sum(result[index[0]]) % MOD
