def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    from collections import deque

    MOD = 1_000_000_007
    char_id = {ch: i for i, ch in enumerate(alphabet)}
    sigma = len(alphabet)

    children = [[-1] * sigma]
    failure = [0]
    terminal = [False]

    for word in banned:
        state = 0
        for ch in word:
            c = char_id[ch]
            if children[state][c] == -1:
                children[state][c] = len(children)
                children.append([-1] * sigma)
                failure.append(0)
                terminal.append(False)
            state = children[state][c]
        terminal[state] = True

    queue = deque()
    for c in range(sigma):
        nxt = children[0][c]
        if nxt == -1:
            children[0][c] = 0
        else:
            queue.append(nxt)

    while queue:
        state = queue.popleft()
        terminal[state] |= terminal[failure[state]]

        for c in range(sigma):
            nxt = children[state][c]
            if nxt == -1:
                children[state][c] = children[failure[state]][c]
            else:
                failure[nxt] = children[failure[state]][c]
                queue.append(nxt)

    safe_states = [state for state in range(len(children)) if not terminal[state]]
    safe_index = {state: i for i, state in enumerate(safe_states)}
    size = len(safe_states)

    transition = [[0] * size for _ in range(size)]
    for state in safe_states:
        i = safe_index[state]
        for c in range(sigma):
            nxt = children[state][c]
            if not terminal[nxt]:
                transition[i][safe_index[nxt]] += 1

    def multiply_matrices(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k in range(size):
                if a[i][k]:
                    aik = a[i][k]
                    for j in range(size):
                        if b[k][j]:
                            result[i][j] = (
                                result[i][j] + aik * b[k][j]
                            ) % MOD
        return result

    def multiply_vector(vector, matrix):
        result = [0] * size
        for i in range(size):
            if vector[i]:
                for j in range(size):
                    if matrix[i][j]:
                        result[j] = (
                            result[j] + vector[i] * matrix[i][j]
                        ) % MOD
        return result

    vector = [0] * size
    vector[safe_index[0]] = 1

    while n:
        if n & 1:
            vector = multiply_vector(vector, transition)
        n >>= 1
        if n:
            transition = multiply_matrices(transition, transition)

    return sum(vector) % MOD
