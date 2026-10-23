def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    coordinates = {1, n + 1}
    for op in ops:
        coordinates.add(op[1])
        coordinates.add(op[2] + 1)

    coordinates = sorted(coordinates)
    index = {x: i for i, x in enumerate(coordinates)}
    segment_count = len(coordinates) - 1

    inf = 10**30
    size = 4 * segment_count + 5
    minimum = [0] * size
    second_minimum = [inf] * size
    assignment = [0] * size

    def apply_set(node: int, value: int) -> None:
        minimum[node] = value
        second_minimum[node] = inf
        assignment[node] = value

    def apply_raise(node: int, value: int) -> None:
        if minimum[node] >= value:
            return
        minimum[node] = value
        if assignment[node] != -1:
            assignment[node] = value

    def push(node: int) -> None:
        left = node * 2
        right = left + 1

        if assignment[node] != -1:
            value = assignment[node]
            apply_set(left, value)
            apply_set(right, value)
            assignment[node] = -1

        value = minimum[node]
        if minimum[left] < value:
            apply_raise(left, value)
        if minimum[right] < value:
            apply_raise(right, value)

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

        assignment[node] = -1

    def range_set(
        node: int, start: int, end: int, query_start: int, query_end: int
    ) -> None:
        if query_end <= start or end <= query_start:
            return
        if query_start <= start and end <= query_end:
            apply_set(node, 0)
            return

        push(node)
        middle = (start + end) // 2
        range_set(node * 2, start, middle, query_start, query_end)
        range_set(node * 2 + 1, middle, end, query_start, query_end)
        pull(node)

    def range_raise(
        node: int,
        start: int,
        end: int,
        query_start: int,
        query_end: int,
        colour: int,
    ) -> None:
        if (
            query_end <= start
            or end <= query_start
            or colour <= minimum[node]
        ):
            return

        if (
            query_start <= start
            and end <= query_end
            and colour < second_minimum[node]
        ):
            apply_raise(node, colour)
            return

        push(node)
        middle = (start + end) // 2
        range_raise(
            node * 2, start, middle, query_start, query_end, colour
        )
        range_raise(
            node * 2 + 1, middle, end, query_start, query_end, colour
        )
        pull(node)

    for op in ops:
        left = index[op[1]]
        right = index[op[2] + 1]

        if op[0] == 0:
            range_set(1, 0, segment_count, left, right)
        else:
            range_raise(1, 0, segment_count, left, right, op[3])

    counts: dict[int, int] = {}

    def collect(node: int, start: int, end: int) -> None:
        if second_minimum[node] == inf:
            colour = minimum[node]
            if colour:
                length = coordinates[end] - coordinates[start]
                counts[colour] = counts.get(colour, 0) + length
            return

        push(node)
        middle = (start + end) // 2
        collect(node * 2, start, middle)
        collect(node * 2 + 1, middle, end)

    collect(1, 0, segment_count)
    return [[colour, counts[colour]] for colour in sorted(counts)]
