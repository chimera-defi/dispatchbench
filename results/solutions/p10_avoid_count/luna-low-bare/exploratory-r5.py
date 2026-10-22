def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie and mark terminal states. Duplicate patterns are harmless.
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

    # Aho-Corasick failure links and completed transitions.
    from collections import deque

    sigma = len(alphabet)
    char_index = {ch: i for i, ch in enumerate(alphabet)}
    transitions = [[0] * sigma for _ in children]
    fail = [0] * len(children)
    queue = deque()

    for i, ch in enumerate(alphabet):
        nxt = children[0].get(ch)
        if nxt is not None:
            transitions[0][i] = nxt
            queue.append(nxt)

    order = [0]
    while queue:
        node = queue.popleft()
        order.append(node)
        for i, ch in enumerate(alphabet):
            nxt = children[node].get(ch)
            if nxt is not None:
                fail[nxt] = transitions[fail[node]][i]
                terminal[nxt] |= terminal[fail[nxt]]
                transitions[node][i] = nxt
                queue.append(nxt)
            else:
                transitions[node][i] = transitions[fail[node]][i]

    safe = [node for node in range(len(children)) if not terminal[node]]
    if not safe:
        return 0

    # Matrix exponentiation over safe automaton states.
    size = len(safe)
    index = {node: i for i, node in enumerate(safe)}
    matrix = [[0] * size for _ in range(size)]
    for node in safe:
        src = index[node]
        for i in range(sigma):
            nxt = transitions[node][i]
            if not terminal[nxt]:
                dst = index[nxt]
                matrix[src][dst] += 1
        matrix[src] = [x % MOD for x in matrix[src]]

    vector = [0] * size
    vector[index[0]] = 1

    def multiply_vector(vec, mat):
        result = [0] * size
        for i, value in enumerate(vec):
            if value:
                row = mat[i]
                for j, coeff in enumerate(row):
                    if coeff:
                        result[j] = (result[j] + value * coeff) % MOD
        return result

    def multiply_matrices(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, x in enumerate(a[i]):
                if x:
                    for j, y in enumerate(b[k]):
                        if y:
                            result[i][j] = (result[i][j] + x * y) % MOD
        return result

    power = n
    while power:
        if power & 1:
            vector = multiply_vector(vector, matrix)
        power >>= 1
        if power:
            matrix = multiply_matrices(matrix, matrix)

    return sum(vector) % MOD
