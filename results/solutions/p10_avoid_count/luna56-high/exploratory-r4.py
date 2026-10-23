def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    children = [{}]
    terminal = [False]

    for word in banned:
        state = 0
        for ch in word:
            if ch not in children[state]:
                children[state][ch] = len(children)
                children.append({})
                terminal.append(False)
            state = children[state][ch]
        terminal[state] = True

    size = len(children)
    fail = [0] * size
    bad = terminal[:]

    queue = []
    for child in children[0].values():
        queue.append(child)

    head = 0
    while head < len(queue):
        state = queue[head]
        head += 1

        for ch, child in children[state].items():
            f = fail[state]
            while f and ch not in children[f]:
                f = fail[f]
            fail[child] = children[f].get(ch, 0)
            bad[child] = bad[child] or bad[fail[child]]
            queue.append(child)

    transitions = [[0] * size for _ in range(size)]

    for state in range(size):
        for ch in alphabet:
            next_state = state
            while next_state and ch not in children[next_state]:
                next_state = fail[next_state]
            next_state = children[next_state].get(ch, 0)

            if not bad[next_state]:
                transitions[state][next_state] += 1

    def mat_mul(a, b):
        m = len(a)
        result = [[0] * m for _ in range(m)]
        for i in range(m):
            for k in range(m):
                if a[i][k]:
                    aik = a[i][k]
                    for j in range(m):
                        result[i][j] = (result[i][j] + aik * b[k][j]) % MOD
        return result

    def vec_mul(vec, matrix):
        result = [0] * size
        for i, value in enumerate(vec):
            if value:
                for j in range(size):
                    result[j] = (result[j] + value * matrix[i][j]) % MOD
        return result

    vector = [0] * size
    vector[0] = 1
    matrix = transitions

    while n:
        if n & 1:
            vector = vec_mul(vector, matrix)
        matrix = mat_mul(matrix, matrix)
        n >>= 1

    return sum(vector) % MOD
