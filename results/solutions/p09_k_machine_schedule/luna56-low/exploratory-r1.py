def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, cap: int, cost: int) -> None:
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    source, sink = 0, n - 1
    total_cost = 0

    for _ in range(k):
        dist = [float("inf")] * n
        in_queue = [False] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n

        dist[source] = 0
        queue = [source]
        in_queue[source] = True
        head = 0

        while head < len(queue):
            u = queue[head]
            head += 1
            in_queue[u] = False

            for ei, edge in enumerate(graph[u]):
                v, cap, cost, _ = edge
                if cap > 0 and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = ei
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        v = sink
        while v != source:
            u = prev_node[v]
            ei = prev_edge[v]
            edge = graph[u][ei]
            edge[1] -= 1
            graph[v][edge[3]][1] += 1
            v = u

        total_cost += dist[sink]

    return -total_cost
