def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    import heapq

    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    n = len(times)

    # Min-cost flow on the timeline: sending k units from the first to
    # the last time selects a set of jobs with at most k overlaps.
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, capacity, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

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
            d, u = heapq.heappop(heap)
            if d != dist[u]:
                continue
            for ei, edge in enumerate(graph[u]):
                v, cap, cost, _ = edge
                if cap:
                    nd = d + cost + potential[u] - potential[v]
                    if nd < dist[v]:
                        dist[v] = nd
                        prev_node[v] = u
                        prev_edge[v] = ei
                        heapq.heappush(heap, (nd, v))

        for v in range(n):
            if dist[v] < float("inf"):
                potential[v] += dist[v]

        total_cost += potential[sink] - potential[source]
        v = sink
        while v != source:
            u = prev_node[v]
            edge = graph[u][prev_edge[v]]
            edge[1] -= 1
            graph[v][edge[3]][1] += 1
            v = u

    return -total_cost
