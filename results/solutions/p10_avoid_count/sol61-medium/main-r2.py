def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    from collections import deque

    MOD = 1_000_000_007
    if n == 0:
        return 1
    if not banned:
        return pow(len(alphabet), n, MOD)

    char_id = {ch: i for i, ch in enumerate(alphabet)}
    width = len(alphabet)
    transitions = [[-1] * width]
    failure = [0]
    terminal = [False]

    for word in banned:
        state = 0
        for ch in word:
            c = char_id[ch]
            if transitions[state][c] == -1:
                transitions[state][c] = len(transitions)
                transitions.append([-1] * width)
                failure.append(0)
                terminal.append(False)
            state = transitions[state][c]
        terminal[state] = True

    queue = deque()
    for c in range(width):
        child = transitions[0][c]
        if child == -1:
            transitions[0][c] = 0
        else:
            queue.append(child)

    while queue:
        state = queue.popleft()
        terminal[state] |= terminal[failure[state]]
        for c in range(width):
            child = transitions[state][c]
            fallback = transitions[failure[state]][c]
            if child == -1:
                transitions[state][c] = fallback
            else:
                failure[child] = fallback
                queue.append(child)

    safe = [s for s in range(len(transitions)) if not terminal[s]]
    index = {state: i for i, state in enumerate(safe)}
    size = len(safe)
    matrix = [[0] * size for _ in range(size)]

    for state in safe:
        row = matrix[index[state]]
        for dest in transitions[state]:
            if not terminal[dest]:
                row[index[dest]] += 1

    def square(a):
        result = [[0] * size for _ in range(size)]
        for i, row in enumerate(a):
            out = result[i]
            for k, value in enumerate(row):
                if value:
                    for j, other in enumerate(a[k]):
                        if other:
                            out[j] = (out[j] + value * other) % MOD
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
                            updated[j] = (updated[j] + count * ways) % MOD
            counts = updated
        n >>= 1
        if n:
            matrix = square(matrix)

    return sum(counts) % MOD
