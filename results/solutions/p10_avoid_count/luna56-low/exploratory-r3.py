def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007

    patterns = list(set(banned))
    prefixes = {""}
    for word in patterns:
        for i in range(1, len(word)):
            prefixes.add(word[:i])

    states = sorted(prefixes)
    index = {s: i for i, s in enumerate(states)}
    size = len(states)

    transitions = [[0] * size for _ in range(size)]

    for state in states:
        i = index[state]
        for ch in alphabet:
            candidate = state + ch
            if any(candidate.endswith(word) for word in patterns):
                continue

            best = ""
            for prefix in states:
                if candidate.endswith(prefix) and len(prefix) > len(best):
                    best = prefix
            transitions[i][index[best]] += 1

    def mat_mul(a, b):
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            for k in range(size):
                if a[i][k]:
                    aik = a[i][k]
                    for j in range(size):
                        if b[k][j]:
                            result[i][j] = (result[i][j] + aik * b[k][j]) % MOD
        return result

    def mat_vec_mul(matrix, vector):
        result = [0] * size
        for i in range(size):
            total = 0
            for j in range(size):
                total += matrix[i][j] * vector[j]
            result[i] = total % MOD
        return result

    vector = [0] * size
    vector[index[""]] = 1
    matrix = transitions

    while n:
        if n & 1:
            vector = mat_vec_mul(matrix, vector)
        matrix = mat_mul(matrix, matrix)
        n >>= 1

    return sum(vector) % MOD
