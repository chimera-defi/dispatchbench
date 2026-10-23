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
    price_by_bit = {1 << z: price for z, price in enumerate(prices)}
    dist = [[float("inf")] * mask_count for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        total, stop, mask = heapq.heappop(heap)
        if total != dist[stop][mask]:
            continue
        if stop == n - 1:
            return total

        remaining = available[stop] & ~mask
        while remaining:
            bit = remaining & -remaining
            remaining ^= bit
            new_mask = mask | bit
            new_total = total + price_by_bit[bit]
            if new_total < dist[stop][new_mask]:
                dist[stop][new_mask] = new_total
                heapq.heappush(heap, (new_total, stop, new_mask))

        for neighbor, cost, bit in graph[stop]:
            new_total = total + (0 if mask & bit else cost)
            if new_total < dist[neighbor][mask]:
                dist[neighbor][mask] = new_total
                heapq.heappush(heap, (new_total, neighbor, mask))

    return -1
