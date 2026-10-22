def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)

    parent = [-1] * n
    order = [0]
    parent[0] = 0

    for v in order:
        for u in graph[v]:
            if parent[u] == -1:
                parent[u] = v
                order.append(u)

    subtree_weight = w[:]
    for v in reversed(order[1:]):
        subtree_weight[parent[v]] += subtree_weight[v]

    total_weight = subtree_weight[0]
    sums = [0] * n
    sums[0] = sum(subtree_weight[v] for v in order[1:])

    for v in order[1:]:
        p = parent[v]
        sums[v] = sums[p] + total_weight - 2 * subtree_weight[v]

    return sums
