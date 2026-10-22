def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    # Build an Aho-Corasick automaton, omitting terminal states.
    children = [{}]
    fail = [0]
    terminal = [False]

    for word in set(banned):
        node = 0
        for ch in word:
            nxt = children[node].get(ch)
            if nxt is None:
                nxt = len(children)
                children[node][ch] = nxt
                children.append({})
                fail.append(0)
                terminal.append(False)
            node = nxt
        terminal[node] = True

    from collections import deque

    queue = deque()
    for ch in alphabet:
        nxt = children[0].get(ch)
        if nxt is not None:
            fail[nxt] = 0
            queue.append(nxt)

    while queue:
        node = queue.popleft()
        if terminal[fail[node]]:
            terminal[node] = True
        for ch in alphabet:
            nxt = children[node].get(ch)
            if nxt is not None:
                f = fail[node]
                while f and ch not in children[f]:
                    f = fail[f]
                fail[nxt] = children[f].get(ch, 0)
                queue.append(nxt)

    states = [i for i in range(len(children)) if not terminal[i]]
    index = {node: i for i, node in enumerate(states)}
    size = len(states)

    if size == 0:
        return 0

    # Transition matrix: rows are source states, columns are destination states.
    matrix = [[0] * size for _ in range(size)]
    for node in states:
        row = index[node]
        for ch in alphabet:
            cur = node
            while cur and ch not in children[cur]:
                cur = fail[cur]
            nxt = children[cur].get(ch, 0)
            if not terminal[nxt]:
                matrix[row][index[nxt]] += 1
        matrix[row] = [x % MOD for x in matrix[row]]

    def multiply(a, b):
        out = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, aik in enumerate(a[i]):
                if aik:
                    bk = b[k]
                    for j, bkj in enumerate(bk):
                        if bkj:
                            out[i][j] = (out[i][j] + aik * bkj) % MOD
        return out

    # Raise the transition matrix to n and sum paths from the root.
    result = [[int(i == j) for j in range(size)] for i in range(size)]
    power = matrix
    exp = n
    while exp:
        if exp & 1:
            result = multiply(result, power)
        power = multiply(power, power)
        exp >>= 1

    root = index[0]
    return sum(result[root]) % MOD
