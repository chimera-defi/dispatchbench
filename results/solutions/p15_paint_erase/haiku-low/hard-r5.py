def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    # Blank cells are modelled as colour 0. Since every colour is >= 1,
    # "keep the greater colour, else take c" is exactly max(old, c).
    # Erasing is assigning 0.
    pts = {1, n + 1}
    for op in ops:
        if op[0] == 1:
            _, l, r, _ = op
        else:
            _, l, r = op
        pts.add(l)
        pts.add(r + 1)
    pts = sorted(pts)
    idx = {p: i for i, p in enumerate(pts)}
    m = len(pts) - 1  # number of elementary segments

    # Lazy tag: (is_assign, value). Identity is (False, 0) since max(x, 0) = x.
    size = 4 * m
    tag_kind = [False] * size
    tag_val = [0] * size

    def compose(old_kind, old_val, new_kind, new_val):
        # Apply old first, then new.
        if new_kind:
            return True, new_val
        if old_kind:
            return True, max(old_val, new_val)
        return False, max(old_val, new_val)

    def apply(node, kind, val):
        k, v = compose(tag_kind[node], tag_val[node], kind, val)
        tag_kind[node] = k
        tag_val[node] = v

    def push(node):
        if tag_kind[node] or tag_val[node]:
            kind, val = tag_kind[node], tag_val[node]
            apply(2 * node, kind, val)
            apply(2 * node + 1, kind, val)
            tag_kind[node] = False
            tag_val[node] = 0

    def update(node, lo, hi, a, b, kind, val):
        if b < lo or hi < a:
            return
        if a <= lo and hi <= b:
            apply(node, kind, val)
            return
        push(node)
        mid = (lo + hi) // 2
        update(2 * node, lo, mid, a, b, kind, val)
        update(2 * node + 1, mid + 1, hi, a, b, kind, val)

    for op in ops:
        if op[0] == 1:
            _, l, r, c = op
            update(1, 0, m - 1, idx[l], idx[r + 1] - 1, False, c)
        else:
            _, l, r = op
            update(1, 0, m - 1, idx[l], idx[r + 1] - 1, True, 0)

    # Collect leaf values and lengths.
    totals = {}

    def collect(node, lo, hi):
        if lo == hi:
            colour = tag_val[node]  # leaf value: assign -> v, chmax on 0 -> v
            if colour:
                length = pts[lo + 1] - pts[lo]
                totals[colour] = totals.get(colour, 0) + length
            return
        push(node)
        mid = (lo + hi) // 2
        collect(2 * node, lo, mid)
        collect(2 * node + 1, mid + 1, hi)

    collect(1, 0, m - 1)
    return [[c, totals[c]] for c in sorted(totals)]
