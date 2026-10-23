def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    parent = [-1] * n
    order = [0]
    parent[0] = n

    depth_sum = 0
    for v in order:
        depth_sum += w[v] * (len(order) - 1 if False else 0)
        for u in adj[v]:
            if u != parent[v]:
                parent[u] = v
                order.append(u)

    depth = [0] * n
    initial = 0
    for v in order:
        initial += w[v] * depth[v]
        for u in adj[v]:
            if u != parent[v]:
                depth[u] = depth[v] + 1

    subtree = w[:]
    for v in reversed(order[1:]):
        subtree[parent[v]] += subtree[v]

    total_weight = sum(w)
    result = [0] * n
    result[0] = initial

    for v in order[1:]:
        p = parent[v]
        result[v] = result[p] + total_weight - 2 * subtree[v]

    return result
