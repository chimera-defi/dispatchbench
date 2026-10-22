def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    import heapq

    if not jobs:
        return 0

    times = sorted({time for start, end, _ in jobs for time in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    n = len(times)

    # Residual graph edges: [to, reverse_edge_index, capacity, cost]
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Send k units of flow from the earliest to the latest time.
    # Potentials make reduced edge costs nonnegative for Dijkstra.
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
            d, u = heapq.heappop(heap)
            if d != dist[u]:
                continue
            for edge_idx, edge in enumerate(graph[u]):
                v, _, capacity, cost = edge
                if capacity == 0:
                    continue
                new_dist = d + cost + potential[u] - potential[v]
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    prev_node[v] = u
                    prev_edge[v] = edge_idx
                    heapq.heappush(heap, (new_dist, v))

        for v in range(n):
            if dist[v] < float("inf"):
                potential[v] += dist[v]

        v = sink
        while v != source:
            u = prev_node[v]
            edge_idx = prev_edge[v]
            edge = graph[u][edge_idx]
            edge[2] -= 1
            graph[v][edge[1]][2] += 1
            total_cost += edge[3]
            v = u

    return -total_cost
