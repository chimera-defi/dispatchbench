from heapq import heappop, heappush


def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for u in range(n - 1):
        add_edge(u, u + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Initial shortest distances in the forward-only DAG.
    potential = [0] * n
    for u in range(n):
        for v, _, capacity, cost in graph[u]:
            if capacity and potential[v] > potential[u] + cost:
                potential[v] = potential[u] + cost

    total_cost = 0
    remaining = k
    infinity = 10**30

    while remaining:
        distance = [infinity] * n
        parent = [None] * n
        distance[0] = 0
        heap = [(0, 0)]

        while heap:
            dist_u, u = heappop(heap)
            if dist_u != distance[u]:
                continue

            for edge_index, (v, _, capacity, cost) in enumerate(graph[u]):
                if not capacity:
                    continue
                candidate = dist_u + cost + potential[u] - potential[v]
                if candidate < distance[v]:
                    distance[v] = candidate
                    parent[v] = (u, edge_index)
                    heappush(heap, (candidate, v))

        for v in range(n):
            if distance[v] < infinity:
                potential[v] += distance[v]

        amount = remaining
        v = n - 1
        while v:
            u, edge_index = parent[v]
            amount = min(amount, graph[u][edge_index][2])
            v = u

        v = n - 1
        while v:
            u, edge_index = parent[v]
            edge = graph[u][edge_index]
            total_cost += amount * edge[3]
            edge[2] -= amount
            graph[v][edge[1]][2] += amount
            v = u

        remaining -= amount

    return -total_cost
