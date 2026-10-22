RUNG = 3
FUNC = "pass_route"
SIGNATURE = "def pass_route(n: int, edges: list[list[int]], stations: list[list[int]], prices: list[int]) -> int:"
STATEMENT = """\
A transit network has stops `0 .. n-1` and undirected rides `edges[i] = [u, v, cost, zone]`. Taking a ride in either direction costs `cost`. `zone` is either `-1` (no zone) or a zone number `0 .. len(prices)-1`.

A traveller can buy a pass for zone `z` at price `prices[z]`, but only while standing at a stop listed in `stations` as `[stop, z]`. Once bought, the pass makes every ride with that zone free for the rest of the trip. A pass can be bought at most once. Rides with zone `-1` are never free.

Return the minimum total amount spent on rides plus passes to travel from stop `0` to stop `n - 1`, or `-1` if stop `n - 1` cannot be reached.

Example: with `n = 4`, `edges = [[0, 1, 5, -1], [1, 2, 100, 0], [2, 3, 100, 0], [0, 3, 250, -1]]`, `stations = [[1, 0]]` and `prices = [30]`, the answer is `35`: ride to stop 1 for 5, buy the zone-0 pass for 30, then ride free to stop 3.

Constraints: `2 <= n <= 2000`, `0 <= len(edges) <= 10000`, `0 <= cost <= 10**6`, `1 <= len(prices) <= 4`, `0 <= prices[z] <= 10**6`, `0 <= len(stations) <= 50`. Multiple rides may join the same pair of stops."""


def ref(n, edges, stations, prices):
    import heapq
    Z = len(prices); adj = [[] for _ in range(n)]
    for u, v, c, z in edges:
        adj[u].append((v, c, z)); adj[v].append((u, c, z))
    buy = [[] for _ in range(n)]
    for s, z in stations:
        buy[s].append(z)
    INF = float("inf"); dist = [[INF] * (1 << Z) for _ in range(n)]
    dist[0][0] = 0; pq = [(0, 0, 0)]
    while pq:
        d, u, m = heapq.heappop(pq)
        if d > dist[u][m]: continue
        if u == n - 1: return d
        for z in buy[u]:
            nm = m | (1 << z)
            if nm != m and d + prices[z] < dist[u][nm]:
                dist[u][nm] = d + prices[z]; heapq.heappush(pq, (d + prices[z], u, nm))
        for v, c, z in adj[u]:
            nd = d + (0 if z >= 0 and m >> z & 1 else c)
            if nd < dist[v][m]:
                dist[v][m] = nd; heapq.heappush(pq, (nd, v, m))
    return -1


def brute(n, edges, stations, prices):
    # Bellman-Ford style relaxation over (stop, passes) until nothing changes.
    Z = len(prices); INF = float("inf")
    d = {(u, m): INF for u in range(n) for m in range(1 << Z)}; d[(0, 0)] = 0
    changed = True
    while changed:
        changed = False
        for (u, m), du in list(d.items()):
            if du == INF: continue
            moves = []
            for a, b, c, z in edges:
                w = 0 if (z != -1 and (m >> z) & 1) else c
                if a == u: moves.append((b, m, du + w))
                if b == u: moves.append((a, m, du + w))
            for s, z in stations:
                if s == u: moves.append((u, m | (1 << z), du + prices[z]))
            for v, mm, nd in moves:
                if nd < d[(v, mm)]: d[(v, mm)] = nd; changed = True
    best = min(d[(n - 1, m)] for m in range(1 << Z))
    return -1 if best == INF else best


def _gen(rng, n, m, Z, S, cmax):
    edges = [[rng.randrange(n), rng.randrange(n), rng.randint(0, cmax), rng.choice([-1] + list(range(Z)))] for _ in range(m)]
    edges = [e for e in edges if e[0] != e[1]]
    prices = [rng.randint(0, cmax * 2) for _ in range(Z)]
    stations = [[rng.randrange(n), rng.randrange(Z)] for _ in range(S)]
    return (n, edges, stations, prices)


def small(rng):
    return _gen(rng, rng.randint(2, 6), rng.randint(0, 9), rng.randint(1, 3), rng.randint(0, 3), 20)


def fixed():
    return [EXAMPLES[0][0], (2, [], [], [5]), (2, [[0, 1, 7, 0]], [[1, 0]], [1]), (3, [[0, 1, 0, 0], [1, 2, 0, -1]], [], [0])]


def big(rng):
    out = []
    for seed_m in (10000, 6000):
        n = 2000; edges = []
        for i in range(n - 1):  # path so the target is reachable
            edges.append([i, i + 1, rng.randint(0, 10**6), rng.choice([-1, 0, 1, 2, 3])])
        for _ in range(seed_m - (n - 1)):
            u, v = rng.randrange(n), rng.randrange(n)
            if u != v: edges.append([u, v, rng.randint(0, 10**6), rng.choice([-1, 0, 1, 2, 3])])
        stations = [[rng.randrange(n), rng.randrange(4)] for _ in range(50)]
        out.append((n, edges, stations, [rng.randint(0, 10**6) for _ in range(4)]))
    return out


EXAMPLES = [((4, [[0, 1, 5, -1], [1, 2, 100, 0], [2, 3, 100, 0], [0, 3, 250, -1]], [[1, 0]], [30]), 35)]

WRONG = {
    "buy_anywhere": """
def pass_route(n, edges, stations, prices):
    import heapq
    Z = len(prices); best = -1
    for m in range(1 << Z):
        if any(m >> z & 1 and not any(s[1] == z for s in stations) for z in range(Z)): continue
        adj = [[] for _ in range(n)]
        for u, v, c, z in edges:
            w = 0 if z >= 0 and m >> z & 1 else c
            adj[u].append((v, w)); adj[v].append((u, w))
        dist = [None] * n; pq = [(sum(prices[z] for z in range(Z) if m >> z & 1), 0)]
        while pq:
            d, u = heapq.heappop(pq)
            if dist[u] is not None: continue
            dist[u] = d
            for v, w in adj[u]:
                if dist[v] is None: heapq.heappush(pq, (d + w, v))
        if dist[n - 1] is not None and (best < 0 or dist[n - 1] < best): best = dist[n - 1]
    return best
""",
    "no_passes": """
def pass_route(n, edges, stations, prices):
    import heapq
    adj = [[] for _ in range(n)]
    for u, v, c, z in edges: adj[u].append((v, c)); adj[v].append((u, c))
    dist = [None] * n; pq = [(0, 0)]
    while pq:
        d, u = heapq.heappop(pq)
        if dist[u] is not None: continue
        dist[u] = d
        for v, w in adj[u]:
            if dist[v] is None: heapq.heappush(pq, (d + w, v))
    return -1 if dist[n - 1] is None else dist[n - 1]
""",
}
