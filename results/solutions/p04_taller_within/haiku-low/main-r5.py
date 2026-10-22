from collections import deque


def taller_within(a: list[int], k: int) -> list[int]:
    n = len(a)
    if n == 0:
        return []
    # Sliding window of the last k values (indices i-k..i-1), kept in
    # decreasing order so the front of the deque is the window maximum-ish
    # structure; we need the count of elements > a[i], so use a Fenwick
    # tree over coordinate-compressed values instead.
    vals = sorted(set(a))
    rank = {v: idx + 1 for idx, v in enumerate(vals)}
    m = len(vals)
    tree = [0] * (m + 1)

    def add(p: int, d: int) -> None:
        while p <= m:
            tree[p] += d
            p += p & -p

    def prefix(p: int) -> int:
        s = 0
        while p > 0:
            s += tree[p]
            p -= p & -p
        return s

    result = [0] * n
    window = deque()
    total = 0
    for i in range(n):
        if k == 0:
            result[i] = 0
        else:
            # Count window elements strictly greater than a[i]
            result[i] = total - prefix(rank[a[i]])
        window.append(a[i])
        add(rank[a[i]], 1)
        total += 1
        if len(window) > k:
            old = window.popleft()
            add(rank[old], -1)
            total -= 1
    return result
