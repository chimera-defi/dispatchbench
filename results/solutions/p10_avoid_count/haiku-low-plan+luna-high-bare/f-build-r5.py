def avoid_count(n: int, alphabet: str, banned: list[str]) -> int:
    MOD = 1_000_000_007
    if n == 0:
        return 1

    char_index = {ch: i for i, ch in enumerate(alphabet)}
    k = len(alphabet)

    children = [[-1] * k]
    fail = [0]
    terminal = [False]

    for word in banned:
        node = 0
        for ch in word:
            c = char_index[ch]
            nxt = children[node][c]
            if nxt == -1:
                nxt = len(children)
                children[node][c] = nxt
                children.append([-1] * k)
                fail.append(0)
                terminal.append(False)
            node = nxt
        terminal[node] = True

    dead = [False] * len(children)
    dead[0] = terminal[0]
    queue = []

    for c in range(k):
        child = children[0][c]
        if child == -1:
            children[0][c] = 0
        else:
            fail[child] = 0
            queue.append(child)

    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        dead[node] = terminal[node] or dead[fail[node]]

        for c in range(k):
            child = children[node][c]
            if child == -1:
                children[node][c] = children[fail[node]][c]
            else:
                fail[child] = children[fail[node]][c]
                queue.append(child)

    live = [i for i in range(len(children)) if not dead[i]]
    remap = {node: i for i, node in enumerate(live)}
    size = len(live)

    matrix = [[0] * size for _ in range(size)]
    for node in live:
        src = remap[node]
        for c in range(k):
            nxt = children[node][c]
            if not dead[nxt]:
                matrix[src][remap[nxt]] += 1

    def multiply(a, b):
        result = [[0] * size for _ in range(size)]
        for i, row in enumerate(a):
            out = result[i]
            for mid, x in enumerate(row):
                if x:
                    brow = b[mid]
                    for j, y in enumerate(brow):
                        if y:
                            out[j] += x * y
            for j in range(size):
                out[j] %= MOD
        return result

    def vector_multiply(vector, matrix):
        result = [0] * size
        for i, x in enumerate(vector):
            if x:
                for j, y in enumerate(matrix[i]):
                    if y:
                        result[j] = (result[j] + x * y) % MOD
        return result

    vector = [0] * size
    vector[remap[0]] = 1
    power = matrix

    while n:
        if n & 1:
            vector = vector_multiply(vector, power)
        n >>= 1
        if n:
            power = multiply(power, power)

    return sum(vector) % MOD
