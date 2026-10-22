def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    k = len(alphabet)
    char_id = {ch: i for i, ch in enumerate(alphabet)}

    # Trie nodes hold one transition per alphabet character.
    nxt = [[-1] * k]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            c = char_id[ch]
            if nxt[node][c] == -1:
                nxt[node][c] = len(nxt)
                nxt.append([-1] * k)
                terminal.append(False)
            node = nxt[node][c]
        terminal[node] = True

    # Complete transitions and compute Aho–Corasick failure links.
    fail = [0] * len(nxt)
    queue = []
    for c in range(k):
        child = nxt[0][c]
        if child == -1:
            nxt[0][c] = 0
        else:
            queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        terminal[node] |= terminal[fail[node]]

        for c in range(k):
            child = nxt[node][c]
            if child == -1:
                nxt[node][c] = nxt[fail[node]][c]
            else:
                fail[child] = nxt[fail[node]][c]
                queue.append(child)

    safe = [i for i, bad in enumerate(terminal) if not bad]
    index = {node: i for i, node in enumerate(safe)}
    size = len(safe)

    # Matrix counts transitions between safe states.
    matrix = [[0] * size for _ in range(size)]
    for node in safe:
        i = index[node]
        for c in range(k):
            dest = nxt[node][c]
            if not terminal[dest]:
                j = index[dest]
                matrix[i][j] += 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for t, value in enumerate(a[i]):
                if value:
                    for j, other in enumerate(b[t]):
                        if other:
                            result[i][j] = (result[i][j] + value * other) % MOD
        return result

    def vector_multiply(vector, mat):
        result = [0] * size
        for i, value in enumerate(vector):
            if value:
                for j, other in enumerate(mat[i]):
                    if other:
                        result[j] = (result[j] + value * other) % MOD
        return result

    vector = [0] * size
    vector[index[0]] = 1

    while n:
        if n & 1:
            vector = vector_multiply(vector, matrix)
        matrix = multiply(matrix, matrix)
        n >>= 1

    return sum(vector) % MOD
