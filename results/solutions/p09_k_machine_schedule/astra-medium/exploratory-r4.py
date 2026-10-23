def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    from heapq import heappop, heappush

    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    # Each unit of flow represents one printer's schedule.
    for u in range(n - 1):
        add_edge(u, u + 1, k, 0)
    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Initial shortest-path potentials: all active edges point forward.
    inf = float("inf")
    potential = [inf] * n
    potential[0] = 0
    for u in range(n):
        for v, _, capacity, cost in graph[u]:
            if capacity:
                potential[v] = min(potential[v], potential[u] + cost)

    flow = 0
    total_cost = 0

    while flow < k:
        distance = [inf] * n
        parent = [None] * n
        distance[0] = 0
        heap = [(0, 0)]

        while heap:
            d, u = heappop(heap)
            if d != distance[u]:
                continue
            for edge_id, (v, _, capacity, cost) in enumerate(graph[u]):
                if capacity == 0:
                    continue
                nd = d + cost + potential[u] - potential[v]
                if nd < distance[v]:
                    distance[v] = nd
                    parent[v] = (u, edge_id)
                    heappush(heap, (nd, v))

        for v in range(n):
            if distance[v] != inf:
                potential[v] += distance[v]

        amount = k - flow
        v = n - 1
        while v:
            u, edge_id = parent[v]
            amount = min(amount, graph[u][edge_id][2])
            v = u

        v = n - 1
        while v:
            u, edge_id = parent[v]
            edge = graph[u][edge_id]
            total_cost += amount * edge[3]
            edge[2] -= amount
            graph[v][edge[1]][2] += amount
            v = u

        flow += amount

    return -total_cost
