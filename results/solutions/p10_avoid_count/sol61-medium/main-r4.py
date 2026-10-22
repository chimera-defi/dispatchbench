def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    if n == 0:
        return 1
    if not banned:
        return pow(len(alphabet), n, MOD)

    char_id = {ch: i for i, ch in enumerate(alphabet)}
    width = len(alphabet)
    transitions = [[-1] * width]
    failure = [0]
    forbidden = [False]

    for word in banned:
        state = 0
        for ch in word:
            c = char_id[ch]
            if transitions[state][c] == -1:
                transitions[state][c] = len(transitions)
                transitions.append([-1] * width)
                failure.append(0)
                forbidden.append(False)
            state = transitions[state][c]
        forbidden[state] = True

    queue = []
    for c in range(width):
        child = transitions[0][c]
        if child == -1:
            transitions[0][c] = 0
        else:
            queue.append(child)

    head = 0
    while head < len(queue):
        state = queue[head]
        head += 1
        fallback = failure[state]
        forbidden[state] |= forbidden[fallback]

        for c in range(width):
            child = transitions[state][c]
            if child == -1:
                transitions[state][c] = transitions[fallback][c]
            else:
                failure[child] = transitions[fallback][c]
                queue.append(child)

    safe = [s for s in range(len(transitions)) if not forbidden[s]]
    index = {state: i for i, state in enumerate(safe)}
    size = len(safe)
    matrix = [[0] * size for _ in range(size)]

    for i, state in enumerate(safe):
        for destination in transitions[state]:
            if not forbidden[destination]:
                matrix[i][index[destination]] += 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i, row in enumerate(a):
            out = result[i]
            for k, value in enumerate(row):
                if value:
                    for j, other in enumerate(b[k]):
                        if other:
                            out[j] += value * other
            for j in range(size):
                out[j] %= MOD
        return result

    counts = [0] * size
    counts[index[0]] = 1

    while n:
        if n & 1:
            updated = [0] * size
            for i, count in enumerate(counts):
                if count:
                    for j, ways in enumerate(matrix[i]):
                        if ways:
                            updated[j] += count * ways
            counts = [value % MOD for value in updated]

        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(counts) % MOD
