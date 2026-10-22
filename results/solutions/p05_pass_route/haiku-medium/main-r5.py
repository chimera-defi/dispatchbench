import heapq


def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    zones = len(prices)
    full = 1 << zones

    adj = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        adj[u].append((v, cost, zone))
        adj[v].append((u, cost, zone))

    # stop_zones[s] is a bitmask of zones whose pass can be bought at stop s
    stop_zones = [0] * n
    for stop, zone in stations:
        stop_zones[stop] |= 1 << zone

    INF = float("inf")
    # State is (stop, mask of passes already bought), flattened as stop * full + mask
    dist = [INF] * (n * full)
    dist[0] = 0
    heap = [(0, 0, 0)]  # (cost, stop, mask)

    while heap:
        d, node, mask = heapq.heappop(heap)
        if d > dist[node * full + mask]:
            continue

        # Ride to an adjacent stop
        for nxt, cost, zone in adj[node]:
            if zone >= 0 and (mask >> zone) & 1:
                step = 0
            else:
                step = cost
            nd = d + step
            idx = nxt * full + mask
            if nd < dist[idx]:
                dist[idx] = nd
                heapq.heappush(heap, (nd, nxt, mask))

        # Buy an unowned pass available at this stop
        available = stop_zones[node] & ~mask
        for zone in range(zones):
            if (available >> zone) & 1:
                nmask = mask | (1 << zone)
                nd = d + prices[zone]
                idx = node * full + nmask
                if nd < dist[idx]:
                    dist[idx] = nd
                    heapq.heappush(heap, (nd, node, nmask))

    best = min(dist[(n - 1) * full + mask] for mask in range(full))
    return -1 if best == INF else best
