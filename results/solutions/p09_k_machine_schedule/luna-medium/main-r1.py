def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    from heapq import heappush, heappop

    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)

    # Residual graph edges: [destination, reverse_edge_index, capacity, cost]
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Successive shortest augmenting paths with reduced costs.
    potential = [0] * n
    total_cost = 0
    source, sink = 0, n - 1

    for _ in range(k):
        dist = [float("inf")] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        dist[source] = 0
        heap = [(0, source)]

        while heap:
            d, u = heappop(heap)
            if d != dist[u]:
                continue
            for ei, edge in enumerate(graph[u]):
                v, _, capacity, cost = edge
                if capacity == 0:
                    continue
                nd = d + cost + potential[u] - potential[v]
                if nd < dist[v]:
                    dist[v] = nd
                    prev_node[v] = u
                    prev_edge[v] = ei
                    heappush(heap, (nd, v))

        if dist[sink] == float("inf"):
            break

        for v in range(n):
            if dist[v] < float("inf"):
                potential[v] += dist[v]

        if potential[sink] >= 0:
            break

        total_cost += potential[sink]
        v = sink
        while v != source:
            u = prev_node[v]
            ei = prev_edge[v]
            edge = graph[u][ei]
            edge[2] -= 1
            graph[v][edge[1]][2] += 1
            v = u

    return -total_cost
