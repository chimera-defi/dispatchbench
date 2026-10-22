def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    from heapq import heappop, heappush

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        bit = 0 if zone == -1 else 1 << zone
        graph[u].append((v, cost, bit))
        graph[v].append((u, cost, bit))

    available = [0] * n
    for stop, zone in stations:
        available[stop] |= 1 << zone

    mask_count = 1 << len(prices)
    dist = [[float("inf")] * mask_count for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        spent, stop, mask = heappop(heap)
        if spent != dist[stop][mask]:
            continue
        if stop == n - 1:
            return spent

        remaining = available[stop] & ~mask
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            new_mask = mask | bit
            new_spent = spent + prices[bit.bit_length() - 1]
            if new_spent < dist[stop][new_mask]:
                dist[stop][new_mask] = new_spent
                heappush(heap, (new_spent, stop, new_mask))

        for neighbor, cost, bit in graph[stop]:
            new_spent = spent + (0 if mask & bit else cost)
            if new_spent < dist[neighbor][mask]:
                dist[neighbor][mask] = new_spent
                heappush(heap, (new_spent, neighbor, mask))

    return -1
