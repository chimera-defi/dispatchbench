def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    mod = 1_000_000_007
    char_index = {ch: i for i, ch in enumerate(alphabet)}
    m = len(alphabet)

    children = [{}]
    bad = [False]

    for word in banned:
        state = 0
        for ch in word:
            c = char_index[ch]
            if c not in children[state]:
                children[state][c] = len(children)
                children.append({})
                bad.append(False)
            state = children[state][c]
        bad[state] = True

    fail = [0] * len(children)
    go = [[0] * m for _ in children]
    queue = []

    for c in range(m):
        child = children[0].get(c)
        if child is not None:
            queue.append(child)
            go[0][c] = child

    head = 0
    while head < len(queue):
        state = queue[head]
        head += 1
        bad[state] |= bad[fail[state]]

        for c in range(m):
            child = children[state].get(c)
            if child is not None:
                fail[child] = go[fail[state]][c]
                queue.append(child)
                go[state][c] = child
            else:
                go[state][c] = go[fail[state]][c]

    safe_states = [s for s in range(len(children)) if not bad[s]]
    remap = {s: i for i, s in enumerate(safe_states)}
    size = len(safe_states)

    matrix = [[0] * size for _ in range(size)]
    for s in safe_states:
        i = remap[s]
        for c in range(m):
            t = go[s][c]
            if not bad[t]:
                j = remap[t]
                matrix[i][j] += 1

    vector = [0] * size
    vector[remap[0]] = 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k in range(size):
                if a[i][k]:
                    value = a[i][k]
                    for j in range(size):
                        result[i][j] += value * b[k][j]
            for j in range(size):
                result[i][j] %= mod
        return result

    while n:
        if n & 1:
            vector = [
                sum(vector[i] * matrix[i][j] for i in range(size)) % mod
                for j in range(size)
            ]
        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(vector) % mod
