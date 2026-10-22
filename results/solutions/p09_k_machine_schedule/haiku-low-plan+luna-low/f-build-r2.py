def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({time for start, end, _ in jobs for time in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    n = len(times)

    # Residual edges are [destination, reverse_edge_index, capacity, cost].
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        forward = [v, len(graph[v]), capacity, cost]
        backward = [u, len(graph[u]), 0, -cost]
        graph[u].append(forward)
        graph[v].append(backward)

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Initial shortest distances are computed in topological time order.
    # They serve as feasible potentials for Dijkstra on the residual graph.
    inf = 10**30
    potential = [inf] * n
    potential[0] = 0
    for u in range(n):
        if potential[u] == inf:
            continue
        for v, _, capacity, cost in graph[u]:
            if capacity and v > u:
                potential[v] = min(potential[v], potential[u] + cost)

    total_cost = 0
    flow = 0

    while flow < k:
        dist = [inf] * n
        previous_node = [-1] * n
        previous_edge = [-1] * n
        dist[0] = 0
        heap = [(0, 0)]

        while heap:
            current_dist, u = heapq.heappop(heap)
            if current_dist != dist[u]:
                continue
            for edge_index, edge in enumerate(graph[u]):
                v, _, capacity, cost = edge
                if capacity <= 0:
                    continue
                reduced_cost = cost + potential[u] - potential[v]
                candidate = current_dist + reduced_cost
                if candidate < dist[v]:
                    dist[v] = candidate
                    previous_node[v] = u
                    previous_edge[v] = edge_index
                    heapq.heappush(heap, (candidate, v))

        for v in range(n):
            if dist[v] < inf:
                potential[v] += dist[v]

        # The zero-cost chain guarantees a path for every unit.
        v = n - 1
        path_cost = 0
        while v != 0:
            u = previous_node[v]
            edge_index = previous_edge[v]
            edge = graph[u][edge_index]
            path_cost += edge[3]
            edge[2] -= 1
            graph[v][edge[1]][2] += 1
            v = u

        total_cost += path_cost
        flow += 1

    return -total_cost


import heapq
