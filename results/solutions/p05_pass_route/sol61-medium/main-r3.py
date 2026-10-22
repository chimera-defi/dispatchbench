import heapq


def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:
    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        bit = 0 if zone == -1 else 1 << zone
        graph[u].append((v, cost, bit))
        graph[v].append((u, cost, bit))

    available = [0] * n
    for stop, zone in stations:
        available[stop] |= 1 << zone

    dist = [[float("inf")] * n for _ in range(1 << len(prices))]
    dist[0][0] = 0
    heap = [(0, 0, 0)]

    while heap:
        spent, stop, mask = heapq.heappop(heap)
        if spent != dist[mask][stop]:
            continue
        if stop == n - 1:
            return spent

        for neighbor, cost, bit in graph[stop]:
            new_spent = spent + (0 if mask & bit else cost)
            if new_spent < dist[mask][neighbor]:
                dist[mask][neighbor] = new_spent
                heapq.heappush(heap, (new_spent, neighbor, mask))

        purchasable = available[stop] & ~mask
        while purchasable:
            bit = purchasable & -purchasable
            purchasable ^= bit
            new_mask = mask | bit
            new_spent = spent + prices[bit.bit_length() - 1]
            if new_spent < dist[new_mask][stop]:
                dist[new_mask][stop] = new_spent
                heapq.heappush(heap, (new_spent, stop, new_mask))

    return -1
