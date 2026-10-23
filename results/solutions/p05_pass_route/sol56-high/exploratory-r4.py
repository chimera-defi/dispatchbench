from heapq import heappop, heappush


def pass_route(
    n: int,
    edges: list[list[int]],
    stations: list[list[int]],
    prices: list[int],
) -> int:
    zone_count = len(prices)
    state_count = 1 << zone_count

    graph = [[] for _ in range(n)]
    for u, v, cost, zone in edges:
        graph[u].append((v, cost, zone))
        graph[v].append((u, cost, zone))

    available = [0] * n
    for stop, zone in stations:
        available[stop] |= 1 << zone

    inf = float("inf")
    dist = [[inf] * state_count for _ in range(n)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]  # (total cost, stop, purchased-zone mask)

    while heap:
        total, stop, mask = heappop(heap)
        if total != dist[stop][mask]:
            continue
        if stop == n - 1:
            return total

        purchasable = available[stop] & ~mask
        while purchasable:
            bit = purchasable & -purchasable
            zone = bit.bit_length() - 1
            new_mask = mask | bit
            new_total = total + prices[zone]
            if new_total < dist[stop][new_mask]:
                dist[stop][new_mask] = new_total
                heappush(heap, (new_total, stop, new_mask))
            purchasable ^= bit

        for neighbor, ride_cost, zone in graph[stop]:
            if zone != -1 and (mask & (1 << zone)):
                new_total = total
            else:
                new_total = total + ride_cost

            if new_total < dist[neighbor][mask]:
                dist[neighbor][mask] = new_total
                heappush(heap, (new_total, neighbor, mask))

    return -1
