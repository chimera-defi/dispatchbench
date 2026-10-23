from collections import deque

MOD = 1_000_000_007


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    if n == 0:
        return 1

    children = [{}]
    failure = [0]
    terminal = [False]

    for word in banned:
        state = 0
        for char in word:
            if char not in children[state]:
                children[state][char] = len(children)
                children.append({})
                failure.append(0)
                terminal.append(False)
            state = children[state][char]
        terminal[state] = True

    queue = deque()
    for char in alphabet:
        if char in children[0]:
            state = children[0][char]
            queue.append(state)
        else:
            children[0][char] = 0

    while queue:
        state = queue.popleft()
        terminal[state] |= terminal[failure[state]]

        for char in alphabet:
            if char in children[state]:
                nxt = children[state][char]
                failure[nxt] = children[failure[state]][char]
                queue.append(nxt)
            else:
                children[state][char] = children[failure[state]][char]

    safe_states = [state for state in range(len(children)) if not terminal[state]]
    index = {state: i for i, state in enumerate(safe_states)}
    size = len(safe_states)

    matrix = [[0] * size for _ in range(size)]
    for state in safe_states:
        row = matrix[index[state]]
        for char in alphabet:
            nxt = children[state][char]
            if not terminal[nxt]:
                j = index[nxt]
                row[j] = (row[j] + 1) % MOD

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            result_row = result[i]
            for k, aik in enumerate(a[i]):
                if aik:
                    b_row = b[k]
                    for j, bkj in enumerate(b_row):
                        if bkj:
                            result_row[j] = (
                                result_row[j] + aik * bkj
                            ) % MOD
        return result

    def multiply_vector(vector, mat):
        result = [0] * size
        for i, value in enumerate(vector):
            if value:
                for j, coefficient in enumerate(mat[i]):
                    if coefficient:
                        result[j] = (
                            result[j] + value * coefficient
                        ) % MOD
        return result

    vector = [0] * size
    vector[index[0]] = 1

    while n:
        if n & 1:
            vector = multiply_vector(vector, matrix)
        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(vector) % MOD
