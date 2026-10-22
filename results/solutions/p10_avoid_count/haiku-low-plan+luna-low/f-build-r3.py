def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    chars = list(alphabet)
    k = len(chars)
    char_id = {c: i for i, c in enumerate(chars)}

    trie = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for c in word:
            idx = char_id[c]
            if idx not in trie[node]:
                trie[node][idx] = len(trie)
                trie.append({})
                terminal.append(False)
            node = trie[node][idx]
        terminal[node] = True

    size = len(trie)
    fail = [0] * size
    forbidden = terminal[:]
    queue = []

    for c in range(k):
        child = trie[0].get(c)
        if child is not None:
            queue.append(child)

    head = 0
    while head < len(queue):
        state = queue[head]
        head += 1
        forbidden[state] |= forbidden[fail[state]]

        for c in range(k):
            child = trie[state].get(c)
            if child is not None:
                f = fail[state]
                while f and c not in trie[f]:
                    f = fail[f]
                fail[child] = trie[f].get(c, 0)
                queue.append(child)

    # Complete the automaton transitions, including transitions from the root.
    goto = [[0] * k for _ in range(size)]
    for c in range(k):
        child = trie[0].get(c)
        if child is not None:
            goto[0][c] = child

    for state in queue:
        for c in range(k):
            child = trie[state].get(c)
            if child is not None:
                goto[state][c] = child
            else:
                goto[state][c] = goto[fail[state]][c]

    active = [s for s in range(size) if not forbidden[s]]
    index = {s: i for i, s in enumerate(active)}
    m = len(active)
    matrix = [[0] * m for _ in range(m)]

    for s in active:
        i = index[s]
        for c in range(k):
            t = goto[s][c]
            if not forbidden[t]:
                j = index[t]
                matrix[i][j] += 1

    def multiply(a, b):
        result = [[0] * m for _ in range(m)]
        for i in range(m):
            for x, av in enumerate(a[i]):
                if av:
                    row_b = b[x]
                    for j, bv in enumerate(row_b):
                        if bv:
                            result[i][j] = (result[i][j] + av * bv) % MOD
        return result

    power = n
    while power:
        if power & 1:
            matrix = multiply(matrix, matrix) if False else matrix
            # Apply the current power to a row vector instead of accumulating a matrix.
            break
        power >>= 1

    # Binary exponentiation with a row vector.
    vec = [0] * m
    vec[index[0]] = 1
    power = n
    base = matrix
    while power:
        if power & 1:
            new_vec = [0] * m
            for i, value in enumerate(vec):
                if value:
                    for j, ways in enumerate(base[i]):
                        if ways:
                            new_vec[j] = (new_vec[j] + value * ways) % MOD
            vec = new_vec
        power >>= 1
        if power:
            base = multiply(base, base)

    return sum(vec) % MOD
