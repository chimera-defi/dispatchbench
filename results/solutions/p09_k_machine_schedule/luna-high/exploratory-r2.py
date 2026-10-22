def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

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

    # Initial shortest-path potentials; all usable original edges go forward in time.
    potential = [0] * n
    for u in range(n):
        for v, _, capacity, cost in graph[u]:
            if capacity > 0:
                potential[v] = min(potential[v], potential[u] + cost)

    total_cost = 0
    flow = 0
    sink = n - 1

    while flow < k:
        dist = [float("inf")] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        dist[0] = 0
        heap = [(0, 0)]

        while heap:
            d, u = __import__("heapq").heappop(heap)
            if d != dist[u]:
                continue
            for ei, edge in enumerate(graph[u]):
                v, _, capacity, cost = edge
                if capacity <= 0:
                    continue
                nd = d + cost + potential[u] - potential[v]
                if nd < dist[v]:
                    dist[v] = nd
                    prev_node[v] = u
                    prev_edge[v] = ei
                    __import__("heapq").heappush(heap, (nd, v))

        for v in range(n):
            if dist[v] < float("inf"):
                potential[v] += dist[v]

        add = k - flow
        v = sink
        while v != 0:
            u = prev_node[v]
            ei = prev_edge[v]
            add = min(add, graph[u][ei][2])
            v = u

        v = sink
        while v != 0:
            u = prev_node[v]
            ei = prev_edge[v]
            edge = graph[u][ei]
            total_cost += add * edge[3]
            edge[2] -= add
            graph[v][edge[1]][2] += add
            v = u

        flow += add

    return -total_cost
