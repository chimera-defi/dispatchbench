def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie, removing duplicates and strings containing a shorter
    # banned string (the automaton would reject them in any case).
    unique = sorted(set(banned), key=len)
    minimal = []
    for word in unique:
        if not any(shorter in word for shorter in minimal):
            minimal.append(word)

    children = [{}]
    terminal = [False]
    for word in minimal:
        node = 0
        for ch in word:
            if ch not in children[node]:
                children[node][ch] = len(children)
                children.append({})
                terminal.append(False)
            node = children[node][ch]
        terminal[node] = True

    # Aho–Corasick failure links and transitions.
    from collections import deque

    fail = [0] * len(children)
    queue = deque()
    for ch in alphabet:
        nxt = children[0].get(ch)
        if nxt is not None:
            queue.append(nxt)

    while queue:
        v = queue.popleft()
        if terminal[fail[v]]:
            terminal[v] = True
        for ch in alphabet:
            nxt = children[v].get(ch)
            if nxt is not None:
                fail[nxt] = children[fail[v]].get(ch, 0)
                queue.append(nxt)

    safe_nodes = [i for i in range(len(children)) if not terminal[i]]
    index = {node: i for i, node in enumerate(safe_nodes)}
    size = len(safe_nodes)
    if size == 0:
        return 0

    matrix = [[0] * size for _ in range(size)]
    for node in safe_nodes:
        row = index[node]
        for ch in alphabet:
            nxt = node
            while nxt and ch not in children[nxt]:
                nxt = fail[nxt]
            nxt = children[nxt].get(ch, 0)
            if not terminal[nxt]:
                matrix[row][index[nxt]] += 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, val in enumerate(a[i]):
                if val:
                    for j, other in enumerate(b[k]):
                        if other:
                            result[i][j] = (result[i][j] + val * other) % MOD
        return result

    def apply(vector, mat):
        result = [0] * size
        for i, val in enumerate(vector):
            if val:
                for j, other in enumerate(mat[i]):
                    if other:
                        result[j] = (result[j] + val * other) % MOD
        return result

    vector = [0] * size
    vector[index[0]] = 1
    while n:
        if n & 1:
            vector = apply(vector, matrix)
        matrix = multiply(matrix, matrix)
        n >>= 1

    return sum(vector) % MOD
