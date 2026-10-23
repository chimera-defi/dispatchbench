def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}

    n = len(times) + 2
    source = len(times)
    sink = source + 1
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, capacity, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    add_edge(source, index[times[0]], k, 0)
    add_edge(index[times[-1]], sink, k, 0)

    for i in range(len(times) - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    total_cost = 0
    flow = 0

    while flow < k:
        dist = [float("inf")] * n
        prev = [None] * n
        in_queue = [False] * n
        queue = [source]
        head = 0
        dist[source] = 0
        in_queue[source] = True

        while head < len(queue):
            u = queue[head]
            head += 1
            in_queue[u] = False

            for edge_index, edge in enumerate(graph[u]):
                v, capacity, cost, _ = edge
                if capacity > 0 and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    prev[v] = (u, edge_index)
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        add_flow = k - flow
        v = sink
        while v != source:
            u, edge_index = prev[v]
            add_flow = min(add_flow, graph[u][edge_index][1])
            v = u

        v = sink
        while v != source:
            u, edge_index = prev[v]
            edge = graph[u][edge_index]
            edge[1] -= add_flow
            graph[v][edge[3]][1] += add_flow
            v = u

        flow += add_flow
        total_cost += add_flow * dist[sink]

    return -total_cost
