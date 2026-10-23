def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for job in jobs for t in job[:2]})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    source = n
    sink = n + 1
    graph = [[] for _ in range(n + 2)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    add_edge(source, 0, k, 0)
    add_edge(n - 1, sink, k, 0)

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    total_cost = 0
    flow = 0

    while flow < k:
        inf = 10**30
        dist = [inf] * (n + 2)
        prev = [None] * (n + 2)
        in_queue = [False] * (n + 2)
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
                if capacity and dist[v] > dist[u] + cost:
                    dist[v] = dist[u] + cost
                    prev[v] = (u, i)
                    if not in_queue[v]:
                        in_queue[v] = True
                        queue.append(v)

        if dist[sink] == inf:
            break

        amount = k - flow
        v = sink
        while v != source:
            u, edge_index = prev[v]
            amount = min(amount, graph[u][edge_index][2])
            v = u

        v = sink
        while v != source:
            u, edge_index = prev[v]
            edge = graph[u][edge_index]
            edge[2] -= amount
            graph[v][edge[1]][2] += amount
            v = u

        flow += amount
        total_cost += amount * dist[sink]

    return -total_cost
