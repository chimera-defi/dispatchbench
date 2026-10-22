def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({time for start, end, _ in jobs for time in (start, end)})
    index = {time: i for i, time in enumerate(times)}
    source, sink = 0, len(times) - 1
    graph = [[] for _ in times]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, capacity, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(len(times) - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    total_cost = 0
    n = len(times)
    potential = [0] * n

    for _ in range(k):
        dist = [float("inf")] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        dist[source] = 0
        used = [False] * n

        for _ in range(n):
            u = -1
            for v in range(n):
                if not used[v] and (u == -1 or dist[v] < dist[u]):
                    u = v
            if u == -1 or dist[u] == float("inf"):
                break
            used[u] = True
            for ei, edge in enumerate(graph[u]):
                v, capacity, cost, _ = edge
                if capacity and dist[v] > dist[u] + cost + potential[u] - potential[v]:
                    dist[v] = dist[u] + cost + potential[u] - potential[v]
                    prev_node[v] = u
                    prev_edge[v] = ei

        if dist[sink] == float("inf"):
            break

        for v in range(n):
            if dist[v] < float("inf"):
                potential[v] += dist[v]

        v = sink
        while v != source:
            u = prev_node[v]
            ei = prev_edge[v]
            edge = graph[u][ei]
            edge[1] -= 1
            graph[v][edge[3]][1] += 1
            total_cost += edge[2]
            v = u

    return -total_cost
