from collections import deque


def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    # BFS from node 0 to get a parent array and a top-down processing order.
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

    # W[v]: total weight in v's subtree.
    # D[v]: sum of w[u] * dist(u, v) over u in v's subtree.
    W = list(w)
    D = [0] * n
    for v in reversed(order):
        p = parent[v]
        if p != -1:
            W[p] += W[v]
            D[p] += D[v] + W[v]

    # Reroot: moving the root from p to child c shifts weight W[c] one step
    # closer and the remaining total - W[c] one step farther.
    total = W[0]
    S = [0] * n
    S[0] = D[0]
    for v in order:
        p = parent[v]
        if p != -1:
            S[v] = S[p] + total - 2 * W[v]

    return S
