def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0
    if k >= len(jobs):
        return sum(job[2] for job in jobs)

    times = sorted({t for start, end, _ in jobs for t in (start, end)})
    index = {t: i for i, t in enumerate(times)}
    n = len(times)
    graph = [[] for _ in range(n)]

    def add_edge(u, v, cap, cost):
        graph[u].append([v, cap, cost, len(graph[v])])
        graph[v].append([u, 0, -cost, len(graph[u]) - 1])

    for i in range(n - 1):
        add_edge(i, i + 1, k, 0)
    for start, end, pay in jobs:
        add_edge(index[start], index[end], 1, -pay)

    # Initial shortest-distance potentials; all positive-capacity edges go forward.
    inf = float("inf")
    potential = [inf] * n
    potential[0] = 0
    for u in range(n):
        if potential[u] == inf:
            continue
        for v, cap, cost, _ in graph[u]:
            if cap and potential[v] > potential[u] + cost:
                potential[v] = potential[u] + cost
    potential = [0 if d == inf else d for d in potential]

    total_cost = 0
    for _ in range(k):
        dist = [inf] * n
        parent_node = [-1] * n
        parent_edge = [-1] * n
        dist[0] = 0
        heap = [(0, 0)]

        while heap:
            d, u = heapq.heappop(heap)
            if d != dist[u]:
                continue
            for ei, (v, cap, cost, _) in enumerate(graph[u]):
                if cap <= 0:
                    continue
                nd = d + cost + potential[u] - potential[v]
                if nd < dist[v]:
                    dist[v] = nd
                    parent_node[v] = u
                    parent_edge[v] = ei
                    heapq.heappush(heap, (nd, v))

        for v in range(n):
            if dist[v] < inf:
                potential[v] += dist[v]

        v = n - 1
        while v != 0:
            u = parent_node[v]
            ei = parent_edge[v]
            edge = graph[u][ei]
            total_cost += edge[2]
            edge[1] -= 1
            graph[v][edge[3]][1] += 1
            v = u

    return -total_cost


import heapq
