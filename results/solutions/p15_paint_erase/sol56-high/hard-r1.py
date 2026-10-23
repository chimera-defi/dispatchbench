def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    points = {1, n + 1}
    for op in ops:
        points.add(op[1])
        points.add(op[2] + 1)

    coords = sorted(points)
    index = {x: i for i, x in enumerate(coords)}
    segments = len(coords) - 1

    inf = 10**30
    size = 4 * segments + 5
    minimum = [0] * size
    second_minimum = [inf] * size
    assigned = [0] * size

    def apply_set(node: int, value: int) -> None:
        minimum[node] = value
        second_minimum[node] = inf
        assigned[node] = value

    def apply_chmax(node: int, value: int) -> None:
        if value <= minimum[node]:
            return
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

        floor = minimum[node]
        if minimum[left] < floor:
            apply_chmax(left, floor)
        if minimum[right] < floor:
            apply_chmax(right, floor)

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
                second_minimum[left],
                second_minimum[right],
            )

        assigned[node] = -1

    def range_set(
        node: int,
        start: int,
        end: int,
        query_left: int,
        query_right: int,
    ) -> None:
        if query_left <= start and end <= query_right:
            apply_set(node, 0)
            return

        push(node)
        middle = (start + end) // 2

        if query_left <= middle:
            range_set(node * 2, start, middle, query_left, query_right)
        if query_right > middle:
            range_set(node * 2 + 1, middle + 1, end, query_left, query_right)

        pull(node)

    def range_chmax(
        node: int,
        start: int,
        end: int,
        query_left: int,
        query_right: int,
        colour: int,
    ) -> None:
        if colour <= minimum[node]:
            return

        if (
            query_left <= start
            and end <= query_right
            and colour < second_minimum[node]
        ):
            apply_chmax(node, colour)
            return

        push(node)
        middle = (start + end) // 2

        if query_left <= middle:
            range_chmax(
                node * 2,
                start,
                middle,
                query_left,
                query_right,
                colour,
            )
        if query_right > middle:
            range_chmax(
                node * 2 + 1,
                middle + 1,
                end,
                query_left,
                query_right,
                colour,
            )

        pull(node)

    for op in ops:
        left = index[op[1]]
        right = index[op[2] + 1] - 1

        if op[0] == 0:
            range_set(1, 0, segments - 1, left, right)
        else:
            range_chmax(1, 0, segments - 1, left, right, op[3])

    counts = {}

    def collect(node: int, start: int, end: int) -> None:
        if second_minimum[node] == inf:
            colour = minimum[node]
            if colour:
                length = coords[end + 1] - coords[start]
                counts[colour] = counts.get(colour, 0) + length
            return

        push(node)
        middle = (start + end) // 2
        collect(node * 2, start, middle)
        collect(node * 2 + 1, middle + 1, end)

    collect(1, 0, segments - 1)
    return [[colour, counts[colour]] for colour in sorted(counts)]
