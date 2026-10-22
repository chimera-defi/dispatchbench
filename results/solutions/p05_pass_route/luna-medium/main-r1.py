def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    k = len(prices)
    start_mask = [0] * n
    for stop, zone in stations:
        start_mask[stop] |= 1 << zone

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        bit = (1 << zone) if zone >= 0 else 0
        graph[u].append((v, cost, bit))
        graph[v].append((u, cost, bit))

    state_count = 1 << k
    inf = float("inf")
    dist = [[inf] * state_count for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        spent, stop, mask = heapq.heappop(heap)
        if spent != dist[stop][mask]:
            continue
        if stop == n - 1:
            return spent

        available = start_mask[stop] & ~mask
        while available:
            bit = available & -available
            available -= bit
            zone = bit.bit_length() - 1
            new_mask = mask | bit
            new_spent = spent + prices[zone]
            if new_spent < dist[stop][new_mask]:
                dist[stop][new_mask] = new_spent
                heapq.heappush(heap, (new_spent, stop, new_mask))

        for nxt, cost, bit in graph[stop]:
            ride_cost = 0 if bit and (mask & bit) else cost
            new_spent = spent + ride_cost
            if new_spent < dist[nxt][mask]:
                dist[nxt][mask] = new_spent
                heapq.heappush(heap, (new_spent, nxt, mask))

    return -1
