def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)

    parent = [-1] * n
    depth = [0] * n
    order = [0]

    for v in order:
        for u in graph[v]:
            if u == parent[v]:
                continue
            parent[u] = v
            depth[u] = depth[v] + 1
            order.append(u)

    total_weight = sum(w)
    subtree = w[:]

    for v in reversed(order[1:]):
        subtree[parent[v]] += subtree[v]

    result = [0] * n
    result[0] = sum(w[v] * depth[v] for v in range(n))

    for v in order[1:]:
        p = parent[v]
        result[v] = result[p] + total_weight - 2 * subtree[v]

    return result
