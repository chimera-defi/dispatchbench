def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    trie = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            if ch not in trie[node]:
                trie[node][ch] = len(trie)
                trie.append({})
                terminal.append(False)
            node = trie[node][ch]
        terminal[node] = True

    size = len(trie)
    fail = [0] * size
    queue = []

    for child in trie[0].values():
        queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1

        terminal[node] |= terminal[fail[node]]

        for ch, child in trie[node].items():
            f = fail[node]
            while f and ch not in trie[f]:
                f = fail[f]
            fail[child] = trie[f].get(ch, 0)
            queue.append(child)

    matrix = [[0] * size for _ in range(size)]

    for node in range(size):
        if terminal[node]:
            continue
        for ch in alphabet:
            current = node
            while current and ch not in trie[current]:
                current = fail[current]
            nxt = trie[current].get(ch, 0)
            if not terminal[nxt]:
                matrix[node][nxt] = (matrix[node][nxt] + 1) % MOD

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k in range(size):
                if a[i][k]:
                    aik = a[i][k]
                    for j in range(size):
                        result[i][j] = (result[i][j] + aik * b[k][j]) % MOD
        return result

    vector = [0] * size
    vector[0] = 1

    while n:
        if n & 1:
            vector = [
                sum(vector[i] * matrix[i][j] for i in range(size)) % MOD
                for j in range(size)
            ]
        matrix = multiply(matrix, matrix)
        n >>= 1

    return sum(vector) % MOD
