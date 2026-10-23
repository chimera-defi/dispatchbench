def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    from collections import deque

    MOD = 1_000_000_007
    if n == 0:
        return 1
    if not banned:
        return pow(len(alphabet), n, MOD)

    char_index = {ch: i for i, ch in enumerate(alphabet)}
    k = len(alphabet)

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

    safe_states = [
        state for state in range(len(transitions))
        if not forbidden[state]
    ]
    index = {state: i for i, state in enumerate(safe_states)}
    size = len(safe_states)

    matrix = [[0] * size for _ in range(size)]
    for state in safe_states:
        row = matrix[index[state]]
        for target in transitions[state]:
            if not forbidden[target]:
                row[index[target]] += 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i, a_row in enumerate(a):
            result_row = result[i]
            for middle, value in enumerate(a_row):
                if value:
                    for j, other in enumerate(b[middle]):
                        if other:
                            result_row[j] += value * other
            for j in range(size):
                result_row[j] %= MOD
        return result

    counts = [0] * size
    counts[index[0]] = 1

    while n:
        if n & 1:
            next_counts = [0] * size
            for i, count in enumerate(counts):
                if count:
                    for j, ways in enumerate(matrix[i]):
                        if ways:
                            next_counts[j] += count * ways
            counts = [count % MOD for count in next_counts]

        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(counts) % MOD
