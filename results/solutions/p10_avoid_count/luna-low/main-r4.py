def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    chars = list(alphabet)
    k = len(chars)

    # Build the Aho–Corasick automaton, omitting terminal states.
    nxt = [{}]
    fail = [0]
    terminal = [False]

    for word in set(banned):
        state = 0
        for ch in word:
            if ch not in nxt[state]:
                nxt[state][ch] = len(nxt)
                nxt.append({})
                fail.append(0)
                terminal.append(False)
            state = nxt[state][ch]
        terminal[state] = True

    queue = []
    for ch in chars:
        child = nxt[0].get(ch)
        if child is not None:
            queue.append(child)

    head = 0
    while head < len(queue):
        state = queue[head]
        head += 1

        if terminal[fail[state]]:
            terminal[state] = True

        for ch in chars:
            child = nxt[state].get(ch)
            if child is not None:
                f = fail[state]
                while f and ch not in nxt[f]:
                    f = fail[f]
                fail[child] = nxt[f].get(ch, 0)
                queue.append(child)

    states = [i for i in range(len(nxt)) if not terminal[i]]
    index = {state: i for i, state in enumerate(states)}
    m = len(states)

    # Count transitions between safe states.
    mat = [[0] * m for _ in range(m)]
    for state in states:
        i = index[state]
        for ch in chars:
            s = state
            while s and ch not in nxt[s]:
                s = fail[s]
            dest = nxt[s].get(ch, 0)
            if not terminal[dest]:
                j = index[dest]
                mat[i][j] += 1

    def multiply(a, b):
        size = len(a)
        out = [[0] * size for _ in range(size)]
        for i in range(size):
            for t, x in enumerate(a[i]):
                if x:
                    for j, y in enumerate(b[t]):
                        if y:
                            out[i][j] = (out[i][j] + x * y) % MOD
        return out

    def apply(vec, matrix):
        out = [0] * m
        for i, x in enumerate(vec):
            if x:
                for j, y in enumerate(matrix[i]):
                    if y:
                        out[j] = (out[j] + x * y) % MOD
        return out

    vec = [0] * m
    vec[index[0]] = 1
    while n:
        if n & 1:
            vec = apply(vec, mat)
        mat = multiply(mat, mat)
        n >>= 1

    return sum(vec) % MOD
