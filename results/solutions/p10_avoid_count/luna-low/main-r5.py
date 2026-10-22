def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie, marking terminal nodes as forbidden.
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

    # Aho-Corasick failure links.
    fail = [0] * len(children)
    queue = []
    for ch, node in children[0].items():
        queue.append(node)

    for node in queue:
        pass

    head = 0
    while head < len(queue):
        v = queue[head]
        head += 1
        if terminal[fail[v]]:
            terminal[v] = True

        for ch, u in children[v].items():
            f = fail[v]
            while f and ch not in children[f]:
                f = fail[f]
            fail[u] = children[f].get(ch, 0)
            queue.append(u)

    # Keep only non-forbidden states reachable from the root.
    states = [0]
    index = {0: 0}
    transitions = []
    head = 0
    while head < len(states):
        v = states[head]
        head += 1
        row = []
        for ch in alphabet:
            u = v
            while u and ch not in children[u]:
                u = fail[u]
            u = children[u].get(ch, 0)
            if terminal[u]:
                row.append(-1)
            else:
                if u not in index:
                    index[u] = len(states)
                    states.append(u)
                row.append(index[u])
        transitions.append(row)

    size = len(states)
    if size == 1 and all(t == -1 for t in transitions[0]):
        return 1 if n == 0 else 0

    # Count walks of length n in the safe-state automaton via matrix exponentiation.
    matrix = [[0] * size for _ in range(size)]
    for i, row in enumerate(transitions):
        for j in row:
            if j >= 0:
                matrix[i][j] = (matrix[i][j] + 1) % MOD

    def multiply(a, b):
        out = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, x in enumerate(a[i]):
                if x:
                    for j, y in enumerate(b[k]):
                        if y:
                            out[i][j] = (out[i][j] + x * y) % MOD
        return out

    vector = [0] * size
    vector[0] = 1
    power = matrix
    while n:
        if n & 1:
            nxt = [0] * size
            for i, x in enumerate(vector):
                if x:
                    for j, y in enumerate(power[i]):
                        if y:
                            nxt[j] = (nxt[j] + x * y) % MOD
            vector = nxt
        power = multiply(power, power)
        n >>= 1

    return sum(vector) % MOD
