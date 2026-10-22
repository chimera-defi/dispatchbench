import heapq


def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    adj = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        adj[u].append((v, cost, zone))
        adj[v].append((u, cost, zone))

    buy = [[] for _ in range(n)]
    for stop, zone in stations:
        buy[stop].append(zone)

    full = 1 << len(prices)
    INF = 10 ** 18
    dist = [[INF] * full for _ in range(n)]
    dist[0][0] = 0
    pq = [(0, 0, 0)]  # (cost, stop, mask of purchased passes)

    while pq:
        d, u, m = heapq.heappop(pq)
        if d > dist[u][m]:
            continue
        if u == n - 1:
            return d

        # Buy a pass for a zone available at this stop.
        for z in buy[u]:
            if not (m >> z) & 1:
                nm = m | (1 << z)
                nd = d + prices[z]
                if nd < dist[u][nm]:
                    dist[u][nm] = nd
                    heapq.heappush(pq, (nd, u, nm))

        # Ride to a neighbouring stop, free if its zone pass is held.
        for v, cost, zone in adj[u]:
            if zone >= 0 and (m >> zone) & 1:
                nd = d
            else:
                nd = d + cost
            if nd < dist[v][m]:
                dist[v][m] = nd
                heapq.heappush(pq, (nd, v, m))

    return -1
