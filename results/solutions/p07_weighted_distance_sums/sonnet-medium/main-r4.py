def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    parent = [-1] * n
    order = []
    visited = [False] * n
    visited[0] = True
    stack = [0]
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                stack.append(v)

    total = sum(w)
    sub = list(w)       # subtree weight sums
    down = [0] * n      # sum of w[u]*dist(u, v) over u in subtree of v

    for u in reversed(order):
        p = parent[u]
        if p >= 0:
            sub[p] += sub[u]
            down[p] += down[u] + sub[u]

    res = [0] * n
    res[0] = down[0]
    for u in order:
        p = parent[u]
        if p >= 0:
            res[u] = res[p] + total - 2 * sub[u]
    return res
