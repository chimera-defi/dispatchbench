def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    zone_count = len(prices)
    station_masks = [0] * n
    for stop, zone in stations:
        station_masks[stop] |= 1 << zone

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        bit = 0 if zone == -1 else 1 << zone
        graph[u].append((v, cost, bit))
        graph[v].append((u, cost, bit))

    inf = 10**30
    dist = [[inf] * (1 << zone_count) for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        amount, stop, mask = heapq.heappop(heap)
        if amount != dist[stop][mask]:
            continue
        if stop == n - 1:
            return amount

        available = station_masks[stop] & ~mask
        while available:
            bit = available & -available
            available -= bit
            zone = bit.bit_length() - 1
            new_amount = amount + prices[zone]
            new_mask = mask | bit
            if new_amount < dist[stop][new_mask]:
                dist[stop][new_mask] = new_amount
                heapq.heappush(heap, (new_amount, stop, new_mask))

        for nxt, cost, zone_bit in graph[stop]:
            ride_cost = 0 if zone_bit and (mask & zone_bit) else cost
            new_amount = amount + ride_cost
            if new_amount < dist[nxt][mask]:
                dist[nxt][mask] = new_amount
                heapq.heappush(heap, (new_amount, nxt, mask))

    return -1
