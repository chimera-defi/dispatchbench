def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    import heapq

    if not jobs:
        return 0

    times = sorted({time for start, end, _ in jobs for time in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    n = len(times)

    # Residual graph edges: [destination, reverse-edge index, capacity, cost]
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Send k units of flow from the first to the last time point.
    # Initial negative costs are on forward job edges, so initialize
    # feasible potentials with shortest paths in this DAG.
    inf = 10**30
    potential = [inf] * n
    potential[0] = 0
    for u in range(n):
        if potential[u] == inf:
            continue
        for v, _, capacity, cost in graph[u]:
            if capacity and v > u:
                potential[v] = min(potential[v], potential[u] + cost)
    potential = [0 if value == inf else value for value in potential]

    total_cost = 0
    for _ in range(k):
        dist = [inf] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        dist[0] = 0
        heap = [(0, 0)]

        while heap:
            d, u = heapq.heappop(heap)
            if d != dist[u]:
                continue
            for ei, edge in enumerate(graph[u]):
                v, _, capacity, cost = edge
                if capacity == 0:
                    continue
                reduced_cost = cost + potential[u] - potential[v]
                nd = d + reduced_cost
                if nd < dist[v]:
                    dist[v] = nd
                    prev_node[v] = u
                    prev_edge[v] = ei
                    heapq.heappush(heap, (nd, v))

        for v in range(n):
            if dist[v] < inf:
                potential[v] += dist[v]

        v = n - 1
        path_cost = 0
        while v != 0:
            u = prev_node[v]
            ei = prev_edge[v]
            edge = graph[u][ei]
            path_cost += edge[3] if len(edge) > 3 else 0
            edge[2] -= 1
            graph[v][edge[1]][2] += 1
            v = u

        total_cost += path_cost

    return -total_cost
