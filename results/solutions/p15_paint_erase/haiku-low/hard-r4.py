from bisect import bisect_right


def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    # Disjoint, sorted segments [start, end, colour] with colour > 0.
    # Blank cells are simply not stored.
    segs = []
    starts = []

    for op in ops:
        if op[0] == 1:
            _, l, r, c = op
        else:
            _, l, r = op
            c = 0  # erase: cells become blank

        # First segment that might overlap [l, r].
        i = bisect_right(starts, l) - 1
        if i < 0 or segs[i][1] < l:
            i += 1
        # Segments with index in [i, j) start at or before r.
        j = bisect_right(starts, r)

        if i < j:
            # Keep the parts of boundary segments that lie outside [l, r].
            prefix = []
            suffix = []
            s0, _, c0 = segs[i]
            if s0 < l:
                prefix.append([s0, l - 1, c0])
            s1, e1, c1 = segs[j - 1]
            if e1 > r:
                suffix.append([r + 1, e1, c1])
        else:
            prefix, suffix = [], []

        out = []
        cur = l
        for k in range(i, j):
            s, e, col = segs[k]
            a = max(s, l)
            b = min(e, r)
            if cur < a and c:
                out.append([cur, a - 1, c])  # blank gap gets colour c
            if c:
                out.append([a, b, max(col, c)])  # keep larger colour
            cur = b + 1
        if cur <= r and c:
            out.append([cur, r, c])

        pieces = prefix + out + suffix

        # Merge adjacent pieces of the same colour.
        merged = []
        for s, e, col in pieces:
            if merged and merged[-1][1] + 1 == s and merged[-1][2] == col:
                merged[-1][1] = e
            else:
                merged.append([s, e, col])

        segs[i:j] = merged
        starts[i:j] = [p[0] for p in merged]

    counts = {}
    for s, e, col in segs:
        counts[col] = counts.get(col, 0) + (e - s + 1)

    return [[col, counts[col]] for col in sorted(counts)]
