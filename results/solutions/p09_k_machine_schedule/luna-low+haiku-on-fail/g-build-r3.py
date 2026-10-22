def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    import heapq

    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)

    # Residual graph edge: [destination, reverse-edge index, capacity, cost]
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Send k units from the first to the last time. Job edges have negative
    # costs, so potentials make the residual-edge costs nonnegative.
    potential = [0] * n
    total_cost = 0

    for _ in range(k):
        dist = [float("inf")] * n
        previous_node = [-1] * n
        previous_edge = [-1] * n
        dist[0] = 0
        heap = [(0, 0)]

        while heap:
            d, u = heapq.heappop(heap)
            if d != dist[u]:
                continue
            for edge_index, edge in enumerate(graph[u]):
                v, _, capacity, cost = edge
                if capacity == 0:
                    continue
                new_dist = d + cost + potential[u] - potential[v]
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    previous_node[v] = u
                    previous_edge[v] = edge_index
                    heapq.heappush(heap, (new_dist, v))

        for v in range(n):
            if dist[v] < float("inf"):
                potential[v] += dist[v]

        total_cost += potential[n - 1] - potential[0]

        v = n - 1
        while v != 0:
            u = previous_node[v]
            edge = graph[u][previous_edge[v]]
            edge[2] -= 1
            graph[v][edge[1]][2] += 1
            v = u

    return -total_cost
