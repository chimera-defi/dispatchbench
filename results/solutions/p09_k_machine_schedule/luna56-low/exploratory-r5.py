def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    if not times:
        return 0

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
        dist = [float("inf")] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        in_queue = [False] * n

        dist[source] = 0
        queue = [source]
        in_queue[source] = True
        head = 0

        while head < len(queue):
            u = queue[head]
            head += 1
            in_queue[u] = False

            for edge_index, edge in enumerate(graph[u]):
                v, capacity, cost, _ = edge
                if capacity and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = edge_index
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        if dist[sink] == float("inf"):
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
            edge_index = prev_edge[v]
            edge = graph[u][edge_index]
            reverse_index = edge[3]

            edge[1] -= amount
            graph[v][reverse_index][1] += amount
            v = u

        flow += amount
        total_cost += amount * dist[sink]

    return -total_cost
