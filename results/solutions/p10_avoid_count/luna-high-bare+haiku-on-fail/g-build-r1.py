def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    chars = list(alphabet)
    char_index = {ch: i for i, ch in enumerate(chars)}
    k = len(chars)

    children = [{}]
    terminal = [False]

    for word in banned:
        state = 0
        for ch in word:
            ci = char_index[ch]
            if ci not in children[state]:
                children[state][ci] = len(children)
                children.append({})
                terminal.append(False)
            state = children[state][ci]
        terminal[state] = True

    go = [[0] * k for _ in children]
    fail = [0] * len(children)
    queue = []

    for ci in range(k):
        child = children[0].get(ci)
        if child is not None:
            go[0][ci] = child
            queue.append(child)

    head = 0
    while head < len(queue):
        state = queue[head]
        head += 1
        terminal[state] |= terminal[fail[state]]

        for ci in range(k):
            child = children[state].get(ci)
            if child is not None:
                fail[child] = go[fail[state]][ci]
                go[state][ci] = child
                queue.append(child)
            else:
                go[state][ci] = go[fail[state]][ci]

    safe = [s for s in range(len(children)) if not terminal[s]]
    index = {state: i for i, state in enumerate(safe)}
    size = len(safe)

    matrix = [[0] * size for _ in range(size)]
    for state in safe:
        src = index[state]
        for ci in range(k):
            dest = go[state][ci]
            if not terminal[dest]:
                dst = index[dest]
                matrix[src][dst] = (matrix[src][dst] + 1) % MOD

    vector = [0] * size
    vector[index[0]] = 1

    def multiply_matrices(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for mid, value in enumerate(a[i]):
                if value:
                    for j, other in enumerate(b[mid]):
                        if other:
                            result[i][j] = (result[i][j] + value * other) % MOD
        return result

    def multiply_vector(v, m):
        result = [0] * size
        for i, value in enumerate(v):
            if value:
                for j, other in enumerate(m[i]):
                    if other:
                        result[j] = (result[j] + value * other) % MOD
        return result

    while n:
        if n & 1:
            vector = multiply_vector(vector, matrix)
        n >>= 1
        if n:
            matrix = multiply_matrices(matrix, matrix)

    return sum(vector) % MOD
