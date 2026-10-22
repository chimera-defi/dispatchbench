from collections import deque


def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    # BFS from root 0 to get a parent array and a processing order.
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

    # sub[v] = total weight in v's subtree
    # down[v] = sum of w[u] * dist(u, v) over u in v's subtree
    sub = w[:]
    down = [0] * n
    for u in reversed(order):
        p = parent[u]
        if p != -1:
            sub[p] += sub[u]
            down[p] += down[u] + sub[u]

    total = sub[0]
    res = [0] * n
    res[0] = down[0]

    # Reroot: moving from p to child c shifts sub[c] nodes one step closer
    # and the remaining (total - sub[c]) nodes one step farther.
    for u in order:
        for v in adj[u]:
            if parent[v] == u:
                res[v] = res[u] + total - 2 * sub[v]

    return res
