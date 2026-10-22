def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = []
    for start, end in meetings:
        if start < end:
            events.append((start, 1))
            events.append((end, -1))
    events.sort()

    total = 0
    active = 0
    prev = 0
    for time, delta in events:
        if active >= k:
            total += time - prev
        active += delta
        prev = time
    return total
