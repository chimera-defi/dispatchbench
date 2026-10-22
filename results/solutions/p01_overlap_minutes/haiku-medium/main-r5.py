def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    deltas = {}
    for start, end in meetings:
        if start == end:
            continue
        deltas[start] = deltas.get(start, 0) + 1
        deltas[end] = deltas.get(end, 0) - 1

    total = 0
    count = 0
    times = sorted(deltas)
    for i, t in enumerate(times):
        count += deltas[t]
        if i + 1 < len(times) and count >= k:
            total += times[i + 1] - t
    return total
