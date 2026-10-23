def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    adjacency = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        bit = 0 if zone == -1 else 1 << zone
        adjacency[u].append((v, cost, bit))
        adjacency[v].append((u, cost, bit))

    available = [0] * n
    for stop, zone in stations:
        available[stop] |= 1 << zone

    mask_count = 1 << len(prices)
    bit_prices = {1 << z: price for z, price in enumerate(prices)}
    dist = [[float("inf")] * mask_count for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        spent, stop, mask = heapq.heappop(heap)
        if spent != dist[stop][mask]:
            continue
        if stop == n - 1:
            return spent

        purchasable = available[stop] & ~mask
        while purchasable:
            bit = purchasable & -purchasable
            purchasable ^= bit
            new_mask = mask | bit
            new_spent = spent + bit_prices[bit]
            if new_spent < dist[stop][new_mask]:
                dist[stop][new_mask] = new_spent
                heapq.heappush(heap, (new_spent, stop, new_mask))

        for neighbor, cost, bit in adjacency[stop]:
            new_spent = spent + (0 if mask & bit else cost)
            if new_spent < dist[neighbor][mask]:
                dist[neighbor][mask] = new_spent
                heapq.heappush(heap, (new_spent, neighbor, mask))

    return -1
