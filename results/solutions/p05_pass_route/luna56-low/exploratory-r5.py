def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    k = len(prices)
    station_mask = [0] * n
    for stop, zone in stations:
        station_mask[stop] |= 1 << zone

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

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

        available = station_mask[stop] & ~mask
        while available:
            bit = available & -available
            available -= bit
            zone = bit.bit_length() - 1
            new_total = total + prices[zone]
            new_mask = mask | bit
            if new_total < dist[stop][new_mask]:
                dist[stop][new_mask] = new_total
                heapq.heappush(heap, (new_total, stop, new_mask))

        for nxt, cost, zone in graph[stop]:
            ride_cost = 0 if zone >= 0 and (mask >> zone) & 1 else cost
            new_total = total + ride_cost
            if new_total < dist[nxt][mask]:
                dist[nxt][mask] = new_total
                heapq.heappush(heap, (new_total, nxt, mask))

    return -1
