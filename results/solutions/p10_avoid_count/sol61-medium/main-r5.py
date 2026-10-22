def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    from collections import deque

    MOD = 1_000_000_007
    if n == 0:
        return 1
    if not banned:
        return pow(len(alphabet), n, MOD)

    char_index = {ch: i for i, ch in enumerate(alphabet)}
    width = len(alphabet)

    transitions = [[-1] * width]
    failure = [0]
    forbidden = [False]

    for word in banned:
        state = 0
        for ch in word:
            c = char_index[ch]
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
    index = {s: i for i, s in enumerate(safe_states)}
    size = len(safe_states)

    matrix = [[0] * size for _ in range(size)]
    for state in safe_states:
        row = matrix[index[state]]
        for target in transitions[state]:
            if not forbidden[target]:
                row[index[target]] += 1

    def square(a):
        result = [[0] * size for _ in range(size)]
        for i, a_row in enumerate(a):
            result_row = result[i]
            for k, value in enumerate(a_row):
                if value:
                    for j, other in enumerate(a[k]):
                        if other:
                            result_row[j] += value * other
            for j in range(size):
                result_row[j] %= MOD
        return result

    counts = [0] * size
    counts[index[0]] = 1

    while n:
        if n & 1:
            updated = [0] * size
            for i, value in enumerate(counts):
                if value:
                    for j, ways in enumerate(matrix[i]):
                        if ways:
                            updated[j] += value * ways
            counts = [value % MOD for value in updated]

        n >>= 1
        if n:
            matrix = square(matrix)

    return sum(counts) % MOD
