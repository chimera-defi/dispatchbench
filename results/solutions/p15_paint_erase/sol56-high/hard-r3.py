def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    from bisect import bisect_left

    points = [1, n + 1]
    for op in ops:
        points.append(op[1])
        points.append(op[2] + 1)
    points = sorted(set(points))

    segments = len(points) - 1
    size = 4 * segments + 5
    inf = 10**30

    minimum = [0] * size
    second_minimum = [inf] * size
    assignment = [0] * size

    def apply_assign(node: int, value: int) -> None:
        minimum[node] = value
        second_minimum[node] = inf
        assignment[node] = value

    def apply_raise(node: int, value: int) -> None:
        minimum[node] = value
        if assignment[node] != -1:
            assignment[node] = value

    def push(node: int) -> None:
        left = node * 2
        right = left + 1

        value = assignment[node]
        if value != -1:
            apply_assign(left, value)
            apply_assign(right, value)
            assignment[node] = -1

        floor = minimum[node]
        if minimum[left] < floor:
            apply_raise(left, floor)
        if minimum[right] < floor:
            apply_raise(right, floor)

    def pull(node: int) -> None:
        left = node * 2
        right = left + 1
        left_min = minimum[left]
        right_min = minimum[right]

        if left_min < right_min:
            minimum[node] = left_min
            second_minimum[node] = min(second_minimum[left], right_min)
        elif right_min < left_min:
            minimum[node] = right_min
            second_minimum[node] = min(second_minimum[right], left_min)
        else:
            minimum[node] = left_min
            second_minimum[node] = min(
                second_minimum[left], second_minimum[right]
            )

    def range_raise(
        node: int, lo: int, hi: int, query_lo: int, query_hi: int, value: int
    ) -> None:
        if query_hi <= lo or hi <= query_lo or value <= minimum[node]:
            return

        if query_lo <= lo and hi <= query_hi and value < second_minimum[node]:
            apply_raise(node, value)
            return

        push(node)
        mid = (lo + hi) // 2
        range_raise(node * 2, lo, mid, query_lo, query_hi, value)
        range_raise(node * 2 + 1, mid, hi, query_lo, query_hi, value)
        pull(node)

    def range_erase(
        node: int, lo: int, hi: int, query_lo: int, query_hi: int
    ) -> None:
        if query_hi <= lo or hi <= query_lo:
            return

        if query_lo <= lo and hi <= query_hi:
            apply_assign(node, 0)
            return

        push(node)
        mid = (lo + hi) // 2
        range_erase(node * 2, lo, mid, query_lo, query_hi)
        range_erase(node * 2 + 1, mid, hi, query_lo, query_hi)
        pull(node)

    for op in ops:
        left = bisect_left(points, op[1])
        right = bisect_left(points, op[2] + 1)

        if op[0] == 0:
            range_erase(1, 0, segments, left, right)
        else:
            range_raise(1, 0, segments, left, right, op[3])

    counts = {}

    def collect(node: int, lo: int, hi: int) -> None:
        if second_minimum[node] == inf:
            colour = minimum[node]
            if colour:
                counts[colour] = counts.get(colour, 0) + points[hi] - points[lo]
            return

        push(node)
        mid = (lo + hi) // 2
        collect(node * 2, lo, mid)
        collect(node * 2 + 1, mid, hi)

    collect(1, 0, segments)
    return [[colour, counts[colour]] for colour in sorted(counts)]
