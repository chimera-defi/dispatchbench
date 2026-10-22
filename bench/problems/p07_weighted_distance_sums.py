RUNG = 4
FUNC = "weighted_distance_sums"
SIGNATURE = "def weighted_distance_sums(n: int, edges: list[list[int]], w: list[int]) -> list[int]:"
STATEMENT = """\
A tree has nodes `0 .. n-1`, connected by the `n - 1` undirected edges in `edges`, each of length 1. Node `u` has weight `w[u]`.

For every node `v`, compute `S(v)`, the sum over all nodes `u` of `w[u] * dist(u, v)`, where `dist` is the number of edges on the path between them.

Return the list `[S(0), S(1), ..., S(n-1)]`.

Example: `weighted_distance_sums(3, [[0, 1], [1, 2]], [1, 10, 100])` returns `[210, 101, 12]`.

Constraints: `1 <= n <= 200000`, `0 <= w[u] <= 10**9`. The tree may be a single long path."""


def ref(n, edges, w):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b); adj[b].append(a)
    parent = [-1] * n; order = [0]; seen = [False] * n; seen[0] = True
    for u in order:
        for v in adj[u]:
            if not seen[v]: seen[v] = True; parent[v] = u; order.append(v)
    sub = w[:]; down = [0] * n  # down[u] = sum over subtree of w * dist to u
    for u in reversed(order):
        p = parent[u]
        if p >= 0:
            sub[p] += sub[u]; down[p] += down[u] + sub[u]
    total = sub[0]; ans = [0] * n; ans[0] = down[0]
    for u in order[1:]:
        ans[u] = ans[parent[u]] + total - 2 * sub[u]
    return ans


def brute(n, edges, w):
    from collections import deque
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b); adj[b].append(a)
    out = []
    for v in range(n):
        d = [-1] * n; d[v] = 0; q = deque([v])
        while q:
            u = q.popleft()
            for x in adj[u]:
                if d[x] < 0: d[x] = d[u] + 1; q.append(x)
        out.append(sum(w[u] * d[u] for u in range(n)))
    return out


def _tree(rng, n, path=False):
    perm = list(range(n)); rng.shuffle(perm)
    edges = []
    for i in range(1, n):
        p = i - 1 if path else rng.randrange(i)
        e = [perm[i], perm[p]]; rng.shuffle(e); edges.append(e)
    rng.shuffle(edges)
    return edges


def small(rng):
    n = rng.randint(1, 9)
    return (n, _tree(rng, n, rng.random() < 0.3), [rng.choice([0, 1, rng.randint(0, 10**9)]) for _ in range(n)])


def fixed():
    return [EXAMPLES[0][0], (1, [], [5]), (2, [[1, 0]], [0, 0]), (2, [[0, 1]], [10**9, 10**9])]


def big(rng):
    n = 200000
    return [(n, _tree(rng, n, path=True), [rng.randint(0, 10**9) for _ in range(n)]),
            (n, _tree(rng, n), [rng.randint(0, 10**9) for _ in range(n)]),
            (n, [[i, i + 1] for i in range(n - 1)], [10**9] * n)]


EXAMPLES = [((3, [[0, 1], [1, 2]], [1, 10, 100]), [210, 101, 12])]

WRONG = {
    "recursive_dfs": """
import sys
sys.setrecursionlimit(10000)
def weighted_distance_sums(n, edges, w):
    adj = [[] for _ in range(n)]
    for a, b in edges: adj[a].append(b); adj[b].append(a)
    sub = w[:]; down = [0] * n; ans = [0] * n
    def dfs1(u, p):
        for v in adj[u]:
            if v != p: dfs1(v, u); sub[u] += sub[v]; down[u] += down[v] + sub[v]
    def dfs2(u, p):
        for v in adj[u]:
            if v != p: ans[v] = ans[u] + sub[0] - 2 * sub[v]; dfs2(v, u)
    dfs1(0, -1); ans[0] = down[0]; dfs2(0, -1)
    return ans
""",
    "bfs_each_node": """
def weighted_distance_sums(n, edges, w):
    from collections import deque
    adj = [[] for _ in range(n)]
    for a, b in edges: adj[a].append(b); adj[b].append(a)
    out = []
    for v in range(n):
        d = [-1] * n; d[v] = 0; q = deque([v])
        while q:
            u = q.popleft()
            for x in adj[u]:
                if d[x] < 0: d[x] = d[u] + 1; q.append(x)
        out.append(sum(w[u] * d[u] for u in range(n)))
    return out
""",
    "unweighted_reroot": """
def weighted_distance_sums(n, edges, w):
    adj = [[] for _ in range(n)]
    for a, b in edges: adj[a].append(b); adj[b].append(a)
    par = [-1] * n; order = [0]; seen = [False] * n; seen[0] = True
    for u in order:
        for v in adj[u]:
            if not seen[v]: seen[v] = True; par[v] = u; order.append(v)
    sub = w[:]; cnt = [1] * n; down = [0] * n
    for u in reversed(order):
        if par[u] >= 0: sub[par[u]] += sub[u]; cnt[par[u]] += cnt[u]; down[par[u]] += down[u] + sub[u]
    ans = [0] * n; ans[0] = down[0]
    for u in order[1:]: ans[u] = ans[par[u]] + n - 2 * cnt[u]
    return ans
""",
}
