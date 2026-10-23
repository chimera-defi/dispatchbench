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
        forbidden[state] |= forbidden[failure[state]]

        for c in range(width):
            child = transitions[state][c]
            if child == -1:
                transitions[state][c] = transitions[failure[state]][c]
            else:
                failure[child] = transitions[failure[state]][c]
                queue.append(child)

    safe = [s for s in range(len(transitions)) if not forbidden[s]]
    index = {state: i for i, state in enumerate(safe)}
    size = len(safe)
    matrix = [[0] * size for _ in range(size)]

    for state in safe:
        row = matrix[index[state]]
        for target in transitions[state]:
            if not forbidden[target]:
                row[index[target]] += 1

    def multiply(a, b):
        result = []
        for a_row in a:
            row = [0] * size
            for k, value in enumerate(a_row):
                if value:
                    b_row = b[k]
                    for j, entry in enumerate(b_row):
                        row[j] += value * entry
            result.append([value % MOD for value in row])
        return result

    counts = [[0] * size]
    counts[0][index[0]] = 1

    while n:
        if n & 1:
            counts = multiply(counts, matrix)
        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(counts[0]) % MOD
