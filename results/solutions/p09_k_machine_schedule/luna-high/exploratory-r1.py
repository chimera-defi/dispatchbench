def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    import heapq

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    if not times:
        return 0

    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u, v, capacity, cost):
        graph[u].append([v, len(graph[v]), capacity, cost])
        graph[v].append([u, len(graph[u]) - 1, 0, -cost])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)

    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Initial shortest-path potentials; all usable edges point forward in time.
    inf = float("inf")
    potential = [inf] * n
    potential[0] = 0
    for u in range(n):
        if potential[u] == inf:
            continue
        for v, _, capacity, cost in graph[u]:
            if capacity and potential[v] > potential[u] + cost:
                potential[v] = potential[u] + cost

    flow = 0
    total_cost = 0
    sink = n - 1

    while flow < k:
        dist = [inf] * n
        prev_node = [-1] * n
        prev_edge = [-1] * n
        dist[0] = 0
        heap = [(0, 0)]

        while heap:
            d, u = heapq.heappop(heap)
            if d != dist[u]:
                continue
            for ei, (v, _, capacity, cost) in enumerate(graph[u]):
                if capacity <= 0:
                    continue
                reduced_cost = cost + potential[u] - potential[v]
                nd = d + reduced_cost
                if nd < dist[v]:
                    dist[v] = nd
                    prev_node[v] = u
                    prev_edge[v] = ei
                    heapq.heappush(heap, (nd, v))

        for v in range(n):
            if dist[v] < inf:
                potential[v] += dist[v]

        amount = k - flow
        v = sink
        while v != 0:
            u = prev_node[v]
            ei = prev_edge[v]
            amount = min(amount, graph[u][ei][2])
            v = u

        v = sink
        while v != 0:
            u = prev_node[v]
            ei = prev_edge[v]
            edge = graph[u][ei]
            total_cost += amount * edge[3]
            edge[2] -= amount
            graph[v][edge[1]][2] += amount
            v = u

        flow += amount

    return -total_cost
