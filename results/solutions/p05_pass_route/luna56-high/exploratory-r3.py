def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    import heapq

    k = len(prices)
    masks = [0] * n
    for stop, zone in stations:
        masks[stop] |= 1 << zone

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    state_count = 1 << k
    inf = 10**30
    dist = [[inf] * state_count for _ in range(n)]
    dist[0][0] = 0

    heap = [(0, 0, 0)]

    while heap:
        total, node, mask = heapq.heappop(heap)
        if total != dist[node][mask]:
            continue
        if node == n - 1:
            return total

        available = masks[node] & ~mask
        while available:
            bit = available & -available
            available -= bit
            zone = bit.bit_length() - 1
            new_total = total + prices[zone]
            new_mask = mask | bit
            if new_total < dist[node][new_mask]:
                dist[node][new_mask] = new_total
                heapq.heappush(heap, (new_total, node, new_mask))

        for nxt, cost, zone in graph[node]:
            ride_cost = cost
            if zone >= 0 and (mask & (1 << zone)):
                ride_cost = 0

            new_total = total + ride_cost
            if new_total < dist[nxt][mask]:
                dist[nxt][mask] = new_total
                heapq.heappush(heap, (new_total, nxt, mask))

    return -1
