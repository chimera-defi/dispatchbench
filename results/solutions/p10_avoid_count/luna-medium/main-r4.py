def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    chars = set(alphabet)

    # Build a trie, ignoring duplicate words and words containing an
    # already-banned prefix.
    children = [{}]
    terminal = [False]

    for word in set(banned):
        node = 0
        dead = False
        for ch in word:
            if terminal[node]:
                dead = True
                break
            nxt = children[node].get(ch)
            if nxt is None:
                nxt = len(children)
                children[node][ch] = nxt
                children.append({})
                terminal.append(False)
            node = nxt
        if not dead:
            terminal[node] = True

    # Aho-Corasick failure links and transitions.
    size = len(children)
    fail = [0] * size
    go = [[0] * len(alphabet) for _ in range(size)]
    char_index = {ch: i for i, ch in enumerate(alphabet)}
    queue = []

    for ch, nxt in children[0].items():
        idx = char_index[ch]
        go[0][idx] = nxt
        queue.append(nxt)

    head = 0
    while head < len(queue):
        v = queue[head]
        head += 1
        terminal[v] |= terminal[fail[v]]

        for ch, idx in char_index.items():
            nxt = children[v].get(ch)
            if nxt is not None:
                go[v][idx] = nxt
                fail[nxt] = go[fail[v]][idx]
                queue.append(nxt)
            else:
                go[v][idx] = go[fail[v]][idx]

    states = [i for i in range(size) if not terminal[i]]
    if not states:
        return 0

    index = {state: i for i, state in enumerate(states)}
    m = len(states)
    matrix = [[0] * m for _ in range(m)]

    for state in states:
        src = index[state]
        for idx in range(len(alphabet)):
            nxt = go[state][idx]
            if not terminal[nxt]:
                dst = index[nxt]
                matrix[src][dst] = (matrix[src][dst] + 1) % MOD

    def multiply(a, b):
        result = [[0] * m for _ in range(m)]
        for i in range(m):
            for k, value in enumerate(a[i]):
                if value:
                    row_b = b[k]
                    for j, other in enumerate(row_b):
                        if other:
                            result[i][j] = (result[i][j] + value * other) % MOD
        return result

    def apply(matrix, vector):
        result = [0] * m
        for i, value in enumerate(vector):
            if value:
                for j, ways in enumerate(matrix[i]):
                    if ways:
                        result[j] = (result[j] + value * ways) % MOD
        return result

    vector = [0] * m
    vector[index[0]] = 1
    power = matrix
    while n:
        if n & 1:
            vector = apply(power, vector)
        n >>= 1
        if n:
            power = multiply(power, power)

    return sum(vector) % MOD
