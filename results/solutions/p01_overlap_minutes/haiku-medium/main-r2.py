def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    delta = {}
    for start, end in meetings:
        if start == end:
            continue
        delta[start] = delta.get(start, 0) + 1
        delta[end] = delta.get(end, 0) - 1

    total = 0
    count = 0
    coords = sorted(delta)
    for i, t in enumerate(coords):
        count += delta[t]
        if count >= k and i + 1 < len(coords):
            total += coords[i + 1] - t
    return total
