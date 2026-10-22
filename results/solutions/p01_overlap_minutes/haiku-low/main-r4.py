def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = []
    for start, end in meetings:
        if start < end:
            events.append((start, 1))
            events.append((end, -1))
    # At the same timestamp, process ends (-1) before starts (+1)
    # so that touching meetings do not count as overlapping.
    events.sort(key=lambda e: (e[0], e[1]))

    total = 0
    active = 0
    prev = 0
    for time, delta in events:
        if active >= k:
            total += time - prev
        active += delta
        prev = time
    return total
