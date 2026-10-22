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

    # Aho-Corasick failure links and forbidden-state propagation.
    from collections import deque

    fail = [0] * len(children)
    q = deque()
    for nxt in children[0].values():
        q.append(nxt)

    while q:
        node = q.popleft()
        if terminal[fail[node]]:
            terminal[node] = True
        for ch, nxt in children[node].items():
            f = fail[node]
            while f and ch not in children[f]:
                f = fail[f]
            fail[nxt] = children[f].get(ch, 0)
            q.append(nxt)

    # Keep only non-forbidden trie states, with transitions completed via
    # failure links. The root is safe since banned words are non-empty.
    states = [i for i in range(len(children)) if not terminal[i]]
    index = {node: i for i, node in enumerate(states)}
    m = len(states)
    matrix = [[0] * m for _ in range(m)]

    for node in states:
        src = index[node]
        for ch in alphabet:
            cur = node
            while cur and ch not in children[cur]:
                cur = fail[cur]
            nxt = children[cur].get(ch, 0)
            if not terminal[nxt]:
                matrix[src][index[nxt]] += 1

    def multiply(a, b):
        size = len(a)
        out = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, val in enumerate(a[i]):
                if val:
                    row = b[k]
                    for j, other in enumerate(row):
                        if other:
                            out[i][j] = (out[i][j] + val * other) % MOD
        return out

    def vector_multiply(v, a):
        out = [0] * len(v)
        for i, val in enumerate(v):
            if val:
                for j, other in enumerate(a[i]):
                    if other:
                        out[j] = (out[j] + val * other) % MOD
        return out

    vec = [0] * m
    vec[index[0]] = 1
    power = matrix
    while n:
        if n & 1:
            vec = vector_multiply(vec, power)
        n >>= 1
        if n:
            power = multiply(power, power)

    return sum(vec) % MOD
