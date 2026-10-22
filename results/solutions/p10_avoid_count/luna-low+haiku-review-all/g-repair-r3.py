from collections import deque


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    if n == 0:
        return 1

    banned_set = set(banned)
    if "" in banned_set:
        return 0

    chars = list(alphabet)

    # Any forbidden string containing another forbidden string is redundant.
    patterns = [
        word for word in banned_set
        if not any(other != word and other in word for other in banned_set)
    ]

    # Aho-Corasick automaton. Terminal states and their failure descendants
    # are omitted from the safe-state transition matrix.
    next_state = [{}]
    fail = [0]
    terminal = [False]

    for word in patterns:
        state = 0
        for ch in word:
            if ch not in next_state[state]:
                next_state[state][ch] = len(next_state)
                next_state.append({})
                fail.append(0)
                terminal.append(False)
            state = next_state[state][ch]
        terminal[state] = True

    queue = deque()
    for ch in chars:
        child = next_state[0].get(ch)
        if child is not None:
            queue.append(child)
        else:
            next_state[0][ch] = 0

    while queue:
        state = queue.popleft()
        terminal[state] |= terminal[fail[state]]
        for ch in chars:
            child = next_state[state].get(ch)
            fallback = next_state[fail[state]][ch]
            if child is None:
                next_state[state][ch] = fallback
            else:
                fail[child] = fallback
                queue.append(child)

    safe_states = [s for s in range(len(next_state)) if not terminal[s]]
    if not safe_states:
        return 0

    safe_index = {s: i for i, s in enumerate(safe_states)}
    size = len(safe_states)

    matrix = [[0] * size for _ in range(size)]
    for s in safe_states:
        i = safe_index[s]
        for ch in chars:
            dest = next_state[s][ch]
            if not terminal[dest]:
                j = safe_index[dest]
                matrix[i][j] = (matrix[i][j] + 1) % MOD

    # Row-vector multiplication: vector * matrix.
    vector = [0] * size
    vector[safe_index[0]] = 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k, value in enumerate(a[i]):
                if value:
                    for j, other in enumerate(b[k]):
                        if other:
                            result[i][j] = (result[i][j] + value * other) % MOD
        return result

    def apply(vec, mat):
        result = [0] * size
        for i, value in enumerate(vec):
            if value:
                for j, ways in enumerate(mat[i]):
                    if ways:
                        result[j] = (result[j] + value * ways) % MOD
        return result

    while n:
        if n & 1:
            vector = apply(vector, matrix)
        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(vector) % MOD
