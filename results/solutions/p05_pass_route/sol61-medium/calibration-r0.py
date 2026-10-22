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

    mask_count = 1 << len(prices)
    inf = float("inf")
    dist = [[inf] * mask_count for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        spent, stop, mask = heapq.heappop(heap)
        if spent != dist[stop][mask]:
            continue
        if stop == n - 1:
            return spent

        for neighbor, cost, bit in graph[stop]:
            next_spent = spent + (0 if mask & bit else cost)
            if next_spent < dist[neighbor][mask]:
                dist[neighbor][mask] = next_spent
                heapq.heappush(heap, (next_spent, neighbor, mask))

        purchasable = available[stop] & ~mask
        while purchasable:
            bit = purchasable & -purchasable
            purchasable ^= bit
            zone = bit.bit_length() - 1
            next_mask = mask | bit
            next_spent = spent + prices[zone]
            if next_spent < dist[stop][next_mask]:
                dist[stop][next_mask] = next_spent
                heapq.heappush(heap, (next_spent, stop, next_mask))

    return -1
