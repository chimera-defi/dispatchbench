from collections import deque


def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    # Build adjacency list
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    # BFS from root 0 to get a parent array and a processing order (no recursion)
    parent = [-1] * n
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
                queue.append(u)

    # sub_w[v]: total weight in v's subtree
    # down[v]: sum of w[u] * dist(u, v) over u in v's subtree
    sub_w = list(w)
    down = [0] * n
    for v in reversed(order):
        p = parent[v]
        if p != -1:
            sub_w[p] += sub_w[v]
            down[p] += down[v] + sub_w[v]

    total = sub_w[0]
    res = [0] * n
    res[0] = down[0]

    # Reroot: moving the root from p to child c brings the c-subtree
    # one step closer and everything else one step farther
    for v in order:
        p = parent[v]
        if p != -1:
            res[v] = res[p] + (total - sub_w[v]) - sub_w[v]

    return res
