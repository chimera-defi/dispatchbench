from collections import deque


def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    # BFS order from root 0 avoids recursion depth issues on long paths.
    parent = [-1] * n
    order = []
    visited = [False] * n
    visited[0] = True
    dq = deque([0])
    while dq:
        v = dq.popleft()
        order.append(v)
        for u in adj[v]:
            if not visited[u]:
                visited[u] = True
                parent[u] = v
                dq.append(u)

    # sub[v]: total weight in subtree of v
    # down[v]: sum of w[u] * dist(u, v) for u in subtree of v
    sub = list(w)
    down = [0] * n
    for v in reversed(order):
        p = parent[v]
        if p != -1:
            sub[p] += sub[v]
            down[p] += down[v] + sub[v]

    # Reroot: moving the root from p to child c shifts sub[c] nodes one step
    # closer and the remaining total - sub[c] nodes one step farther.
    ans = [0] * n
    ans[0] = down[0]
    total = sub[0]
    for v in order:
        for u in adj[v]:
            if u != parent[v]:
                ans[u] = ans[v] + total - 2 * sub[u]

    return ans
