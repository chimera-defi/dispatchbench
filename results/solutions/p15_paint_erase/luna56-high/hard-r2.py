def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    from bisect import bisect_left

    points = [1, n + 1]
    for op in ops:
        points.append(op[1])
        points.append(op[2] + 1)

    coords = sorted(set(points))
    m = len(coords) - 1
    pos = {x: i for i, x in enumerate(coords)}

    size = 4 * m + 5
    INF = 10**19

    minimum = [0] * size
    second = [INF] * size
    count = [0] * size
    lazy = [-1] * size

    def build(node: int, left: int, right: int) -> None:
        count[node] = right - left + 1
        if left != right:
            mid = (left + right) // 2
            build(node * 2, left, mid)
            build(node * 2 + 1, mid + 1, right)

    def apply_raise(node: int, value: int) -> None:
        if value <= minimum[node]:
            return

        minimum[node] = value
        if lazy[node] != -1:
            lazy[node] = value
        elif second[node] == INF:
            lazy[node] = value

    def push(node: int) -> None:
        left = node * 2
        right = left + 1

        if lazy[node] != -1:
            value = lazy[node]

            minimum[left] = value
            second[left] = INF
            lazy[left] = value

            minimum[right] = value
            second[right] = INF
            lazy[right] = value

            lazy[node] = -1

        if minimum[left] < minimum[node]:
            apply_raise(left, minimum[node])
        if minimum[right] < minimum[node]:
            apply_raise(right, minimum[node])

    def pull(node: int) -> None:
        left = node * 2
        right = left + 1
        lazy[node] = -1

        if minimum[left] < minimum[right]:
            minimum[node] = minimum[left]
            count[node] = count[left]
            second[node] = min(second[left], minimum[right])
        elif minimum[left] > minimum[right]:
            minimum[node] = minimum[right]
            count[node] = count[right]
            second[node] = min(minimum[left], second[right])
        else:
            minimum[node] = minimum[left]
            count[node] = count[left] + count[right]
            second[node] = min(second[left], second[right])

    def raise_range(
        node: int,
        left: int,
        right: int,
        query_left: int,
        query_right: int,
        value: int,
    ) -> None:
        if query_right < left or right < query_left or value <= minimum[node]:
            return

        if query_left <= left and right <= query_right and value < second[node]:
            apply_raise(node, value)
            return

        push(node)
        mid = (left + right) // 2
        raise_range(node * 2, left, mid, query_left, query_right, value)
        raise_range(node * 2 + 1, mid + 1, right, query_left, query_right, value)
        pull(node)

    def clear_range(
        node: int,
        left: int,
        right: int,
        query_left: int,
        query_right: int,
    ) -> None:
        if query_right < left or right < query_left:
            return

        if query_left <= left and right <= query_right:
            minimum[node] = 0
            second[node] = INF
            lazy[node] = 0
            return

        push(node)
        mid = (left + right) // 2
        clear_range(node * 2, left, mid, query_left, query_right)
        clear_range(node * 2 + 1, mid + 1, right, query_left, query_right)
        pull(node)

    build(1, 0, m - 1)

    for op in ops:
        left = pos[op[1]]
        right = pos[op[2] + 1] - 1

        if op[0] == 0:
            clear_range(1, 0, m - 1, left, right)
        else:
            raise_range(1, 0, m - 1, left, right, op[3])

    result = {}

    def collect(node: int, left: int, right: int) -> None:
        if second[node] == INF:
            value = minimum[node]
            if value:
                result[value] = result.get(value, 0) + coords[right + 1] - coords[left]
            return

        push(node)
        mid = (left + right) // 2
        collect(node * 2, left, mid)
        collect(node * 2 + 1, mid + 1, right)

    collect(1, 0, m - 1)
    return [[color, result[color]] for color in sorted(result)]
