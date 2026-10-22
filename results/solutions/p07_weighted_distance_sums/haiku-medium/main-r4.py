from collections import deque


def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    parent = [-1] * n
    depth = [0] * n
    visited = [False] * n
    visited[0] = True
    order = []
    queue = deque([0])
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                depth[v] = depth[u] + 1
                queue.append(v)

    total = sum(w)

    # Subtree weight sums, accumulated bottom-up.
    sub = w[:]
    for u in reversed(order):
        p = parent[u]
        if p != -1:
            sub[p] += sub[u]

    # S(root) computed directly.
    res = [0] * n
    res[0] = sum(w[u] * depth[u] for u in range(n))

    # Re-root top-down: moving from p to child c brings the subtree of c
    # one step closer (-sub[c]) and everything else one step farther (+(total - sub[c])).
    for v in order[1:]:
        p = parent[v]
        res[v] = res[p] - sub[v] + (total - sub[v])

    return res
