def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    chars = {c: i for i, c in enumerate(alphabet)}
    k = len(alphabet)

    children = [{}]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            if ch not in children[node]:
                children[node][ch] = len(children)
                children.append({})
                terminal.append(False)
            node = children[node][ch]
        terminal[node] = True

    s = len(children)
    go = [[0] * k for _ in range(s)]
    fail = [0] * s
    bad = terminal[:]
    queue = []

    for ch, v in children[0].items():
        i = chars[ch]
        go[0][i] = v
        queue.append(v)

    head = 0
    while head < len(queue):
        u = queue[head]
        head += 1

        for i, ch in enumerate(alphabet):
            if ch in children[u]:
                v = children[u][ch]
                fail[v] = go[fail[u]][i]
                bad[v] = bad[v] or bad[fail[v]]
                go[u][i] = v
                queue.append(v)
            else:
                go[u][i] = go[fail[u]][i]

    matrix = [[0] * s for _ in range(s)]
    for u in range(s):
        if not bad[u]:
            for i in range(k):
                v = go[u][i]
                if not bad[v]:
                    matrix[u][v] = (matrix[u][v] + 1) % MOD

    def multiply(a, b):
        size = len(a)
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for t in range(size):
                if a[i][t]:
                    ait = a[i][t]
                    for j in range(size):
                        result[i][j] = (result[i][j] + ait * b[t][j]) % MOD
        return result

    vector = [0] * s
    vector[0] = 1

    while n:
        if n & 1:
            vector = [
                sum(vector[i] * matrix[i][j] for i in range(s)) % MOD
                for j in range(s)
            ]
        matrix = multiply(matrix, matrix)
        n >>= 1

    return sum(vector) % MOD
