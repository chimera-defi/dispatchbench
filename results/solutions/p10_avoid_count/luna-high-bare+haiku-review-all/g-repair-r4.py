def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    mod = 1_000_000_007

    children = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            nxt = children[node].get(ch)
            if nxt is None:
                nxt = len(children)
                children[node][ch] = nxt
                children.append({})
                terminal.append(False)
            node = nxt
        terminal[node] = True

    fail = [0] * len(children)
    queue = []
    for nxt in children[0].values():
        queue.append(nxt)

    for node in queue:
        terminal[node] |= terminal[fail[node]]

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        for ch, nxt in children[node].items():
            f = fail[node]
            while f and ch not in children[f]:
                f = fail[f]
            fail[nxt] = children[f].get(ch, 0)
            terminal[nxt] |= terminal[fail[nxt]]
            queue.append(nxt)

    safe_nodes = [i for i, is_terminal in enumerate(terminal) if not is_terminal]
    index = {node: i for i, node in enumerate(safe_nodes)}
    size = len(safe_nodes)

    matrix = [[0] * size for _ in range(size)]
    for node in safe_nodes:
        src = index[node]
        for ch in alphabet:
            cur = node
            while cur and ch not in children[cur]:
                cur = fail[cur]
            nxt = children[cur].get(ch, 0)
            if not terminal[nxt]:
                dst = index[nxt]
                matrix[src][dst] += 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, val in enumerate(a[i]):
                if val:
                    row = b[k]
                    for j, other in enumerate(row):
                        if other:
                            result[i][j] = (result[i][j] + val * other) % mod
        return result

    vector = [0] * size
    vector[index[0]] = 1

    while n:
        if n & 1:
            new_vector = [0] * size
            for i, val in enumerate(vector):
                if val:
                    for j, ways in enumerate(matrix[i]):
                        if ways:
                            new_vector[j] = (new_vector[j] + val * ways) % mod
            vector = new_vector
        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(vector) % mod
