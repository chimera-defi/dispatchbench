def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = {}
    for start, end in meetings:
        if start == end:
            continue
        events[start] = events.get(start, 0) + 1
        events[end] = events.get(end, 0) - 1

    total = 0
    active = 0
    prev = None
    for t in sorted(events):
        if prev is not None and active >= k:
            total += t - prev
        active += events[t]
        prev = t
    return total
