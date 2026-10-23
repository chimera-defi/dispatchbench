def overlap_minutes(meetings: list[list[int]], k: int) -> int:
    events = []

    for start, end in meetings:
        if start < end:
            events.append((start, 1))
            events.append((end, -1))

    events.sort()

    active = 0
    total = 0
    previous = None
    index = 0

    while index < len(events):
        time = events[index][0]

        if previous is not None and active >= k:
            total += time - previous

        while index < len(events) and events[index][0] == time:
            active += events[index][1]
            index += 1

        previous = time

    return total
