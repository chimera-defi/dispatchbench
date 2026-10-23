def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    coords = {1, n + 1}
    for op in ops:
        coords.add(op[1])
        coords.add(op[2] + 1)

    coords = sorted(coords)
    m = len(coords) - 1
    size = 4 * m + 5

    mx = [0] * size
    smax = [-1] * size
    cnt = [0] * size
    lazy = [-1] * size

    def build(node: int, left: int, right: int) -> None:
        cnt[node] = right - left + 1
        if left != right:
            mid = (left + right) // 2
            build(node * 2, left, mid)
            build(node * 2 + 1, mid + 1, right)

    def apply_zero(node: int, left: int, right: int) -> None:
        mx[node] = 0
        smax[node] = -1
        cnt[node] = right - left + 1
        lazy[node] = 0

    def apply_chmin(node: int, value: int) -> None:
        if mx[node] <= value:
            return
        mx[node] = value
        if lazy[node] != -1:
            lazy[node] = min(lazy[node], value)

    def push(node: int, left: int, right: int) -> None:
        if left == right:
            lazy[node] = -1
            return

        lc = node * 2
        rc = lc + 1
        mid = (left + right) // 2

        if lazy[node] != -1:
            value = lazy[node]
            apply_zero(lc, left, mid) if value == 0 else None
            apply_zero(rc, mid + 1, right) if value == 0 else None
            if value != 0:
                mx[lc] = mx[rc] = value
                smax[lc] = smax[rc] = -1
                cnt[lc] = mid - left + 1
                cnt[rc] = right - mid
                lazy[lc] = lazy[rc] = value
            lazy[node] = -1

        if mx[lc] > mx[node]:
            apply_chmin(lc, mx[node])
        if mx[rc] > mx[node]:
            apply_chmin(rc, mx[node])

    def pull(node: int) -> None:
        lc = node * 2
        rc = lc + 1
        if mx[lc] == mx[rc]:
            mx[node] = mx[lc]
            cnt[node] = cnt[lc] + cnt[rc]
            smax[node] = max(smax[lc], smax[rc])
        elif mx[lc] > mx[rc]:
            mx[node] = mx[lc]
            cnt[node] = cnt[lc]
            smax[node] = max(smax[lc], mx[rc])
        else:
            mx[node] = mx[rc]
            cnt[node] = cnt[rc]
            smax[node] = max(mx[lc], smax[rc])

    def erase(node: int, left: int, right: int, ql: int, qr: int) -> None:
        if qr < left or right < ql:
            return
        if ql <= left and right <= qr:
            apply_zero(node, left, right)
            return
        push(node, left, right)
        mid = (left + right) // 2
        erase(node * 2, left, mid, ql, qr)
        erase(node * 2 + 1, mid + 1, right, ql, qr)
        pull(node)

    def chmin(node: int, left: int, right: int, ql: int, qr: int, value: int) -> None:
        if qr < left or right < ql or mx[node] <= value:
            return
        if ql <= left and right <= qr and smax[node] < value:
            apply_chmin(node, value)
            return
        push(node, left, right)
        mid = (left + right) // 2
        chmin(node * 2, left, mid, ql, qr, value)
        chmin(node * 2 + 1, mid + 1, right, ql, qr, value)
        pull(node)

    result = {}
    if m == 0:
        return []

    build(1, 0, m - 1)

    index = {x: i for i, x in enumerate(coords)}

    for op in ops:
        l = index[op[1]]
        r = index[op[2] + 1] - 1
        if op[0] == 0:
            erase(1, 0, m - 1, l, r)
        else:
            chmin(1, 0, m - 1, l, r, op[3])

    def collect(node: int, left: int, right: int) -> None:
        if smax[node] == -1:
            if mx[node]:
                length = coords[right + 1] - coords[left]
                result[mx[node]] = result.get(mx[node], 0) + length
            return
        push(node, left, right)
        mid = (left + right) // 2
        collect(node * 2, left, mid)
        collect(node * 2 + 1, mid + 1, right)

    collect(1, 0, m - 1)
    return [[colour, result[colour]] for colour in sorted(result)]
