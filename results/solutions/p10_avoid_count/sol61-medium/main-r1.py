def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    from collections import deque

    MOD = 1_000_000_007
    if n == 0:
        return 1

    patterns = {s for s in banned if len(s) <= n}
    if not patterns:
        return pow(len(alphabet), n, MOD)

    width = len(alphabet)
    char_index = {c: i for i, c in enumerate(alphabet)}
    transitions = [[-1] * width]
    failure = [0]
    forbidden = [False]

    for pattern in patterns:
        state = 0
        for char in pattern:
            c = char_index[char]
            if transitions[state][c] == -1:
                transitions[state][c] = len(transitions)
                transitions.append([-1] * width)
                failure.append(0)
                forbidden.append(False)
            state = transitions[state][c]
        forbidden[state] = True

    queue = deque()
    for c in range(width):
        child = transitions[0][c]
        if child == -1:
            transitions[0][c] = 0
        else:
            queue.append(child)

    while queue:
        state = queue.popleft()
        fallback = failure[state]
        forbidden[state] |= forbidden[fallback]
        for c in range(width):
            child = transitions[state][c]
            if child == -1:
                transitions[state][c] = transitions[fallback][c]
            else:
                failure[child] = transitions[fallback][c]
                queue.append(child)

    safe_states = [s for s in range(len(transitions)) if not forbidden[s]]
    index = {state: i for i, state in enumerate(safe_states)}
    size = len(safe_states)
    matrix = [[0] * size for _ in range(size)]

    for state in safe_states:
        row = matrix[index[state]]
        for destination in transitions[state]:
            if not forbidden[destination]:
                row[index[destination]] += 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i, a_row in enumerate(a):
            result_row = result[i]
            for k, value in enumerate(a_row):
                if value:
                    for j, other in enumerate(b[k]):
                        if other:
                            result_row[j] += value * other
            for j in range(size):
                result_row[j] %= MOD
        return result

    vector = [0] * size
    vector[index[0]] = 1

    while n:
        if n & 1:
            updated = [0] * size
            for i, value in enumerate(vector):
                if value:
                    for j, count in enumerate(matrix[i]):
                        if count:
                            updated[j] += value * count
            vector = [value % MOD for value in updated]
        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(vector) % MOD
