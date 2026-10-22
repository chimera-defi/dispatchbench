def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    if n == 0:
        return 1

    k = len(alphabet)
    char_index = {ch: i for i, ch in enumerate(alphabet)}

    children = [[-1] * k]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            c = char_index[ch]
            nxt = children[node][c]
            if nxt == -1:
                nxt = len(children)
                children[node][c] = nxt
                children.append([-1] * k)
                terminal.append(False)
            node = nxt
        terminal[node] = True

    fail = [0] * len(children)
    go = [[0] * k for _ in children]
    queue = []

    for c in range(k):
        child = children[0][c]
        if child != -1:
            go[0][c] = child
            queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        terminal[node] |= terminal[fail[node]]

        for c in range(k):
            child = children[node][c]
            if child != -1:
                fail[child] = go[fail[node]][c]
                go[node][c] = child
                queue.append(child)
            else:
                go[node][c] = go[fail[node]][c]

    valid = [i for i, is_terminal in enumerate(terminal) if not is_terminal]
    index = {state: i for i, state in enumerate(valid)}
    size = len(valid)

    matrix = [[0] * size for _ in range(size)]
    for state in valid:
        i = index[state]
        for c in range(k):
            nxt = go[state][c]
            if not terminal[nxt]:
                matrix[i][index[nxt]] += 1

    vector = [0] * size
    vector[index[0]] = 1

    def multiply_matrices(a, b):
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
                row[j] %= MOD
        return result

    while n:
        if n & 1:
            updated = [0] * size
            for i, value in enumerate(vector):
                if value:
                    for j, ways in enumerate(matrix[i]):
                        updated[j] = (updated[j] + value * ways) % MOD
            vector = updated
        n >>= 1
        if n:
            matrix = multiply_matrices(matrix, matrix)

    return sum(vector) % MOD
