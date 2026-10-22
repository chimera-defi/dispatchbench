def taller_within(a: list[int], k: int) -> list[int]:
    from collections import deque

    n = len(a)
    counts = [0] * n
    window = deque()
    taller = 0

    for i, height in enumerate(a):
        if k == 0:
            continue

        while window and window[0][0] < i - k:
            _, old_height = window.popleft()
            if old_height > height:
                taller -= 1

        counts[i] = sum(1 for _, old_height in window if old_height > height)

        window.append((i, height))

    return counts
