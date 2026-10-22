import heapq


def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    zones = len(prices)
    full = 1 << zones

    # Adjacency list: adj[u] = list of (v, cost, zone)
    adj = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        adj[u].append((v, cost, zone))
        adj[v].append((u, cost, zone))

    # Zones purchasable at each stop
    buyable = [[] for _ in range(n)]
    for stop, z in stations:
        buyable[stop].append(z)

    INF = float("inf")
    dist = [[INF] * full for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]  # (cost, node, mask)

    while heap:
        d, u, mask = heapq.heappop(heap)
        if d > dist[u][mask]:
            continue

        # Buy a pass at this stop
        for z in buyable[u]:
            bit = 1 << z
            if not mask & bit:
                nmask = mask | bit
                nd = d + prices[z]
                if nd < dist[u][nmask]:
                    dist[u][nmask] = nd
                    heapq.heappush(heap, (nd, u, nmask))

        # Ride along an edge
        for v, cost, zone in adj[u]:
            if zone != -1 and mask & (1 << zone):
                step = 0
            else:
                step = cost
            nd = d + step
            if nd < dist[v][mask]:
                dist[v][mask] = nd
                heapq.heappush(heap, (nd, v, mask))

    best = min(dist[n - 1])
    return -1 if best == INF else best
