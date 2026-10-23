def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    coordinates = {1, n + 1}
    for op in ops:
        coordinates.add(op[1])
        coordinates.add(op[2] + 1)

    xs = sorted(coordinates)
    index = {x: i for i, x in enumerate(xs)}
    size = len(xs) - 1

    inf = 10**30
    tree_size = 4 * size + 5
    minimum = [0] * tree_size
    second_minimum = [inf] * tree_size
    assigned = [-1] * tree_size

    def apply_set(node: int, value: int) -> None:
        minimum[node] = value
        second_minimum[node] = inf
        assigned[node] = value

    def apply_chmax(node: int, value: int) -> None:
        minimum[node] = value
        if assigned[node] != -1:
            assigned[node] = value

    def push(node: int) -> None:
        left = node * 2
        right = left + 1

        if assigned[node] != -1:
            value = assigned[node]
            apply_set(left, value)
            apply_set(right, value)
            assigned[node] = -1

        value = minimum[node]
        if minimum[left] < value:
            apply_chmax(left, value)
        if minimum[right] < value:
            apply_chmax(right, value)

    def pull(node: int) -> None:
        left = node * 2
        right = left + 1
        left_min = minimum[left]
        right_min = minimum[right]

        if left_min == right_min:
            minimum[node] = left_min
            second_minimum[node] = min(
                second_minimum[left], second_minimum[right]
            )
        elif left_min < right_min:
            minimum[node] = left_min
            second_minimum[node] = min(second_minimum[left], right_min)
        else:
            minimum[node] = right_min
            second_minimum[node] = min(left_min, second_minimum[right])

    def range_set(
        node: int, lo: int, hi: int, query_lo: int, query_hi: int
    ) -> None:
        if query_lo <= lo and hi <= query_hi:
            apply_set(node, 0)
            return

        push(node)
        mid = (lo + hi) // 2
        if query_lo <= mid:
            range_set(node * 2, lo, mid, query_lo, query_hi)
        if query_hi > mid:
            range_set(node * 2 + 1, mid + 1, hi, query_lo, query_hi)
        pull(node)

    def range_chmax(
        node: int,
        lo: int,
        hi: int,
        query_lo: int,
        query_hi: int,
        value: int,
    ) -> None:
        if value <= minimum[node]:
            return
        if query_lo <= lo and hi <= query_hi and value < second_minimum[node]:
            apply_chmax(node, value)
            return

        push(node)
        mid = (lo + hi) // 2
        if query_lo <= mid:
            range_chmax(node * 2, lo, mid, query_lo, query_hi, value)
        if query_hi > mid:
            range_chmax(
                node * 2 + 1, mid + 1, hi, query_lo, query_hi, value
            )
        pull(node)

    for op in ops:
        left = index[op[1]]
        right = index[op[2] + 1] - 1

        if op[0] == 0:
            range_set(1, 0, size - 1, left, right)
        else:
            range_chmax(1, 0, size - 1, left, right, op[3])

    counts: dict[int, int] = {}

    def collect(node: int, lo: int, hi: int) -> None:
        if second_minimum[node] == inf:
            colour = minimum[node]
            if colour:
                counts[colour] = counts.get(colour, 0) + xs[hi + 1] - xs[lo]
            return

        push(node)
        mid = (lo + hi) // 2
        collect(node * 2, lo, mid)
        collect(node * 2 + 1, mid + 1, hi)

    collect(1, 0, size - 1)
    return [[colour, counts[colour]] for colour in sorted(counts)]
