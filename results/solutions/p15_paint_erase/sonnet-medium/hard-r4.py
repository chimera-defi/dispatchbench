def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    q = len(ops)
    starts = {}
    ends = {}
    xs = set()
    for i, op in enumerate(ops):
        l, r = op[1], op[2] + 1
        xs.add(l)
        xs.add(r)
        starts.setdefault(l, []).append(i)
        ends.setdefault(r, []).append(i)
    xs = sorted(xs)

    N = q
    E = [0] * (2 * N)  # erase tree: index+1 if active
    P = [0] * (2 * N)  # paint tree: colour if active

    def update(t, pos, v):
        pos += N
        t[pos] = v
        pos >>= 1
        while pos:
            a = t[2 * pos]
            b = t[2 * pos + 1]
            t[pos] = a if a > b else b
            pos >>= 1

    def query(t, lo, hi):
        res = 0
        lo += N
        hi += N
        while lo < hi:
            if lo & 1:
                if t[lo] > res:
                    res = t[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                if t[hi] > res:
                    res = t[hi]
            lo >>= 1
            hi >>= 1
        return res

    counts = {}
    for k in range(len(xs) - 1):
        x = xs[k]
        for i in ends.get(x, ()):
            if ops[i][0] == 1:
                update(P, i, 0)
            else:
                update(E, i, 0)
        for i in starts.get(x, ()):
            if ops[i][0] == 1:
                update(P, i, ops[i][3])
            else:
                update(E, i, i + 1)
        T = E[1] if N > 1 else E[1]
        m = query(P, T, N)
        if m > 0:
            counts[m] = counts.get(m, 0) + xs[k + 1] - x
    return [[c, counts[c]] for c in sorted(counts)]
