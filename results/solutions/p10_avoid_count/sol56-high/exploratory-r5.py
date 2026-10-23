def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    from collections import deque

    MOD = 1_000_000_007
    chars = {ch: i for i, ch in enumerate(alphabet)}
    width = len(alphabet)

    children = [{}]
    failure = [0]
    terminal = [False]

    for word in banned:
        state = 0
        for ch in word:
            idx = chars[ch]
            if idx not in children[state]:
                children[state][idx] = len(children)
                children.append({})
                failure.append(0)
                terminal.append(False)
            state = children[state][idx]
        terminal[state] = True

    states = len(children)
    transitions = [[0] * width for _ in range(states)]
    queue = deque()

    for c in range(width):
        if c in children[0]:
            child = children[0][c]
            transitions[0][c] = child
            queue.append(child)

    while queue:
        state = queue.popleft()
        terminal[state] |= terminal[failure[state]]

        for c in range(width):
            if c in children[state]:
                child = children[state][c]
                failure[child] = transitions[failure[state]][c]
                transitions[state][c] = child
                queue.append(child)
            else:
                transitions[state][c] = transitions[failure[state]][c]

    safe_states = [state for state in range(states) if not terminal[state]]
    safe_index = {state: i for i, state in enumerate(safe_states)}
    size = len(safe_states)

    matrix = [[0] * size for _ in range(size)]
    for state in safe_states:
        i = safe_index[state]
        for c in range(width):
            destination = transitions[state][c]
            if not terminal[destination]:
                j = safe_index[destination]
                matrix[i][j] += 1

    vector = [0] * size
    vector[safe_index[0]] = 1

    def multiply_vector(vector, matrix):
        result = [0] * size
        for i, value in enumerate(vector):
            if value:
                row = matrix[i]
                for j, coefficient in enumerate(row):
                    if coefficient:
                        result[j] = (result[j] + value * coefficient) % MOD
        return result

    def multiply_matrices(left, right):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            result_row = result[i]
            for k, value in enumerate(left[i]):
                if value:
                    right_row = right[k]
                    for j, coefficient in enumerate(right_row):
                        if coefficient:
                            result_row[j] = (
                                result_row[j] + value * coefficient
                            ) % MOD
        return result

    while n:
        if n & 1:
            vector = multiply_vector(vector, matrix)
        n >>= 1
        if n:
            matrix = multiply_matrices(matrix, matrix)

    return sum(vector) % MOD
