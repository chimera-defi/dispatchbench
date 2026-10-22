def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    if n == 1:
        return [0]

    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    # BFS order from root 0 to avoid recursion depth issues on long paths
    parent = [-1] * n
    order = []
    visited = [False] * n
    visited[0] = True
    stack = [0]
    while stack:
        v = stack.pop()
        order.append(v)
        for u in adj[v]:
            if not visited[u]:
                visited[u] = True
                parent[u] = v
                stack.append(u)

    # sub[v] = total weight in subtree of v
    sub = w[:]
    for v in reversed(order):
        p = parent[v]
        if p != -1:
            sub[p] += sub[v]

    total = sum(w)

    # down[v] = sum over subtree of v of w[u] * dist(u, v)
    down = [0] * n
    for v in reversed(order):
        p = parent[v]
        if p != -1:
            down[p] += down[v] + sub[v]

    # Reroot: res[child] = res[parent] + total - 2 * sub[child]
    res = [0] * n
    res[0] = down[0]
    for v in order:
        p = parent[v]
        if p != -1:
            res[v] = res[p] + total - 2 * sub[v]

    return res
