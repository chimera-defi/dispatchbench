from collections import deque

MOD = 1_000_000_007


def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    # Build the trie of banned strings.
    children: list[dict[str, int]] = [{}]
    terminal: list[bool] = [False]
    for word in banned:
        node = 0
        for ch in word:
            if ch not in children[node]:
                children[node][ch] = len(children)
                children.append({})
                terminal.append(False)
            node = children[node][ch]
        terminal[node] = True

    # Build the Aho-Corasick automaton (full goto function and failure links).
    m = len(children)
    goto: list[dict[str, int]] = [{} for _ in range(m)]
    fail = [0] * m
    queue = deque([0])
    while queue:
        u = queue.popleft()
        if u != 0:
            # fail[u] has smaller depth, so its terminal flag is already final.
            terminal[u] = terminal[u] or terminal[fail[u]]
        for ch in alphabet:
            if ch in children[u]:
                v = children[u][ch]
                goto[u][ch] = v
                fail[v] = goto[fail[u]][ch] if u != 0 else 0
                queue.append(v)
            else:
                goto[u][ch] = goto[fail[u]][ch] if u != 0 else 0

    # Transition matrix over non-terminal states only.
    alive = [u for u in range(m) if not terminal[u]]
    idx = {u: i for i, u in enumerate(alive)}
    k = len(alive)
    M = [[0] * k for _ in range(k)]
    for u in alive:
        for ch in alphabet:
            v = goto[u][ch]
            if not terminal[v]:
                M[idx[u]][idx[v]] += 1

    def mat_mul(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
        size = len(A)
        result = [[0] * size for _ in range(size)]
        for i in range(size):
            row = result[i]
            for t, a in enumerate(A[i]):
                if a:
                    b_row = B[t]
                    for j in range(size):
                        row[j] += a * b_row[j]
            for j in range(size):
                row[j] %= MOD
        return result

    def vec_mul(x: list[int], A: list[list[int]]) -> list[int]:
        size = len(x)
        result = [0] * size
        for i, xi in enumerate(x):
            if xi:
                for j in range(size):
                    result[j] += xi * A[i][j]
        return [r % MOD for r in result]

    # Row vector starts at the root (index 0 in `alive`, since root is non-terminal).
    x = [0] * k
    x[idx[0]] = 1

    # Apply M^n to the vector via binary exponentiation.
    e = n
    while e:
        if e & 1:
            x = vec_mul(x, M)
        e >>= 1
        if e:
            M = mat_mul(M, M)

    return sum(x) % MOD
