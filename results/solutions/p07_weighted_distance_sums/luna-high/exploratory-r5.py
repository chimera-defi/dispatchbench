def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)

    parent = [-1] * n
    depth = [0] * n
    order = [0]
    parent[0] = 0

    for v in order:
        for u in graph[v]:
            if parent[u] == -1:
                parent[u] = v
                depth[u] = depth[v] + 1
                order.append(u)

    total_weight = sum(w)
    subtree_weight = w[:]
    result = [0] * n
    result[0] = sum(w[v] * depth[v] for v in range(n))

    for v in reversed(order[1:]):
        subtree_weight[parent[v]] += subtree_weight[v]

    for v in order[1:]:
        p = parent[v]
        result[v] = result[p] + total_weight - 2 * subtree_weight[v]

    return result
