def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build a trie, omitting words that already contain a shorter banned word.
    children = [{}]
    terminal = [False]
    for word in sorted(set(banned), key=len):
        node = 0
        invalid = False
        for ch in word:
            if terminal[node]:
                invalid = True
                break
            if ch not in children[node]:
                children[node][ch] = len(children)
                children.append({})
                terminal.append(False)
            node = children[node][ch]
        if not invalid:
            terminal[node] = True

    # Build the Aho-Corasick automaton.
    from collections import deque

    failure = [0] * len(children)
    queue = deque()
    for node in children[0].values():
        queue.append(node)

    while queue:
        node = queue.popleft()
        if terminal[failure[node]]:
            terminal[node] = True
        for ch, nxt in children[node].items():
            f = failure[node]
            while f and ch not in children[f]:
                f = failure[f]
            failure[nxt] = children[f].get(ch, 0)
            queue.append(nxt)

    # Keep only non-terminal states and form the transition-count matrix.
    states = [i for i in range(len(children)) if not terminal[i]]
    index = {node: i for i, node in enumerate(states)}
    size = len(states)
    matrix = [[0] * size for _ in range(size)]

    for node in states:
        src = index[node]
        for ch in alphabet:
            cur = node
            while cur and ch not in children[cur]:
                cur = failure[cur]
            nxt = children[cur].get(ch, 0)
            if not terminal[nxt]:
                dst = index[nxt]
                matrix[src][dst] = (matrix[src][dst] + 1) % MOD

    def multiply(a, b):
        out = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, x in enumerate(a[i]):
                if x:
                    row = b[k]
                    for j, y in enumerate(row):
                        if y:
                            out[i][j] = (out[i][j] + x * y) % MOD
        return out

    def vector_multiply(v, a):
        out = [0] * size
        for i, x in enumerate(v):
            if x:
                for j, y in enumerate(a[i]):
                    if y:
                        out[j] = (out[j] + x * y) % MOD
        return out

    result = [0] * size
    result[index[0]] = 1
    while n:
        if n & 1:
            result = vector_multiply(result, matrix)
        matrix = multiply(matrix, matrix)
        n >>= 1

    return sum(result) % MOD
