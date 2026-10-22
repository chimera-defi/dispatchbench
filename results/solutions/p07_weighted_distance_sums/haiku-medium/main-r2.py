from collections import deque


def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    # BFS order from root 0, so parents are processed before children
    parent = [-1] * n
    order = []
    visited = [False] * n
    visited[0] = True
    queue = deque([0])
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                queue.append(v)

    # W[v]: total weight in subtree of v
    # D[v]: sum of w[u] * dist(u, v) for u in subtree of v
    W = list(w)
    D = [0] * n
    for u in reversed(order):
        p = parent[u]
        if p != -1:
            W[p] += W[u]
            D[p] += D[u] + W[u]

    total = W[0]
    S = [0] * n
    S[0] = D[0]

    # Reroot: moving from parent p to child c brings subtree(c) one step closer
    # and everything else one step farther
    for u in order:
        for v in adj[u]:
            if v != parent[u]:
                S[v] = S[u] + total - 2 * W[v]

    return S
