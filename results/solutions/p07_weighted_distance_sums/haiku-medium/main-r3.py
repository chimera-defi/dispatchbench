from collections import deque


def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    # BFS from root 0 for a traversal order and parent array (iterative, safe for deep paths)
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

    # sub_w[v]: total weight in subtree of v
    # sub_d[v]: sum of w[u] * dist(u, v) over u in subtree of v
    sub_w = list(w)
    sub_d = [0] * n
    for v in reversed(order):
        p = parent[v]
        if p != -1:
            sub_w[p] += sub_w[v]
            sub_d[p] += sub_d[v] + sub_w[v]

    total_w = sub_w[0]
    ans = [0] * n
    ans[0] = sub_d[0]
    # Reroot: moving from parent p to child c shifts distances by +1 for nodes
    # outside c's subtree and -1 for nodes inside it.
    for v in order:
        p = parent[v]
        if p != -1:
            ans[v] = ans[p] + total_w - 2 * sub_w[v]

    return ans
