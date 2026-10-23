def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    k = len(prices)
    graph = [[] for _ in range(n)]

    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    station_masks = [0] * n
    for stop, zone in stations:
        station_masks[stop] |= 1 << zone

    inf = 10**30
    dist = [[inf] * (1 << k) for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        total, stop, mask = heapq.heappop(heap)
        if total != dist[stop][mask]:
            continue
        if stop == n - 1:
            return total

        available = station_masks[stop] & ~mask
        while available:
            bit = available & -available
            zone = bit.bit_length() - 1
            new_total = total + prices[zone]
            new_mask = mask | bit
            if new_total < dist[stop][new_mask]:
                dist[stop][new_mask] = new_total
                heapq.heappush(heap, (new_total, stop, new_mask))
            available -= bit

        for nxt, cost, zone in graph[stop]:
            ride_cost = 0 if zone >= 0 and (mask & (1 << zone)) else cost
            new_total = total + ride_cost
            if new_total < dist[nxt][mask]:
                dist[nxt][mask] = new_total
                heapq.heappush(heap, (new_total, nxt, mask))

    return -1
