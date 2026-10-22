def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0

    times = sorted({t for s, e, _ in jobs for t in (s, e)})
    idx = {t: i for i, t in enumerate(times)}
    m = len(times)

    to, frm, cap, cost = [], [], [], []
    graph = [[] for _ in range(m)]

    def add(u, v, c, w):
        graph[u].append(len(to))
        to.append(v); frm.append(u); cap.append(c); cost.append(w)
        graph[v].append(len(to))
        to.append(u); frm.append(v); cap.append(0); cost.append(-w)

    # Idle time: a printer can move forward in time without working.
    for i in range(m - 1):
        add(i, i + 1, k, 0)
    # Each job: one unit of printer flow goes from its start to its end, earning pay.
    for s, e, p in jobs:
        add(idx[s], idx[e], 1, -p)

    src, snk = 0, m - 1
    INF = float('inf')
    flow = 0
    total = 0

    # Successive shortest paths (min cost). Bellman-Ford handles negative costs.
    while flow < k:
        dist = [INF] * m
        prev = [-1] * m
        dist[src] = 0
        for _ in range(m):
            updated = False
            for u in range(m):
                if dist[u] == INF:
                    continue
                for eid in graph[u]:
                    if cap[eid] > 0 and dist[u] + cost[eid] < dist[to[eid]]:
                        dist[to[eid]] = dist[u] + cost[eid]
                        prev[to[eid]] = eid
                        updated = True
            if not updated:
                break

        # Stop once extra printers no longer add pay.
        if dist[snk] == INF or dist[snk] >= 0:
            break

        f = k - flow
        v = snk
        while v != src:
            eid = prev[v]
            f = min(f, cap[eid])
            v = frm[eid]

        v = snk
        while v != src:
            eid = prev[v]
            cap[eid] -= f
            cap[eid ^ 1] += f
            v = frm[eid]

        total += f * dist[snk]
        flow += f

    return -total
