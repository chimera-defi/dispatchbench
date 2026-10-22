def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = []
    for start, end in meetings:
        if start < end:
            events.append((start, 1))
            events.append((end, -1))
    events.sort()

    total = 0
    active = 0
    prev = None
    i = 0
    n = len(events)
    while i < n:
        pos = events[i][0]
        if prev is not None and active >= k:
            total += pos - prev
        while i < n and events[i][0] == pos:
            active += events[i][1]
            i += 1
        prev = pos
    return total
