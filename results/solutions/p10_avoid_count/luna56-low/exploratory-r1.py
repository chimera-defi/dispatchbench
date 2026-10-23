def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    patterns = list(set(banned))
    prefixes = {""}
    for pattern in patterns:
        for i in range(1, len(pattern)):
            prefixes.add(pattern[:i])

    prefixes = list(prefixes)
    index = {s: i for i, s in enumerate(prefixes)}
    m = len(prefixes)
    transitions = [[0] * m for _ in range(m)]

    for state, suffix in enumerate(prefixes):
        for ch in alphabet:
            candidate = suffix + ch
            if any(candidate.endswith(pattern) for pattern in patterns):
                continue

            next_state = ""
            for prefix in prefixes:
                if candidate.endswith(prefix) and len(prefix) > len(next_state):
                    next_state = prefix

            transitions[state][index[next_state]] += 1

    def mat_mul(a, b):
        size = len(a)
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k in range(size):
                if a[i][k]:
                    aik = a[i][k]
                    for j in range(size):
                        result[i][j] = (result[i][j] + aik * b[k][j]) % MOD
        return result

    def mat_vec_mul(v, matrix):
        size = len(v)
        result = [0] * size
        for i, vi in enumerate(v):
            if vi:
                for j in range(size):
                    result[j] = (result[j] + vi * matrix[i][j]) % MOD
        return result

    vector = [0] * m
    vector[index[""]] = 1

    while n:
        if n & 1:
            vector = mat_vec_mul(vector, transitions)
        transitions = mat_mul(transitions, transitions)
        n >>= 1

    return sum(vector) % MOD
