import heapq


def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    k = len(prices)
    full = 1 << k

    adj = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        bit = (1 << zone) if zone != -1 else 0
        adj[u].append((v, cost, bit))
        adj[v].append((u, cost, bit))

    station_zones = [[] for _ in range(n)]
    for stop, z in stations:
        station_zones[stop].append(z)

    INF = float("inf")
    dist = [[INF] * full for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]  # (cost, node, mask)

    while heap:
        d, u, mask = heapq.heappop(heap)
        if d > dist[u][mask]:
            continue

        # Buy any available pass at this stop
        for z in station_zones[u]:
            bit = 1 << z
            if not mask & bit:
                nd = d + prices[z]
                nm = mask | bit
                if nd < dist[u][nm]:
                    dist[u][nm] = nd
                    heapq.heappush(heap, (nd, u, nm))

        # Ride along edges
        for v, cost, bit in adj[u]:
            nd = d if (bit and mask & bit) else d + cost
            if nd < dist[v][mask]:
                dist[v][mask] = nd
                heapq.heappush(heap, (nd, v, mask))

    best = min(dist[n - 1])
    return -1 if best == INF else best
