def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    children = [{}]
    fail = [0]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            if ch not in children[node]:
                children[node][ch] = len(children)
                children.append({})
                fail.append(0)
                terminal.append(False)
            node = children[node][ch]
        terminal[node] = True

    from collections import deque

    queue = deque()
    for ch in alphabet:
        nxt = children[0].get(ch)
        if nxt is not None:
            queue.append(nxt)

    while queue:
        node = queue.popleft()
        terminal[node] = terminal[node] or terminal[fail[node]]
        for ch in alphabet:
            nxt = children[node].get(ch)
            if nxt is None:
                continue
            f = fail[node]
            while f and ch not in children[f]:
                f = fail[f]
            fail[nxt] = children[f].get(ch, 0)
            queue.append(nxt)

    safe_nodes = [i for i in range(len(children)) if not terminal[i]]
    index = {node: i for i, node in enumerate(safe_nodes)}
    size = len(safe_nodes)

    transitions = [[0] * size for _ in range(size)]
    for node in safe_nodes:
        src = index[node]
        for ch in alphabet:
            cur = node
            while cur and ch not in children[cur]:
                cur = fail[cur]
            nxt = children[cur].get(ch, 0)
            if not terminal[nxt]:
                transitions[src][index[nxt]] += 1

    def multiply(a, b):
        m = len(a)
        out = [[0] * m for _ in range(m)]
        for i in range(m):
            for k, x in enumerate(a[i]):
                if x:
                    for j, y in enumerate(b[k]):
                        if y:
                            out[i][j] = (out[i][j] + x * y) % MOD
        return out

    def apply(vector, matrix):
        m = len(vector)
        out = [0] * m
        for i, x in enumerate(vector):
            if x:
                for j, y in enumerate(matrix[i]):
                    if y:
                        out[j] = (out[j] + x * y) % MOD
        return out

    vector = [0] * size
    vector[index[0]] = 1
    power = transitions
    while n:
        if n & 1:
            vector = apply(vector, power)
        power = multiply(power, power)
        n >>= 1

    return sum(vector) % MOD
