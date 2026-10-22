def taller_within(a: list[int], k: int) -> list[int]:
    from collections import deque

    result = [0] * len(a)
    window = deque()  # (height, index), heights in decreasing order

    for i, height in enumerate(a):
        while window and window[0][1] < i - k:
            window.popleft()

        if k > 0 and window:
            result[i] = sum(1 for h, _ in window if h > height)

        while window and window[-1][0] < height:
            window.pop()
        window.append((height, i))

    return result
