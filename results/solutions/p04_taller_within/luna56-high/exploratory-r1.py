def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if k == 0:
        return [0] * n

    values = {x: i + 1 for i, x in enumerate(sorted(set(a)))}
    size = len(values)
    bit = [0] * (size + 1)

    def update(i: int, delta: int) -> None:
        while i <= size:
            bit[i] += delta
            i += i & -i

    def prefix(i: int) -> int:
        total = 0
        while i:
            total += bit[i]
            i -= i & -i
        return total

    result = []
    active = 0

    for i, x in enumerate(a):
        old = i - k - 1
        if old >= 0:
            update(values[a[old]], -1)
            active -= 1

        rank = values[x]
        result.append(active - prefix(rank))

        update(rank, 1)
        active += 1

    return result
