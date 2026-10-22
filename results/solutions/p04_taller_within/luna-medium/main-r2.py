def taller_within(a: list[int], k: int) -> list[int]:
    from collections import deque

    window = deque()
    counts = []
    for i, height in enumerate(a):
        while window and window[0] < i - k:
            window.popleft()

        counts.append(sum(1 for j in window if a[j] > height))
        window.append(i)

    return counts
