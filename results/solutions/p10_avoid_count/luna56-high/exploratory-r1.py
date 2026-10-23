def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    children = [{}]
    terminal = [False]

    for word in banned:
        state = 0
        for ch in word:
            if ch not in children[state]:
                children[state][ch] = len(children)
                children.append({})
                terminal.append(False)
            state = children[state][ch]
        terminal[state] = True

    size = len(children)
    fail = [0] * size
    bad = terminal[:]
    go = [dict(d) for d in children]

    for ch in alphabet:
        go[0][ch] = children[0].get(ch, 0)

    queue = []
    for child in children[0].values():
        queue.append(child)

    head = 0
    while head < len(queue):
        state = queue[head]
        head += 1

        for ch, child in children[state].items():
            fail[child] = go[fail[state]].get(ch, 0)
            bad[child] = bad[child] or bad[fail[child]]
            queue.append(child)

        for ch in alphabet:
            if ch not in go[state]:
                go[state][ch] = go[fail[state]].get(ch, 0)

    matrix = [[0] * size for _ in range(size)]
    for state in range(size):
        if bad[state]:
            continue
        for ch in alphabet:
            nxt = go[state][ch]
            if not bad[nxt]:
                matrix[state][nxt] = (matrix[state][nxt] + 1) % MOD

    def mat_mul(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k in range(size):
                if a[i][k]:
                    aik = a[i][k]
                    for j in range(size):
                        result[i][j] = (result[i][j] + aik * b[k][j]) % MOD
        return result

    def vec_mul(vec, mat):
        result = [0] * size
        for i, value in enumerate(vec):
            if value:
                for j in range(size):
                    result[j] = (result[j] + value * mat[i][j]) % MOD
        return result

    vector = [0] * size
    vector[0] = 1

    while n:
        if n & 1:
            vector = vec_mul(vector, matrix)
        matrix = mat_mul(matrix, matrix)
        n >>= 1

    return sum(vector) % MOD
