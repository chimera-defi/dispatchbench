def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = []
    for start, end in meetings:
        if start < end:
            events.append((start, 1))
            events.append((end, -1))

    events.sort()

    total = 0
    active = 0
    previous = None
    i = 0

    while i < len(events):
        time = events[i][0]
        if previous is not None and active >= k:
            total += time - previous

        delta = 0
        while i < len(events) and events[i][0] == time:
            delta += events[i][1]
            i += 1

        active += delta
        previous = time

    return total
