def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({time for start, end, _ in jobs for time in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    graph = [[] for _ in times]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(len(times) - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    n = len(times)
    # Initial shortest-path potentials in the forward-time DAG.
    potential = [0] * n
    for u in range(n):
        for v, _, capacity, cost in graph[u]:
            if capacity > 0 and v > u:
                potential[v] = min(potential[v], potential[u] + cost)

    total_cost = 0
    flow = 0

    while flow < k:
        dist = [float("inf")] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        dist[0] = 0
        heap = [(0, 0)]

        while heap:
            d, u = heapq.heappop(heap)
            if d != dist[u]:
                continue
            for edge_index, edge in enumerate(graph[u]):
                v, _, capacity, cost = edge
                if capacity <= 0:
                    continue
                reduced_cost = cost + potential[u] - potential[v]
                candidate = d + reduced_cost
                if candidate < dist[v]:
                    dist[v] = candidate
                    prev_node[v] = u
                    prev_edge[v] = edge_index
                    heapq.heappush(heap, (candidate, v))

        sink = n - 1
        for v in range(n):
            if dist[v] < float("inf"):
                potential[v] += dist[v]

        v = sink
        while v != 0:
            u = prev_node[v]
            edge = graph[u][prev_edge[v]]
            edge[2] -= 1
            graph[v][edge[1]][2] += 1
            total_cost += edge[3]
            v = u
        flow += 1

    return -total_cost


import heapq
