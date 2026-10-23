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

    fail = [0] * len(children)
    bad = terminal[:]
    queue = []

    for child in children[0].values():
        queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1

        bad[node] = bad[node] or bad[fail[node]]

        for ch, child in children[node].items():
            f = fail[node]
            while f and ch not in children[f]:
                f = fail[f]
            if ch in children[f]:
                fail[child] = children[f][ch]
            else:
                fail[child] = 0
            queue.append(child)

    valid_states = [i for i in range(len(children)) if not bad[i]]
    index = {node: i for i, node in enumerate(valid_states)}
    size = len(valid_states)

    matrix = [[0] * size for _ in range(size)]

    for node in valid_states:
        i = index[node]
        for ch in alphabet:
            cur = node
            while cur and ch not in children[cur]:
                cur = fail[cur]

            if ch in children[cur]:
                nxt = children[cur][ch]
            else:
                nxt = 0

            if not bad[nxt]:
                matrix[i][index[nxt]] += 1
                if matrix[i][index[nxt]] >= MOD:
                    matrix[i][index[nxt]] -= MOD

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
