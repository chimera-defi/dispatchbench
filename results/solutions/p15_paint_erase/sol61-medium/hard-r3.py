def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    # Each interval between consecutive boundaries behaves as one cell.
    boundaries = {1, n + 1}
    for op in ops:
        boundaries.add(op[1])
        boundaries.add(op[2] + 1)

    xs = sorted(boundaries)
    index = {x: i for i, x in enumerate(xs)}
    size = len(xs) - 1

    INF = 10**9 + 1
    minimum = [0] * (4 * size)
    second = [INF] * (4 * size)
    counts = {}

    def push(v):
        value = minimum[v]
        left = v * 2
        right = left + 1
        if minimum[left] < value:
            minimum[left] = value
        if minimum[right] < value:
            minimum[right] = value

    def pull(v):
        left = v * 2
        right = left + 1
        a, b = minimum[left], minimum[right]
        if a < b:
            minimum[v] = a
            second[v] = min(second[left], b)
        elif a > b:
            minimum[v] = b
            second[v] = min(a, second[right])
        else:
            minimum[v] = a
            second[v] = min(second[left], second[right])

    def raise_range(v, lo, hi, ql, qr, colour):
        if qr <= lo or hi <= ql or minimum[v] >= colour:
            return

        if ql <= lo and hi <= qr and colour < second[v]:
            minimum[v] = colour
            return

        push(v)
        mid = (lo + hi) // 2
        raise_range(v * 2, lo, mid, ql, qr, colour)
        raise_range(v * 2 + 1, mid, hi, ql, qr, colour)
        pull(v)

    def finalize_range(v, lo, hi, ql, qr):
        if qr <= lo or hi <= ql or minimum[v] == INF:
            return

        if hi - lo == 1:
            colour = minimum[v]
            if colour:
                counts[colour] = counts.get(colour, 0) + xs[hi] - xs[lo]
            minimum[v] = INF
            return

        push(v)
        mid = (lo + hi) // 2
        finalize_range(v * 2, lo, mid, ql, qr)
        finalize_range(v * 2 + 1, mid, hi, ql, qr)
        pull(v)

    # In reverse, accumulate the maximum paint until the first erase.
    # That erase fixes the final colour, so the interval is then retired.
    for op in reversed(ops):
        left = index[op[1]]
        right = index[op[2] + 1]
        if op[0] == 1:
            raise_range(1, 0, size, left, right, op[3])
        else:
            finalize_range(1, 0, size, left, right)

    finalize_range(1, 0, size, 0, size)
    return [[colour, counts[colour]] for colour in sorted(counts)]
