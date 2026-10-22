import heapq


def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    zones = len(prices)
    full = 1 << zones

    adj = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        adj[u].append((v, cost, zone))
        adj[v].append((u, cost, zone))

    station_zones = [[] for _ in range(n)]
    for stop, z in stations:
        if z not in station_zones[stop]:
            station_zones[stop].append(z)

    INF = float("inf")
    dist = [[INF] * full for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]  # (cost, node, mask)

    while heap:
        d, u, mask = heapq.heappop(heap)
        if d > dist[u][mask]:
            continue

        # Ride along an edge; zone passes already bought make the ride free.
        for v, cost, zone in adj[u]:
            if zone != -1 and (mask >> zone) & 1:
                step = 0
            else:
                step = cost
            nd = d + step
            if nd < dist[v][mask]:
                dist[v][mask] = nd
                heapq.heappush(heap, (nd, v, mask))

        # Buy a pass for a zone available at this stop.
        for z in station_zones[u]:
            if not (mask >> z) & 1:
                nmask = mask | (1 << z)
                nd = d + prices[z]
                if nd < dist[u][nmask]:
                    dist[u][nmask] = nd
                    heapq.heappush(heap, (nd, u, nmask))

    best = min(dist[n - 1])
    return -1 if best == INF else best
