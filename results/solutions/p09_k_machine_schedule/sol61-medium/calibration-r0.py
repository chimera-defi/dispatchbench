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

    for u in range(n - 1):
        add_edge(u, u + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Initial shortest-path potentials, computed in time order.
    potential = [0] * n
    for u in range(n):
        for v, _, capacity, cost in graph[u]:
            if capacity and potential[u] + cost < potential[v]:
                potential[v] = potential[u] + cost

    total_cost = 0
    flow = 0
    infinity = float("inf")

    while flow < k:
        distance = [infinity] * n
        previous_node = [-1] * n
        previous_edge = [-1] * n
        distance[0] = 0
        heap = [(0, 0)]

        while heap:
            current_distance, u = heappop(heap)
            if current_distance != distance[u]:
                continue

            for edge_index, (v, _, capacity, cost) in enumerate(graph[u]):
                if capacity == 0:
                    continue
                candidate = (
                    current_distance + cost + potential[u] - potential[v]
                )
                if candidate < distance[v]:
                    distance[v] = candidate
                    previous_node[v] = u
                    previous_edge[v] = edge_index
                    heappush(heap, (candidate, v))

        for u in range(n):
            if distance[u] != infinity:
                potential[u] += distance[u]

        amount = k - flow
        v = n - 1
        while v != 0:
            u = previous_node[v]
            edge = graph[u][previous_edge[v]]
            amount = min(amount, edge[2])
            v = u

        v = n - 1
        while v != 0:
            u = previous_node[v]
            edge = graph[u][previous_edge[v]]
            edge[2] -= amount
            graph[v][edge[1]][2] += amount
            total_cost += amount * edge[3]
            v = u

        flow += amount

    return -total_cost
