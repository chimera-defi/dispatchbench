import bisect


def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    # Disjoint, sorted segments [start, end, colour]; blank cells are not stored.
    segs = []

    for op in ops:
        is_paint = op[0] == 1
        if is_paint:
            _, l, r, c = op
        else:
            _, l, r = op

        # Segments overlapping [l, r] are segs[i:j].
        i = bisect.bisect_left(segs, l, key=lambda s: s[1])
        j = bisect.bisect_right(segs, r, key=lambda s: s[0])

        # Keep the parts of boundary segments that fall outside [l, r].
        left, right = [], []
        if i < j:
            s0, _, c0 = segs[i]
            if s0 < l:
                left = [[s0, l - 1, c0]]
            _, e1, c1 = segs[j - 1]
            if e1 > r:
                right = [[r + 1, e1, c1]]

        new = []
        if is_paint:
            # Occupied cells keep the larger colour; blank cells take c.
            pos = l
            for k in range(i, j):
                s, e, col = segs[k]
                a = max(s, l)
                b = min(e, r)
                if pos < a:
                    new.append([pos, a - 1, c])
                new.append([a, b, max(col, c)])
                pos = b + 1
            if pos <= r:
                new.append([pos, r, c])

            # Merge adjacent pieces of equal colour to keep the list small.
            merged = []
            for seg in new:
                if merged and merged[-1][2] == seg[2] and merged[-1][1] + 1 == seg[0]:
                    merged[-1][1] = seg[1]
                else:
                    merged.append(seg)
            new = merged

        segs[i:j] = left + new + right

    totals = {}
    for s, e, col in segs:
        totals[col] = totals.get(col, 0) + (e - s + 1)

    return [[col, totals[col]] for col in sorted(totals)]
