def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    coords = sorted({x for op in ops for x in (op[1], op[2] + 1)})
    index = {x: i for i, x in enumerate(coords)}
    size = len(coords) - 1
    inf = 10**9 + 1

    minimum = [0] * (4 * size)
    second = [inf] * (4 * size)

    def push(node):
        left = node * 2
        right = left + 1
        value = minimum[node]

        if second[node] == inf:
            minimum[left] = minimum[right] = value
            second[left] = second[right] = inf
        else:
            if minimum[left] < value:
                minimum[left] = value
            if minimum[right] < value:
                minimum[right] = value

    def update(node, lo, hi, ql, qr, colour):
        if colour and minimum[node] >= colour:
            return

        if ql <= lo and hi <= qr:
            if colour == 0:
                minimum[node] = 0
                second[node] = inf
                return
            if colour < second[node]:
                minimum[node] = colour
                return

        push(node)
        mid = (lo + hi) // 2
        left = node * 2
        right = left + 1

        if ql < mid:
            update(left, lo, mid, ql, qr, colour)
        if qr > mid:
            update(right, mid, hi, ql, qr, colour)

        a = minimum[left]
        b = minimum[right]
        if a < b:
            minimum[node] = a
            second[node] = min(second[left], b)
        elif b < a:
            minimum[node] = b
            second[node] = min(second[right], a)
        else:
            minimum[node] = a
            second[node] = min(second[left], second[right])

    for op in ops:
        colour = op[3] if op[0] == 1 else 0
        update(1, 0, size, index[op[1]], index[op[2] + 1], colour)

    counts = {}

    def collect(node, lo, hi):
        if second[node] == inf:
            colour = minimum[node]
            if colour:
                counts[colour] = (
                    counts.get(colour, 0) + coords[hi] - coords[lo]
                )
            return

        push(node)
        mid = (lo + hi) // 2
        collect(node * 2, lo, mid)
        collect(node * 2 + 1, mid, hi)

    collect(1, 0, size)
    return [[colour, counts[colour]] for colour in sorted(counts)]
