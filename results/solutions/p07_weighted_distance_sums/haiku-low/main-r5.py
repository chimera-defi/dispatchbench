from collections import deque

def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    if n == 1:
        return [0]

    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    # BFS order from root 0, with parent array
    parent = [-1] * n
    order = []
    visited = [False] * n
    visited[0] = True
    dq = deque([0])
    while dq:
        u = dq.popleft()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                dq.append(v)

    # sub[u] = total weight in subtree of u
    sub = [0] * n
    for u in reversed(order):
        sub[u] += w[u]
        if parent[u] != -1:
            sub[parent[u]] += sub[u]

    total = sub[0]

    # S(0) = sum of w[u] * depth(u)
    depth = [0] * n
    for u in order:
        if parent[u] != -1:
            depth[u] = depth[parent[u]] + 1
    s0 = sum(w[u] * depth[u] for u in range(n))

    # Rerooting: S(child) = S(parent) + total - 2 * sub[child]
    res = [0] * n
    res[0] = s0
    for u in order:
        if parent[u] != -1:
            res[u] = res[parent[u]] + total - 2 * sub[u]

    return res
