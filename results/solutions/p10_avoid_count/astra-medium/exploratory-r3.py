def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    from collections import deque

    MOD = 1_000_000_007
    if n == 0:
        return 1
    if not banned:
        return pow(len(alphabet), n, MOD)

    k = len(alphabet)
    char_id = {ch: i for i, ch in enumerate(alphabet)}
    transitions = [[-1] * k]
    fail = [0]
    forbidden = [False]

    for word in banned:
        state = 0
        for ch in word:
            c = char_id[ch]
            if transitions[state][c] == -1:
                transitions[state][c] = len(transitions)
                transitions.append([-1] * k)
                fail.append(0)
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
        forbidden[state] |= forbidden[fail[state]]
        for c in range(k):
            child = transitions[state][c]
            if child == -1:
                transitions[state][c] = transitions[fail[state]][c]
            else:
                fail[child] = transitions[fail[state]][c]
                queue.append(child)

    safe = [s for s in range(len(transitions)) if not forbidden[s]]
    index = {s: i for i, s in enumerate(safe)}
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
            for mid, value in enumerate(a_row):
                if value:
                    for j, other in enumerate(b[mid]):
                        row[j] += value * other
            result.append([value % MOD for value in row])
        return result

    counts = [0] * size
    counts[index[0]] = 1

    while n:
        if n & 1:
            updated = [0] * size
            for i, count in enumerate(counts):
                if count:
                    for j, ways in enumerate(matrix[i]):
                        updated[j] += count * ways
            counts = [value % MOD for value in updated]
        n >>= 1
        if n:
            matrix = multiply(matrix, matrix)

    return sum(counts) % MOD
