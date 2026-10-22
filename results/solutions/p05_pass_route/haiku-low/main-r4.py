import heapq


def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    zones = len(prices)
    full = 1 << zones

    adj = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        adj[u].append((v, cost, zone))
        adj[v].append((u, cost, zone))

    # Zones purchasable at each stop
    buy_here = [[] for _ in range(n)]
    for stop, zone in stations:
        buy_here[stop].append(zone)

    INF = float('inf')
    # dist[node][mask]: min spend to reach node holding the passes in mask
    dist = [[INF] * full for _ in range(n)]
    dist[0][0] = 0
    pq = [(0, 0, 0)]  # (cost, node, mask)

    while pq:
        d, u, mask = heapq.heappop(pq)
        if d > dist[u][mask]:
            continue

        # Buy a pass for any zone available at this stop
        for z in buy_here[u]:
            bit = 1 << z
            if not mask & bit:
                nmask = mask | bit
                nd = d + prices[z]
                if nd < dist[u][nmask]:
                    dist[u][nmask] = nd
                    heapq.heappush(pq, (nd, u, nmask))

        # Take a ride; free if its zone pass is already held
        for v, cost, zone in adj[u]:
            if zone >= 0 and mask & (1 << zone):
                step = 0
            else:
                step = cost
            nd = d + step
            if nd < dist[v][mask]:
                dist[v][mask] = nd
                heapq.heappush(pq, (nd, v, mask))

    best = min(dist[n - 1])
    return -1 if best == INF else best
