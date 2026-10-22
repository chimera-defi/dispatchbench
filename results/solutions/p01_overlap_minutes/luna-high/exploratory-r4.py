def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = []
    for start, end in meetings:
        if start < end:
            events.append((start, 1))
            events.append((end, -1))

    events.sort()
    active = 0
    total = 0
    i = 0

    while i < len(events):
        time = events[i][0]
        delta = 0
        while i < len(events) and events[i][0] == time:
            delta += events[i][1]
            i += 1

        active += delta
        if i < len(events) and active >= k:
            total += events[i][0] - time

    return total
