def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, capacity, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    source, sink = 0, n - 1
    total_cost = 0
    flow = 0

    while flow < k:
        inf = 10**30
        dist = [inf] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        in_queue = [False] * n
        queue = [source]
        dist[source] = 0
        head = 0
        in_queue[source] = True

        while head < len(queue):
            u = queue[head]
            head += 1
            in_queue[u] = False

            for ei, edge in enumerate(graph[u]):
                v, capacity, cost, _ = edge
                if capacity and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = ei
                    if not in_queue[v]:
                        in_queue[v] = True
                        queue.append(v)

        if dist[sink] == inf:
            break

        amount = k - flow
        v = sink
        while v != source:
            u = prev_node[v]
            amount = min(amount, graph[u][prev_edge[v]][1])
            v = u

        v = sink
        while v != source:
            u = prev_node[v]
            ei = prev_edge[v]
            edge = graph[u][ei]
            reverse_index = edge[3]
            edge[1] -= amount
            graph[v][reverse_index][1] += amount
            v = u

        flow += amount
        total_cost += amount * dist[sink]

    return -total_cost
