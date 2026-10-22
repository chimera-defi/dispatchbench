def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    coords = sorted({x for op in ops for x in (op[1], op[2] + 1)})
    index = {x: i for i, x in enumerate(coords)}
    m = len(coords) - 1
    if m <= 0:
        return []

    size = 4 * m
    done = [False] * size
    lazy = [0] * size
    counts = {}

    def apply(node: int, color: int) -> None:
        if not done[node] and color > lazy[node]:
            lazy[node] = color

    def push(node: int) -> None:
        color = lazy[node]
        if color:
            apply(node * 2, color)
            apply(node * 2 + 1, color)
            lazy[node] = 0

    def raise_range(node: int, left: int, right: int,
                    ql: int, qr: int, color: int) -> None:
        if done[node] or qr <= left or right <= ql:
            return
        if ql <= left and right <= qr:
            apply(node, color)
            return
        push(node)
        mid = (left + right) // 2
        raise_range(node * 2, left, mid, ql, qr, color)
        raise_range(node * 2 + 1, mid, right, ql, qr, color)
        done[node] = done[node * 2] and done[node * 2 + 1]

    def finalize(node: int, left: int, right: int) -> None:
        if done[node]:
            return
        if right - left == 1:
            color = lazy[node]
            if color:
                counts[color] = counts.get(color, 0) + coords[right] - coords[left]
            done[node] = True
            return
        push(node)
        mid = (left + right) // 2
        finalize(node * 2, left, mid)
        finalize(node * 2 + 1, mid, right)
        done[node] = done[node * 2] and done[node * 2 + 1]

    def erase_range(node: int, left: int, right: int,
                    ql: int, qr: int) -> None:
        if done[node] or qr <= left or right <= ql:
            return
        if ql <= left and right <= qr:
            finalize(node, left, right)
            return
        push(node)
        mid = (left + right) // 2
        erase_range(node * 2, left, mid, ql, qr)
        erase_range(node * 2 + 1, mid, right, ql, qr)
        done[node] = done[node * 2] and done[node * 2 + 1]

    for op in reversed(ops):
        ql = index[op[1]]
        qr = index[op[2] + 1]
        if op[0] == 1:
            raise_range(1, 0, m, ql, qr, op[3])
        else:
            erase_range(1, 0, m, ql, qr)

    finalize(1, 0, m)
    return [[color, counts[color]] for color in sorted(counts)]
