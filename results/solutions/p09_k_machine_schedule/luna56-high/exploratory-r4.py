def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)

    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, cap: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), cap, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    source, sink = 0, n - 1
    flow = 0
    min_cost = 0

    while flow < k:
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
                v, _, cap, cost = edge
                if cap > 0 and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = ei
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        if dist[sink] == float("inf"):
            break

        add = k - flow
        v = sink
        while v != source:
            u = prev_node[v]
            add = min(add, graph[u][prev_edge[v]][2])
            v = u

        v = sink
        while v != source:
            u = prev_node[v]
            ei = prev_edge[v]
            edge = graph[u][ei]
            edge[2] -= add
            graph[v][edge[1]][2] += add
            v = u

        flow += add
        min_cost += add * dist[sink]

    return -min_cost
