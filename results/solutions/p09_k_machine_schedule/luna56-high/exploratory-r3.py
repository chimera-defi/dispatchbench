def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)

    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, capacity, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    total_cost = 0

    for _ in range(k):
        inf = 10**30
        dist = [inf] * n
        in_queue = [False] * n
        parent = [None] * n
        queue = [0]
        dist[0] = 0
        in_queue[0] = True
        head = 0

        while head < len(queue):
            u = queue[head]
            head += 1
            in_queue[u] = False

            for edge_index, edge in enumerate(graph[u]):
                v, capacity, cost, _ = edge
                if capacity and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    parent[v] = (u, edge_index)
                    if not in_queue[v]:
                        in_queue[v] = True
                        queue.append(v)

        v = n - 1
        while v != 0:
            u, edge_index = parent[v]
            edge = graph[u][edge_index]
            reverse_index = edge[3]
            edge[1] -= 1
            graph[v][reverse_index][1] += 1
            v = u

        total_cost += dist[n - 1]

    return -total_cost
