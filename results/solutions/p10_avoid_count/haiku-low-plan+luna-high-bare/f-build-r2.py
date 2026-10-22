def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    char_index = {ch: i for i, ch in enumerate(alphabet)}
    sigma = len(alphabet)

    trie = [[-1] * sigma]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            c = char_index[ch]
            if trie[node][c] == -1:
                trie[node][c] = len(trie)
                trie.append([-1] * sigma)
                terminal.append(False)
            node = trie[node][c]
        terminal[node] = True

    fail = [0] * len(trie)
    dangerous = terminal[:]
    queue = []

    for c in range(sigma):
        child = trie[0][c]
        if child == -1:
            trie[0][c] = 0
        else:
            queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        dangerous[node] = dangerous[node] or dangerous[fail[node]]

        for c in range(sigma):
            child = trie[node][c]
            if child == -1:
                trie[node][c] = trie[fail[node]][c]
            else:
                fail[child] = trie[fail[node]][c]
                queue.append(child)

    safe_nodes = [i for i in range(len(trie)) if not dangerous[i]]
    if not safe_nodes:
        return 0

    safe_index = {node: i for i, node in enumerate(safe_nodes)}
    k = len(safe_nodes)
    matrix = [[0] * k for _ in range(k)]

    for node in safe_nodes:
        i = safe_index[node]
        for c in range(sigma):
            target = trie[node][c]
            if not dangerous[target]:
                j = safe_index[target]
                matrix[i][j] += 1

    vector = [0] * k
    vector[safe_index[0]] = 1

    def multiply(a, b):
        size = len(a)
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            row = result[i]
            for t, value in enumerate(a[i]):
                if value:
                    other = b[t]
                    for j, item in enumerate(other):
                        if item:
                            row[j] = (row[j] + value * item) % MOD
        return result

    def vector_multiply(v, m):
        result = [0] * len(v)
        for i, value in enumerate(v):
            if value:
                for j, item in enumerate(m[i]):
                    if item:
                        result[j] = (result[j] + value * item) % MOD
        return result

    while n:
        if n & 1:
            vector = vector_multiply(vector, matrix)
        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(vector) % MOD
