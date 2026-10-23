def paint(n: int, ops: list[list[int]]) -> list[list[int]]:
    points = {1, n + 1}
    for op in ops:
        points.add(op[1])
        points.add(op[2] + 1)

    coords = sorted(points)
    index = {x: i for i, x in enumerate(coords)}
    segments = len(coords) - 1

    size = 1
    while size < segments:
        size <<= 1

    total_nodes = size << 1
    inf = 10**30

    minimum = [inf] * total_nodes
    second_minimum = [inf] * total_nodes
    minimum_weight = [0] * total_nodes
    total_weight = [0] * total_nodes
    assigned = [-1] * total_nodes

    for i in range(segments):
        node = size + i
        length = coords[i + 1] - coords[i]
        minimum[node] = 0
        minimum_weight[node] = length
        total_weight[node] = length

    def pull(node: int) -> None:
        left = node << 1
        right = left | 1

        total_weight[node] = total_weight[left] + total_weight[right]

        left_min = minimum[left]
        right_min = minimum[right]

        if left_min < right_min:
            minimum[node] = left_min
            minimum_weight[node] = minimum_weight[left]
            second_minimum[node] = min(second_minimum[left], right_min)
        elif right_min < left_min:
            minimum[node] = right_min
            minimum_weight[node] = minimum_weight[right]
            second_minimum[node] = min(left_min, second_minimum[right])
        else:
            minimum[node] = left_min
            minimum_weight[node] = (
                minimum_weight[left] + minimum_weight[right]
            )
            second_minimum[node] = min(
                second_minimum[left], second_minimum[right]
            )

    for node in range(size - 1, 0, -1):
        pull(node)

    def apply_assign(node: int, value: int) -> None:
        minimum[node] = value
        second_minimum[node] = inf
        minimum_weight[node] = total_weight[node]
        assigned[node] = value

    def apply_chmax(node: int, value: int) -> None:
        if value <= minimum[node]:
            return
        minimum[node] = value
        if assigned[node] != -1:
            assigned[node] = value

    def push(node: int) -> None:
        left = node << 1
        right = left | 1

        if assigned[node] != -1:
            value = assigned[node]
            apply_assign(left, value)
            apply_assign(right, value)
            assigned[node] = -1

        floor = minimum[node]
        if minimum[left] < floor:
            apply_chmax(left, floor)
        if minimum[right] < floor:
            apply_chmax(right, floor)

    def range_assign(
        ql: int, qr: int, value: int,
        node: int = 1, nl: int = 0, nr: int = size
    ) -> None:
        if qr <= nl or nr <= ql:
            return
        if ql <= nl and nr <= qr:
            apply_assign(node, value)
            return

        push(node)
        mid = (nl + nr) >> 1
        range_assign(ql, qr, value, node << 1, nl, mid)
        range_assign(ql, qr, value, node << 1 | 1, mid, nr)
        pull(node)

    def range_chmax(
        ql: int, qr: int, value: int,
        node: int = 1, nl: int = 0, nr: int = size
    ) -> None:
        if qr <= nl or nr <= ql or value <= minimum[node]:
            return
        if ql <= nl and nr <= qr and value < second_minimum[node]:
            apply_chmax(node, value)
            return

        push(node)
        mid = (nl + nr) >> 1
        range_chmax(ql, qr, value, node << 1, nl, mid)
        range_chmax(ql, qr, value, node << 1 | 1, mid, nr)
        pull(node)

    for op in ops:
        left = index[op[1]]
        right = index[op[2] + 1]

        if op[0] == 0:
            range_assign(left, right, 0)
        else:
            range_chmax(left, right, op[3])

    counts: dict[int, int] = {}

    def collect(node: int = 1) -> None:
        weight = total_weight[node]
        if weight == 0:
            return

        if second_minimum[node] == inf:
            colour = minimum[node]
            if colour:
                counts[colour] = counts.get(colour, 0) + weight
            return

        push(node)
        collect(node << 1)
        collect(node << 1 | 1)

    collect()
    return [[colour, counts[colour]] for colour in sorted(counts)]
