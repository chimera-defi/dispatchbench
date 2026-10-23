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

    subtree = w[:]
    total = sum(w)
    root_sum = 0

    for v in range(n):
        root_sum += w[v] * 0  # placeholder for depth calculation

    depth = [0] * n
    for v in order[1:]:
        depth[v] = depth[parent[v]] + 1
        root_sum += w[v] * depth[v]

    for v in reversed(order[1:]):
        subtree[parent[v]] += subtree[v]

    result = [0] * n
    result[0] = root_sum

    for v in order[1:]:
        result[v] = result[parent[v]] + total - 2 * subtree[v]

    return result
