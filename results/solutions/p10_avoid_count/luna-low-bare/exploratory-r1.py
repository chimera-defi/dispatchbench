def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie, removing duplicate and redundant banned strings as
    # terminal trie nodes naturally cover all their descendants.
    children = [{}]
    terminal = [False]

    for word in set(banned):
        node = 0
        already_covered = False
        for ch in word:
            if terminal[node]:
                already_covered = True
                break
            if ch not in children[node]:
                children[node][ch] = len(children)
                children.append({})
                terminal.append(False)
            node = children[node][ch]
        if not already_covered:
            terminal[node] = True

    # Aho-Corasick failure links; propagate terminal status through them.
    fail = [0] * len(children)
    queue = []
    for nxt in children[0].values():
        queue.append(nxt)

    for node in queue:
        for ch, nxt in children[node].items():
            f = fail[node]
            while f and ch not in children[f]:
                f = fail[f]
            fail[nxt] = children[f].get(ch, 0)
            terminal[nxt] = terminal[nxt] or terminal[fail[nxt]]
            queue.append(nxt)

    if terminal[0]:
        return 0

    # Keep only non-terminal automaton states and count transitions between them.
    states = [i for i in range(len(children)) if not terminal[i]]
    index = {node: i for i, node in enumerate(states)}
    size = len(states)
    matrix = [[0] * size for _ in range(size)]

    for node in states:
        src = index[node]
        for ch in alphabet:
            cur = node
            while cur and ch not in children[cur]:
                cur = fail[cur]
            nxt = children[cur].get(ch, 0)
            if not terminal[nxt]:
                dst = index[nxt]
                matrix[src][dst] = (matrix[src][dst] + 1) % MOD

    def multiply(a, b):
        m = len(a)
        out = [[0] * m for _ in range(m)]
        for i in range(m):
            for k, av in enumerate(a[i]):
                if av:
                    for j, bv in enumerate(b[k]):
                        if bv:
                            out[i][j] = (out[i][j] + av * bv) % MOD
        return out

    def apply(vector, matrix):
        m = len(vector)
        out = [0] * m
        for i, value in enumerate(vector):
            if value:
                for j, ways in enumerate(matrix[i]):
                    if ways:
                        out[j] = (out[j] + value * ways) % MOD
        return out

    vector = [0] * size
    vector[index[0]] = 1
    power = matrix
    exponent = n
    while exponent:
        if exponent & 1:
            vector = apply(vector, power)
        exponent >>= 1
        if exponent:
            power = multiply(power, power)

    return sum(vector) % MOD
