def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    next_nodes = [{}]
    fail = [0]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            if ch not in next_nodes[node]:
                next_nodes[node][ch] = len(next_nodes)
                next_nodes.append({})
                fail.append(0)
                terminal.append(False)
            node = next_nodes[node][ch]
        terminal[node] = True

    from collections import deque

    q = deque()
    for ch in alphabet:
        child = next_nodes[0].get(ch)
        if child is not None:
            q.append(child)
            fail[child] = 0

    while q:
        node = q.popleft()
        terminal[node] |= terminal[fail[node]]

        for ch, child in next_nodes[node].items():
            q.append(child)
            f = fail[node]
            while f and ch not in next_nodes[f]:
                f = fail[f]
            fail[child] = next_nodes[f].get(ch, 0)

    good = [i for i in range(len(next_nodes)) if not terminal[i]]
    index = {node: i for i, node in enumerate(good)}
    size = len(good)

    matrix = [[0] * size for _ in range(size)]

    for node in good:
        i = index[node]
        for ch in alphabet:
            cur = node
            while cur and ch not in next_nodes[cur]:
                cur = fail[cur]
            nxt = next_nodes[cur].get(ch, 0)
            if not terminal[nxt]:
                matrix[i][index[nxt]] = (matrix[i][index[nxt]] + 1) % MOD

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k in range(size):
                if a[i][k]:
                    aik = a[i][k]
                    for j in range(size):
                        result[i][j] = (result[i][j] + aik * b[k][j]) % MOD
        return result

    def vector_multiply(v, m):
        result = [0] * size
        for i in range(size):
            if v[i]:
                for j in range(size):
                    result[j] = (result[j] + v[i] * m[i][j]) % MOD
        return result

    vector = [0] * size
    vector[index[0]] = 1

    while n:
        if n & 1:
            vector = vector_multiply(vector, matrix)
        matrix = multiply(matrix, matrix)
        n >>= 1

    return sum(vector) % MOD
