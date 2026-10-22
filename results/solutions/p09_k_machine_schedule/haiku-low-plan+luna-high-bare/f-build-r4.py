import heapq


def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({time for start, end, _ in jobs for time in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, capacity, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Initial shortest-path potentials; all original edges point forward.
    inf = float("inf")
    potential = [inf] * n
    potential[0] = 0
    for u in range(n):
        for v, capacity, cost, _ in graph[u]:
            if capacity and v > u:
                potential[v] = min(potential[v], potential[u] + cost)

    total_cost = 0
    source, sink = 0, n - 1

    for _ in range(k):
        dist = [inf] * n
        parent_node = [-1] * n
        parent_edge = [-1] * n
        dist[source] = 0
        heap = [(0, source)]

        while heap:
            d, u = heapq.heappop(heap)
            if d != dist[u]:
                continue
            for edge_i, (v, capacity, cost, _) in enumerate(graph[u]):
                if capacity <= 0:
                    continue
                reduced_cost = cost + potential[u] - potential[v]
                candidate = d + reduced_cost
                if candidate < dist[v]:
                    dist[v] = candidate
                    parent_node[v] = u
                    parent_edge[v] = edge_i
                    heapq.heappush(heap, (candidate, v))

        for v in range(n):
            if dist[v] < inf:
                potential[v] += dist[v]

        v = sink
        path_cost = 0
        while v != source:
            u = parent_node[v]
            edge_i = parent_edge[v]
            edge = graph[u][edge_i]
            path_cost += edge[2]
            edge[1] -= 1
            graph[v][edge[3]][1] += 1
            v = u

        total_cost += path_cost

    return -total_cost
