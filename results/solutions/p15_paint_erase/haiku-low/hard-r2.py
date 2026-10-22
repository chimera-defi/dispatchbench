from bisect import bisect_left, bisect_right


def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    # Disjoint, sorted coloured segments [S[k], E[k]] with colour C[k].
    # Blank cells are simply not stored.
    S: list[int] = []
    E: list[int] = []
    C: list[int] = []

    def cut(l: int, r: int):
        # Remove coverage of [l, r]; return removed pieces (sorted) and their insert index.
        i = bisect_left(E, l)
        j = bisect_right(S, r)
        pos = bisect_left(S, l)
        if i >= j:
            return [], pos
        removed = []
        for k in range(i, j):
            removed.append((max(S[k], l), min(E[k], r), C[k]))
        newS, newE, newC = [], [], []
        if S[i] < l:
            newS.append(S[i])
            newE.append(l - 1)
            newC.append(C[i])
        if E[j - 1] > r:
            newS.append(r + 1)
            newE.append(E[j - 1])
            newC.append(C[j - 1])
        S[i:j] = newS
        E[i:j] = newE
        C[i:j] = newC
        return removed, pos

    for op in ops:
        if op[0] == 1:
            _, l, r, c = op
            removed, _ = cut(l, r)
            pieces = []
            cur = l
            for s, e, col in removed:
                if s > cur:
                    pieces.append((cur, s - 1, c))  # blank gap takes c
                # Keep existing colour only if it is greater than c
                pieces.append((s, e, col if col > c else c))
                cur = e + 1
            if cur <= r:
                pieces.append((cur, r, c))

            # Merge adjacent pieces of equal colour
            merged = []
            for s, e, col in pieces:
                if merged and merged[-1][2] == col and merged[-1][1] + 1 == s:
                    merged[-1] = (merged[-1][0], e, col)
                else:
                    merged.append((s, e, col))

            if merged:
                pos = bisect_left(S, l)
                S[pos:pos] = [p[0] for p in merged]
                E[pos:pos] = [p[1] for p in merged]
                C[pos:pos] = [p[2] for p in merged]
        else:
            _, l, r = op
            cut(l, r)

    cnt: dict[int, int] = {}
    for s, e, col in zip(S, E, C):
        cnt[col] = cnt.get(col, 0) + (e - s + 1)

    return [[col, cnt[col]] for col in sorted(cnt)]
