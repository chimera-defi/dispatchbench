def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    children = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            if ch not in children[node]:
                children[node][ch] = len(children)
                children.append({})
                terminal.append(False)
            node = children[node][ch]
        terminal[node] = True

    k = len(alphabet)
    go = [[-1] * k for _ in children]
    fail = [0] * len(children)
    queue = []

    for c, ch in enumerate(alphabet):
        child = children[0].get(ch)
        if child is None:
            go[0][c] = 0
        else:
            go[0][c] = child
            queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1

        terminal[node] |= terminal[fail[node]]

        for c, ch in enumerate(alphabet):
            child = children[node].get(ch)
            if child is None:
                go[node][c] = go[fail[node]][c]
            else:
                go[node][c] = child
                fail[child] = go[fail[node]][c]
                queue.append(child)

    safe_nodes = [i for i, is_terminal in enumerate(terminal) if not is_terminal]
    index = {node: i for i, node in enumerate(safe_nodes)}
    size = len(safe_nodes)

    matrix = [[0] * size for _ in range(size)]
    for node in safe_nodes:
        i = index[node]
        for c in range(k):
            nxt = go[node][c]
            if not terminal[nxt]:
                j = index[nxt]
                matrix[i][j] += 1

    vector = [0] * size
    vector[index[0]] = 1

    def multiply_matrices(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for t, value in enumerate(a[i]):
                if value:
                    for j, other in enumerate(b[t]):
                        if other:
                            result[i][j] = (result[i][j] + value * other) % MOD
        return result

    while n:
        if n & 1:
            next_vector = [0] * size
            for i, value in enumerate(vector):
                if value:
                    for j, ways in enumerate(matrix[i]):
                        if ways:
                            next_vector[j] = (next_vector[j] + value * ways) % MOD
            vector = next_vector
        n >>= 1
        if n:
            matrix = multiply_matrices(matrix, matrix)

    return sum(vector) % MOD
