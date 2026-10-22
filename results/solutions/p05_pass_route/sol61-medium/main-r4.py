def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        bit = 0 if zone == -1 else 1 << zone
        graph[u].append((v, cost, bit))
        graph[v].append((u, cost, bit))

    available = [0] * n
    for stop, zone in stations:
        available[stop] |= 1 << zone

    dist = [[float("inf")] * n for _ in range(1 << len(prices))]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        spent, stop, mask = heapq.heappop(heap)
        if spent != dist[mask][stop]:
            continue
        if stop == n - 1:
            return spent

        for nxt, cost, bit in graph[stop]:
            total = spent + (0 if mask & bit else cost)
            if total < dist[mask][nxt]:
                dist[mask][nxt] = total
                heapq.heappush(heap, (total, nxt, mask))

        purchasable = available[stop] & ~mask
        while purchasable:
            bit = purchasable & -purchasable
            purchasable ^= bit
            new_mask = mask | bit
            total = spent + prices[bit.bit_length() - 1]
            if total < dist[new_mask][stop]:
                dist[new_mask][stop] = total
                heapq.heappush(heap, (total, stop, new_mask))

    return -1
