from collections import deque


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    if n == 0:
        return 1
    if not banned:
        return pow(len(alphabet), n, MOD)

    k = len(alphabet)
    char_index = {ch: i for i, ch in enumerate(alphabet)}
    transitions = [[-1] * k]
    failure = [0]
    forbidden = [False]

    for word in banned:
        state = 0
        for ch in word:
            c = char_index[ch]
            if transitions[state][c] == -1:
                transitions[state][c] = len(transitions)
                transitions.append([-1] * k)
                failure.append(0)
                forbidden.append(False)
            state = transitions[state][c]
        forbidden[state] = True

    queue = deque()
    for c in range(k):
        child = transitions[0][c]
        if child == -1:
            transitions[0][c] = 0
        else:
            queue.append(child)

    while queue:
        state = queue.popleft()
        fallback = failure[state]
        forbidden[state] |= forbidden[fallback]

        for c in range(k):
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

    for i, state in enumerate(safe_states):
        for target in transitions[state]:
            if not forbidden[target]:
                matrix[i][index[target]] += 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i, row in enumerate(a):
            out = result[i]
            for j, value in enumerate(row):
                if value:
                    for t, other in enumerate(b[j]):
                        if other:
                            out[t] += value * other
            for t in range(size):
                out[t] %= MOD
        return result

    vector = [0] * size
    vector[index[0]] = 1

    while n:
        if n & 1:
            updated = [0] * size
            for i, value in enumerate(vector):
                if value:
                    for j, weight in enumerate(matrix[i]):
                        if weight:
                            updated[j] += value * weight
            vector = [value % MOD for value in updated]

        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(vector) % MOD
