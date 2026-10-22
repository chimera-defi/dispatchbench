def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie of banned strings, marking terminal nodes as forbidden.
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

    # Aho-Corasick failure links; propagate forbidden status from suffixes.
    fail = [0] * len(children)
    queue = []
    for ch, node in children[0].items():
        queue.append(node)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        if terminal[fail[node]]:
            terminal[node] = True

        for ch, nxt in children[node].items():
            f = fail[node]
            while f and ch not in children[f]:
                f = fail[f]
            fail[nxt] = children[f].get(ch, 0)
            queue.append(nxt)

    # Keep only non-forbidden states reachable from the root.
    states = [0]
    index = {0: 0}
    transitions = []

    for node in states:
        row = []
        for ch in alphabet:
            cur = node
            while cur and ch not in children[cur]:
                cur = fail[cur]
            nxt = children[cur].get(ch, 0)
            if terminal[nxt]:
                row.append(-1)
            else:
                if nxt not in index:
                    index[nxt] = len(states)
                    states.append(nxt)
                row.append(index[nxt])
        transitions.append(row)

    size = len(states)

    # Count walks of length n using binary exponentiation of the transition matrix.
    matrix = [[0] * size for _ in range(size)]
    for src, row in enumerate(transitions):
        for dst in row:
            if dst >= 0:
                matrix[src][dst] = (matrix[src][dst] + 1) % MOD

    vector = [0] * size
    vector[0] = 1
    power = n

    while power:
        if power & 1:
            result = [0] * size
            for i, value in enumerate(vector):
                if value:
                    for j, ways in enumerate(matrix[i]):
                        if ways:
                            result[j] = (result[j] + value * ways) % MOD
            vector = result

        power >>= 1
        if power:
            squared = [[0] * size for _ in range(size)]
            for i in range(size):
                for k, left in enumerate(matrix[i]):
                    if left:
                        row_k = matrix[k]
                        for j, right in enumerate(row_k):
                            if right:
                                squared[i][j] = (
                                    squared[i][j] + left * right
                                ) % MOD
            matrix = squared

    return sum(vector) % MOD
