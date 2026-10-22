def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    mod = 1_000_000_007
    if n == 0:
        return 1

    chars = list(alphabet)
    index = {c: i for i, c in enumerate(chars)}
    k = len(chars)

    children = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for char in word:
            ci = index[char]
            if ci not in children[node]:
                children[node][ci] = len(children)
                children.append({})
                terminal.append(False)
            node = children[node][ci]
        terminal[node] = True

    size = len(children)
    go = [[0] * k for _ in range(size)]
    fail = [0] * size
    queue = []

    for ci in range(k):
        child = children[0].get(ci)
        if child is not None:
            go[0][ci] = child
            queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        terminal[node] |= terminal[fail[node]]

        for ci in range(k):
            child = children[node].get(ci)
            if child is not None:
                fail[child] = go[fail[node]][ci]
                go[node][ci] = child
                queue.append(child)
            else:
                go[node][ci] = go[fail[node]][ci]

    matrix = [[0] * size for _ in range(size)]
    for node in range(size):
        if terminal[node]:
            continue
        for ci in range(k):
            target = go[node][ci]
            if not terminal[target]:
                matrix[node][target] += 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            row = result[i]
            for mid, value in enumerate(a[i]):
                if value:
                    brow = b[mid]
                    for j, other in enumerate(brow):
                        if other:
                            row[j] += value * other
            for j in range(size):
                row[j] %= mod
        return result

    def multiply_vector(vector, matrix):
        result = [0] * size
        for i, value in enumerate(vector):
            if value:
                for j, entry in enumerate(matrix[i]):
                    if entry:
                        result[j] += value * entry
        return [x % mod for x in result]

    vector = [0] * size
    vector[0] = 1
    exponent = n

    while exponent:
        if exponent & 1:
            vector = multiply_vector(vector, matrix)
        exponent >>= 1
        if exponent:
            matrix = multiply(matrix, matrix)

    return sum(vector) % mod
