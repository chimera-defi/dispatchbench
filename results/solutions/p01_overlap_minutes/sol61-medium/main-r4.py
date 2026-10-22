def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    if k > len(meetings):
        return 0

    events = {}
    for start, end in meetings:
        if start < end:
            events[start] = events.get(start, 0) + 1
            events[end] = events.get(end, 0) - 1

    total = 0
    active = 0
    previous = 0

    for time in sorted(events):
        if active >= k:
            total += time - previous
        active += events[time]
        previous = time

    return total
