def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Trie nodes store transitions by character.
    trie = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            if ch not in trie[node]:
                trie[node][ch] = len(trie)
                trie.append({})
                terminal.append(False)
            node = trie[node][ch]
        terminal[node] = True

    # Build failure links and complete transitions in BFS order.
    from collections import deque

    fail = [0] * len(trie)
    queue = deque()

    for ch in alphabet:
        child = trie[0].get(ch)
        if child is not None:
            queue.append(child)

    order = [0]
    while queue:
        node = queue.popleft()
        order.append(node)

        terminal[node] = terminal[node] or terminal[fail[node]]

        for ch in alphabet:
            child = trie[node].get(ch)
            if child is not None:
                fail[child] = trie[fail[node]].get(ch, 0)
                queue.append(child)

    # Complete transitions for every node.
    go = [{} for _ in trie]
    for ch in alphabet:
        go[0][ch] = trie[0].get(ch, 0)

    for node in order[1:]:
        for ch in alphabet:
            go[node][ch] = trie[node].get(ch, go[fail[node]][ch])

    states = [node for node in range(len(trie)) if not terminal[node]]
    index = {node: i for i, node in enumerate(states)}
    size = len(states)

    matrix = [[0] * size for _ in range(size)]
    for node in states:
        u = index[node]
        for ch in alphabet:
            dest = go[node][ch]
            if not terminal[dest]:
                matrix[u][index[dest]] += 1

    def multiply(a, b):
        c = [[0] * size for _ in range(size)]
        for i in range(size):
            for k in range(size):
                if a[i][k]:
                    aik = a[i][k]
                    for j in range(size):
                        if b[k][j]:
                            c[i][j] = (c[i][j] + aik * b[k][j]) % MOD
        return c

    # Row vector initially concentrated at the root.
    vector = [0] * size
    vector[index[0]] = 1

    power = matrix
    while n:
        if n & 1:
            result = [0] * size
            for i, value in enumerate(vector):
                if value:
                    for j in range(size):
                        result[j] = (result[j] + value * power[i][j]) % MOD
            vector = result
        power = multiply(power, power)
        n >>= 1

    return sum(vector) % MOD
