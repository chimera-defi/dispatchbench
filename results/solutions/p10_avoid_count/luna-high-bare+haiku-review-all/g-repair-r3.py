def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    mod = 1_000_000_007
    k = len(alphabet)
    char_id = {ch: i for i, ch in enumerate(alphabet)}

    transitions = [[-1] * k]
    terminal = [False]

    for word in banned:
        state = 0
        for ch in word:
            c = char_id[ch]
            nxt = transitions[state][c]
            if nxt == -1:
                nxt = len(transitions)
                transitions[state][c] = nxt
                transitions.append([-1] * k)
                terminal.append(False)
            state = nxt
        terminal[state] = True

    fail = [0] * len(transitions)
    queue = []
    for c in range(k):
        child = transitions[0][c]
        if child == -1:
            transitions[0][c] = 0
        else:
            queue.append(child)

    head = 0
    while head < len(queue):
        state = queue[head]
        head += 1
        terminal[state] |= terminal[fail[state]]

        for c in range(k):
            child = transitions[state][c]
            if child == -1:
                transitions[state][c] = transitions[fail[state]][c]
            else:
                fail[child] = transitions[fail[state]][c]
                queue.append(child)

    safe_states = [s for s in range(len(transitions)) if not terminal[s]]
    index = {s: i for i, s in enumerate(safe_states)}
    size = len(safe_states)

    matrix = [[0] * size for _ in range(size)]
    for s in safe_states:
        i = index[s]
        for c in range(k):
            target = transitions[s][c]
            if not terminal[target]:
                j = index[target]
                matrix[i][j] += 1

    vector = [0] * size
    vector[index[0]] = 1

    def multiply_matrices(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for t, value in enumerate(a[i]):
                if value:
                    for j, other in enumerate(b[t]):
                        if other:
                            result[i][j] = (result[i][j] + value * other) % mod
        return result

    def multiply_vector(v, a):
        result = [0] * size
        for i, value in enumerate(v):
            if value:
                for j, other in enumerate(a[i]):
                    if other:
                        result[j] = (result[j] + value * other) % mod
        return result

    while n:
        if n & 1:
            vector = multiply_vector(vector, matrix)
        n >>= 1
        if n:
            matrix = multiply_matrices(matrix, matrix)

    return sum(vector) % mod
