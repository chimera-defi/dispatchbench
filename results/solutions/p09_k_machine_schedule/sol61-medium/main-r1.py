def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    import heapq

    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        forward = [v, len(graph[v]), capacity, cost]
        backward = [u, len(graph[u]), 0, -cost]
        graph[u].append(forward)
        graph[v].append(backward)

    # Each unit of flow represents one printer's schedule.
    for u in range(n - 1):
        add_edge(u, u + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    source, sink = 0, n - 1
    inf = float("inf")

    # Initially all usable edges go forward, so shortest paths form a DAG.
    potential = [inf] * n
    potential[source] = 0
    for u in range(n):
        for v, _, capacity, cost in graph[u]:
            if capacity and potential[u] + cost < potential[v]:
                potential[v] = potential[u] + cost

    flow = 0
    total_cost = 0

    while flow < k:
        distance = [inf] * n
        parent = [None] * n
        distance[source] = 0
        heap = [(0, source)]

        while heap:
            dist, u = heapq.heappop(heap)
            if dist != distance[u]:
                continue

            for edge_index, (v, _, capacity, cost) in enumerate(graph[u]):
                if capacity == 0:
                    continue

                new_dist = dist + cost + potential[u] - potential[v]
                if new_dist < distance[v]:
                    distance[v] = new_dist
                    parent[v] = (u, edge_index)
                    heapq.heappush(heap, (new_dist, v))

        for v in range(n):
            if distance[v] != inf:
                potential[v] += distance[v]

        amount = k - flow
        v = sink
        while v != source:
            u, edge_index = parent[v]
            amount = min(amount, graph[u][edge_index][2])
            v = u

        v = sink
        while v != source:
            u, edge_index = parent[v]
            edge = graph[u][edge_index]
            total_cost += amount * edge[3]
            edge[2] -= amount
            graph[v][edge[1]][2] += amount
            v = u

        flow += amount

    return -total_cost
