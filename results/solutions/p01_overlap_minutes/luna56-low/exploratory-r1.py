def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = []

    for start, end in meetings:
        if start < end:
            events.append((start, 1))
            events.append((end, -1))

    if not events:
        return 0

    events.sort()

    total = 0
    active = 0
    previous = events[0][0]
    i = 0

    while i < len(events):
        time = events[i][0]

        if active >= k:
            total += time - previous

        while i < len(events) and events[i][0] == time:
            active += events[i][1]
            i += 1

        previous = time

    return total
