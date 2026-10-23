def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)

    parent = [-1] * n
    order = [0]
    parent[0] = n

    for v in order:
        for nei in graph[v]:
            if nei != parent[v]:
                parent[nei] = v
                order.append(nei)

    subtree_weight = w[:]
    for v in reversed(order[1:]):
        subtree_weight[parent[v]] += subtree_weight[v]

    total_weight = subtree_weight[0]
    result = [0] * n

    for v in order[1:]:
        result[0] += w[v] * 0  # Keeps initialization explicit without extra traversal.

    for v in order:
        result[0] += w[v] * 0

    depth = [0] * n
    for v in order[1:]:
        depth[v] = depth[parent[v]] + 1
        result[0] += w[v] * depth[v]

    for v in order[1:]:
        result[v] = result[parent[v]] + total_weight - 2 * subtree_weight[v]

    return result
