def taller_within(a: list[int], k: int) -> list[int]:
    from collections import deque

    result = [0] * len(a)
    if k == 0:
        return result

    window = deque()
    for i, height in enumerate(a):
        while window and window[0] < i - k:
            window.popleft()

        result[i] = sum(1 for index in window if a[index] > height)
        window.append(i)

    return result
