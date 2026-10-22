def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)

    # Residual graph edges: [to, reverse_edge_index, capacity, cost]
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)
    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Send k units of flow, choosing minimum-cost paths in the residual graph.
    # Initial negative edges are job edges; their DAG structure permits
    # initializing potentials with shortest paths from the source.
    inf = 10**30
    potential = [inf] * n
    potential[0] = 0
    for u in range(n):
        if potential[u] == inf:
            continue
        for v, _, cap, cost in graph[u]:
            if cap and potential[v] > potential[u] + cost:
                potential[v] = potential[u] + cost
    potential = [0 if p == inf else p for p in potential]

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
                v, _, cap, cost = edge
                if cap:
                    nd = d + cost + potential[u] - potential[v]
                    if nd < dist[v]:
                        dist[v] = nd
                        prev_node[v] = u
                        prev_edge[v] = ei
                        heapq.heappush(heap, (nd, v))

        for v in range(n):
            if dist[v] < inf:
                potential[v] += dist[v]

        v = n - 1
        while v != 0:
            u = prev_node[v]
            ei = prev_edge[v]
            edge = graph[u][ei]
            total_cost += edge[3]
            edge[2] -= 1
            graph[v][edge[1]][2] += 1
            v = u

    return -total_cost


import heapq
