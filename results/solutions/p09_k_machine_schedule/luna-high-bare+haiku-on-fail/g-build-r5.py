def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u: int, v: int, capacity: int, cost: int) -> None:
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    total_cost = 0
    flow = 0
    source, sink = 0, n - 1

    while flow < k:
        dist = [float("inf")] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        in_queue = [False] * n
        queue = [source]
        head = 0
        dist[source] = 0
        in_queue[source] = True

        while head < len(queue):
            u = queue[head]
            head += 1
            in_queue[u] = False

            for i, edge in enumerate(graph[u]):
                v, _, capacity, cost = edge
                if capacity > 0 and dist[u] + cost < dist[v]:
                    dist[v] = dist[u] + cost
                    prev_node[v] = u
                    prev_edge[v] = i
                    if not in_queue[v]:
                        queue.append(v)
                        in_queue[v] = True

        v = sink
        while v != source:
            u = prev_node[v]
            edge = graph[u][prev_edge[v]]
            edge[2] -= 1
            graph[v][edge[1]][2] += 1
            v = u

        total_cost += dist[sink]
        flow += 1

    return -total_cost
