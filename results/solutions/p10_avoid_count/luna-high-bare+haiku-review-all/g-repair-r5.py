def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    mod = 1_000_000_007

    children = [{}]
    fail = [0]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            if ch not in children[node]:
                children[node][ch] = len(children)
                children.append({})
                fail.append(0)
                terminal.append(False)
            node = children[node][ch]
        terminal[node] = True

    from collections import deque

    queue = deque()
    for ch in alphabet:
        child = children[0].get(ch)
        if child is not None:
            queue.append(child)

    while queue:
        node = queue.popleft()
        terminal[node] = terminal[node] or terminal[fail[node]]
        for ch in alphabet:
            child = children[node].get(ch)
            if child is not None:
                fallback = fail[node]
                while fallback and ch not in children[fallback]:
                    fallback = fail[fallback]
                fail[child] = children[fallback].get(ch, 0)
                queue.append(child)

    safe = [i for i in range(len(children)) if not terminal[i]]
    index = {node: i for i, node in enumerate(safe)}
    size = len(safe)

    matrix = [[0] * size for _ in range(size)]
    for node in safe:
        i = index[node]
        for ch in alphabet:
            current = node
            while current and ch not in children[current]:
                current = fail[current]
            nxt = children[current].get(ch, 0)
            if not terminal[nxt]:
                j = index[nxt]
                matrix[i][j] = (matrix[i][j] + 1) % mod

    vector = [0] * size
    vector[index[0]] = 1

    def multiply_matrices(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, value in enumerate(a[i]):
                if value:
                    row_b = b[k]
                    for j, other in enumerate(row_b):
                        if other:
                            result[i][j] = (result[i][j] + value * other) % mod
        return result

    def multiply_vector(v, m):
        result = [0] * size
        for i, value in enumerate(v):
            if value:
                for j, other in enumerate(m[i]):
                    if other:
                        result[j] = (result[j] + value * other) % mod
        return result

    while n:
        if n & 1:
            vector = multiply_vector(vector, matrix)
        n >>= 1
        if n:
            matrix = multiply_matrices(matrix, matrix)

    return sum(vector) % mod
