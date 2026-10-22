from collections import deque

def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    if not jobs:
        return 0
    times = sorted({t for s, e, p in jobs for t in (s, e)})
    idx = {t: i for i, t in enumerate(times)}
    n = len(times)

    to = []
    cap = []
    cost = []
    adj = [[] for _ in range(n)]

    def add(u, v, c, w):
        adj[u].append(len(to))
        to.append(v)
        cap.append(c)
        cost.append(w)
        adj[v].append(len(to))
        to.append(u)
        cap.append(0)
        cost.append(-w)

    for i in range(n - 1):
        add(i, i + 1, k, 0)
    for s, e, p in jobs:
        add(idx[s], idx[e], 1, -p)

    src, snk = 0, n - 1
    flow = 0
    total = 0
    INF = float("inf")
    while flow < k:
        dist = [INF] * n
        inq = [False] * n
        prev = [-1] * n
        dist[src] = 0
        dq = deque([src])
        while dq:
            u = dq.popleft()
            inq[u] = False
            du = dist[u]
            for eid in adj[u]:
                if cap[eid] > 0:
                    v = to[eid]
                    nd = du + cost[eid]
                    if nd < dist[v]:
                        dist[v] = nd
                        prev[v] = eid
                        if not inq[v]:
                            inq[v] = True
                            dq.append(v)
        if dist[snk] == INF:
            break
        # bottleneck
        f = k - flow
        v = snk
        while v != src:
            eid = prev[v]
            f = min(f, cap[eid])
            v = to[eid ^ 1]
        v = snk
        while v != src:
            eid = prev[v]
            cap[eid] -= f
            cap[eid ^ 1] += f
            v = to[eid ^ 1]
        flow += f
        total += f * dist[snk]
    return -total
