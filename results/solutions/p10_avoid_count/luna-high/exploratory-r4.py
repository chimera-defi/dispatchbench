def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    k = len(alphabet)
    char_index = {ch: i for i, ch in enumerate(alphabet)}

    trie = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            c = char_index[ch]
            if c not in trie[node]:
                trie[node][c] = len(trie)
                trie.append({})
                terminal.append(False)
            node = trie[node][c]
        terminal[node] = True

    size = len(trie)
    fail = [0] * size
    go = [[0] * k for _ in range(size)]
    queue = []

    for c in range(k):
        child = trie[0].get(c)
        if child is not None:
            queue.append(child)
            go[0][c] = child

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        terminal[node] |= terminal[fail[node]]

        for c in range(k):
            child = trie[node].get(c)
            if child is not None:
                fail[child] = go[fail[node]][c]
                queue.append(child)
                go[node][c] = child
            else:
                go[node][c] = go[fail[node]][c]

    safe = [i for i in range(size) if not terminal[i]]
    index = {node: i for i, node in enumerate(safe)}
    m = len(safe)

    matrix = [[0] * m for _ in range(m)]
    for node in safe:
        i = index[node]
        for c in range(k):
            nxt = go[node][c]
            if not terminal[nxt]:
                j = index[nxt]
                matrix[i][j] = (matrix[i][j] + 1) % MOD

    vector = [0] * m
    vector[index[0]] = 1

    while n:
        if n & 1:
            result = [0] * m
            for i, value in enumerate(vector):
                if value:
                    for j, ways in enumerate(matrix[i]):
                        result[j] = (result[j] + value * ways) % MOD
            vector = result

        n >>= 1
        if n:
            squared = [[0] * m for _ in range(m)]
            for i in range(m):
                for t, a in enumerate(matrix[i]):
                    if a:
                        for j, b in enumerate(matrix[t]):
                            if b:
                                squared[i][j] = (squared[i][j] + a * b) % MOD
            matrix = squared

    return sum(vector) % MOD
