from collections import deque


def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    # BFS from root 0 to get a parent-first order and depths
    parent = [-1] * n
    depth = [0] * n
    order = []
    visited = [False] * n
    visited[0] = True
    queue = deque([0])
    while queue:
        v = queue.popleft()
        order.append(v)
        for u in adj[v]:
            if not visited[u]:
                visited[u] = True
                parent[u] = v
                depth[u] = depth[v] + 1
                queue.append(u)

    total_weight = sum(w)

    # Subtree weight sums, processed children before parents
    sub = list(w)
    for v in reversed(order):
        p = parent[v]
        if p != -1:
            sub[p] += sub[v]

    # S(0) directly from depths
    s = [0] * n
    s[0] = sum(w[u] * depth[u] for u in range(n))

    # Reroot: moving root from p to child c shifts weight sub[c] closer by 1
    # and the remaining total_weight - sub[c] farther by 1
    for v in order:
        for u in adj[v]:
            if parent[u] == v:
                s[u] = s[v] + total_weight - 2 * sub[u]

    return s
