def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = {}

    for start, end in meetings:
        if start < end:
            events[start] = events.get(start, 0) + 1
            events[end] = events.get(end, 0) - 1

    active = 0
    total = 0
    previous = None

    for time in sorted(events):
        if previous is not None and active >= k:
            total += time - previous
        active += events[time]
        previous = time

    return total
