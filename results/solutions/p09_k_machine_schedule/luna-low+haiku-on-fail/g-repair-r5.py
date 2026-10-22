import heapq


def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    # Min-cost flow: each unit of flow represents one printer's timeline.
    # Job edges have cost -pay; timeline edges have zero cost.
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)

    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        forward = [v, capacity, cost, None]
        backward = [u, 0, -cost, forward]
        forward[3] = backward
        graph[u].append(forward)
        graph[v].append(backward)

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Initial potentials: negative edge costs exist, so Dijkstra needs valid
    # potentials up front. All original edges go from lower to higher index,
    # so a single forward pass over the nodes gives exact shortest distances.
    INF = float("inf")
    potential = [INF] * n
    potential[0] = 0
    for u in range(n):
        if potential[u] == INF:
            continue
        for edge in graph[u]:
            v, capacity, cost, _ = edge
            if capacity > 0 and potential[u] + cost < potential[v]:
                potential[v] = potential[u] + cost
    # Nodes unreachable from 0 cannot occur (timeline chain), but keep safe.
    potential = [p if p < INF else 0 for p in potential]

    total_cost = 0

    # Successive shortest augmenting paths, one unit of flow per printer.
    for _ in range(k):
        dist = [INF] * n
        prev_node = [-1] * n
        prev_edge = [None] * n
        dist[0] = 0
        heap = [(0, 0)]

        while heap:
            d, u = heapq.heappop(heap)
            if d != dist[u]:
                continue
            for edge in graph[u]:
                v, capacity, cost, _ = edge
                if capacity:
                    nd = d + cost + potential[u] - potential[v]
                    if nd < dist[v]:
                        dist[v] = nd
                        prev_node[v] = u
                        prev_edge[v] = edge
                        heapq.heappush(heap, (nd, v))

        for v in range(n):
            if dist[v] < INF:
                potential[v] += dist[v]

        v = n - 1
        while v != 0:
            edge = prev_edge[v]
            edge[1] -= 1
            edge[3][1] += 1
            total_cost += edge[2]
            v = prev_node[v]

    return -total_cost
