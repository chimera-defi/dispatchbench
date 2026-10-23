def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    if n == 0:
        return 1

    index = {ch: i for i, ch in enumerate(alphabet)}
    next_nodes = [[-1] * len(alphabet)]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            c = index[ch]
            if next_nodes[node][c] == -1:
                next_nodes[node][c] = len(next_nodes)
                next_nodes.append([-1] * len(alphabet))
                terminal.append(False)
            node = next_nodes[node][c]
        terminal[node] = True

    fail = [0] * len(next_nodes)
    queue = []

    for c in range(len(alphabet)):
        child = next_nodes[0][c]
        if child == -1:
            next_nodes[0][c] = 0
        else:
            queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1

        terminal[node] |= terminal[fail[node]]

        for c in range(len(alphabet)):
            child = next_nodes[node][c]
            if child == -1:
                next_nodes[node][c] = next_nodes[fail[node]][c]
            else:
                fail[child] = next_nodes[fail[node]][c]
                queue.append(child)

    safe = [i for i, bad in enumerate(terminal) if not bad]
    remap = {node: i for i, node in enumerate(safe)}
    size = len(safe)

    matrix = [[0] * size for _ in range(size)]
    for node in safe:
        i = remap[node]
        for c in range(len(alphabet)):
            target = next_nodes[node][c]
            if not terminal[target]:
                j = remap[target]
                matrix[i][j] = (matrix[i][j] + 1) % MOD

    def mat_mul(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k in range(size):
                if a[i][k]:
                    aik = a[i][k]
                    for j in range(size):
                        result[i][j] = (result[i][j] + aik * b[k][j]) % MOD
        return result

    vector = [0] * size
    vector[remap[0]] = 1

    while n:
        if n & 1:
            new_vector = [0] * size
            for i in range(size):
                if vector[i]:
                    for j in range(size):
                        new_vector[j] = (
                            new_vector[j] + vector[i] * matrix[i][j]
                        ) % MOD
            vector = new_vector
        n >>= 1
        if n:
            matrix = mat_mul(matrix, matrix)

    return sum(vector) % MOD
