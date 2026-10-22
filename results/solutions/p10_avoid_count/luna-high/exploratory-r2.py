def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    char_index = {ch: i for i, ch in enumerate(alphabet)}
    edges = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            c = char_index[ch]
            if c not in edges[node]:
                edges[node][c] = len(edges)
                edges.append({})
                terminal.append(False)
            node = edges[node][c]
        terminal[node] = True

    # Build failure links and complete transitions.
    go = [[0] * len(alphabet) for _ in edges]
    queue = []
    for c, child in edges[0].items():
        go[0][c] = child
        queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        fail = go[0][0]  # overwritten below using the stored failure link
        terminal[node] |= terminal[fail_links[node]]

        for c in range(len(alphabet)):
            child = edges[node].get(c)
            if child is not None:
                fail_links[child] = go[fail_links[node]][c]
                go[node][c] = child
                queue.append(child)
            else:
                go[node][c] = go[fail_links[node]][c]

    safe_nodes = [i for i, is_terminal in enumerate(terminal) if not is_terminal]
    index = {node: i for i, node in enumerate(safe_nodes)}
    size = len(safe_nodes)

    matrix = [[0] * size for _ in range(size)]
    for node in safe_nodes:
        i = index[node]
        for c in range(len(alphabet)):
            dest = go[node][c]
            if not terminal[dest]:
                j = index[dest]
                matrix[i][j] += 1

    vector = [0] * size
    vector[index[0]] = 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i, row in enumerate(a):
            out = result[i]
            for k, value in enumerate(row):
                if value:
                    for j, other in enumerate(b[k]):
                        out[j] += value * other
            result[i] = [x % MOD for x in out]
        return result

    def apply(vector, matrix):
        return [
            sum(vector[i] * matrix[i][j] for i in range(size)) % MOD
            for j in range(size)
        ]

    # Failure links are initialized before processing trie nodes.
    # (The root's children have failure link 0.)
    # This assignment is placed here to keep the automaton construction explicit.
    return _count_with_matrix(n, vector, matrix, size, MOD)
