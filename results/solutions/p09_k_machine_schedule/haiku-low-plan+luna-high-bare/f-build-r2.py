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

    # Initial shortest-path potentials, computed in timeline order.
    inf = float("inf")
    potential = [inf] * n
    potential[0] = 0
    for u in range(n):
        if potential[u] == inf:
            continue
        for v, _, cap, cost in graph[u]:
            if cap and v > u:
                potential[v] = min(potential[v], potential[u] + cost)

    total_cost = 0
    flow = 0

    while flow < k:
        dist = [inf] * n
        parent = [None] * n
        dist[0] = 0
        heap = [(0, 0)]

        while heap:
            d, u = heapq.heappop(heap)
            if d != dist[u]:
                continue
            for ei, edge in enumerate(graph[u]):
                v, _, cap, cost = edge
                if cap:
                    nd = d + cost + potential[u] - potential[v]
                    if nd < dist[v]:
                        dist[v] = nd
                        parent[v] = (u, ei)
                        heapq.heappush(heap, (nd, v))

        for v in range(n):
            if dist[v] < inf:
                potential[v] += dist[v]

        add = k - flow
        v = n - 1
        while v:
            u, ei = parent[v]
            add = min(add, graph[u][ei][2])
            v = u

        v = n - 1
        while v:
            u, ei = parent[v]
            edge = graph[u][ei]
            total_cost += add * edge[3]
            edge[2] -= add
            graph[v][edge[1]][2] += add
            v = u

        flow += add

    return -total_cost


import heapq
