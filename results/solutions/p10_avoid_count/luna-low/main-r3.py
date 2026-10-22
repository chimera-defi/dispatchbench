def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    if n == 0:
        return 1

    # Build a trie, stopping at terminal nodes. A terminal prefix makes all
    # longer banned strings containing it redundant.
    children = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            if terminal[node]:
                break
            if ch not in children[node]:
                children[node][ch] = len(children)
                children.append({})
                terminal.append(False)
            node = children[node][ch]
        else:
            terminal[node] = True

    # Aho-Corasick failure links and transitions.
    from collections import deque

    fail = [0] * len(children)
    queue = deque()
    for ch, nxt in children[0].items():
        queue.append(nxt)

    while queue:
        v = queue.popleft()
        if terminal[fail[v]]:
            terminal[v] = True
        for ch, nxt in children[v].items():
            f = fail[v]
            while f and ch not in children[f]:
                f = fail[f]
            fail[nxt] = children[f].get(ch, 0)
            queue.append(nxt)

    chars = list(alphabet)
    states = [i for i in range(len(children)) if not terminal[i]]
    index = {state: i for i, state in enumerate(states)}
    size = len(states)

    transitions = [[0] * len(chars) for _ in range(size)]
    for i, state in enumerate(states):
        for j, ch in enumerate(chars):
            v = state
            while v and ch not in children[v]:
                v = fail[v]
            nxt = children[v].get(ch, 0)
            if not terminal[nxt]:
                transitions[i][j] = index[nxt]
            else:
                transitions[i][j] = -1

    # Binary exponentiation of the transition-count matrix.
    matrix = [[0] * size for _ in range(size)]
    for i in range(size):
        for nxt in transitions[i]:
            if nxt >= 0:
                matrix[i][nxt] = (matrix[i][nxt] + 1) % MOD

    def multiply(a, b):
        out = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, av in enumerate(a[i]):
                if av:
                    for j, bv in enumerate(b[k]):
                        if bv:
                            out[i][j] = (out[i][j] + av * bv) % MOD
        return out

    result = [[int(i == j) for j in range(size)] for i in range(size)]
    power = matrix
    exponent = n
    while exponent:
        if exponent & 1:
            result = multiply(result, power)
        exponent >>= 1
        if exponent:
            power = multiply(power, power)

    return sum(result[0]) % MOD
