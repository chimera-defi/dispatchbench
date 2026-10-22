RUNG = 5
FUNC = "k_machine_schedule"
SIGNATURE = "def k_machine_schedule(jobs: list[list[int]], k: int) -> int:"
STATEMENT = """\
A print shop has `k` identical printers. Job `i` is `[start, end, pay]`: if accepted, it occupies one printer for the half-open time interval `[start, end)` and earns `pay`. Each printer runs at most one job at a time. A job that ends at time `t` and a job that starts at time `t` can use the same printer. Jobs cannot be moved, split or paused.

Return the maximum total pay of a set of jobs that can all be accepted.

Examples:
- `k_machine_schedule([[0, 4, 5], [1, 3, 4], [3, 6, 4]], 1)` returns `8`.
- `k_machine_schedule([[0, 10, 9], [0, 5, 5], [5, 10, 5], [0, 10, 1]], 2)` returns `19`.

Constraints: `0 <= len(jobs) <= 300`, `1 <= k <= 10`, `0 <= start < end <= 10**9`, `1 <= pay <= 10**6`."""


def ref(jobs, k):
    # Min-cost flow on the time line: k units flow left to right; a job edge skips ahead at cost -pay.
    pts = sorted({t for s, e, _ in jobs for t in (s, e)})
    if not pts: return 0
    idx = {t: i for i, t in enumerate(pts)}; N = len(pts) + 2; S, T = N - 2, N - 1
    graph = [[] for _ in range(N)]

    def edge(u, v, cap, cost):
        graph[u].append([v, cap, cost, len(graph[v])]); graph[v].append([u, 0, -cost, len(graph[u]) - 1])
    edge(S, 0, k, 0); edge(len(pts) - 1, T, k, 0)
    for i in range(len(pts) - 1): edge(i, i + 1, k, 0)
    for s, e, p in jobs: edge(idx[s], idx[e], 1, -p)
    total = 0
    while True:  # successive shortest paths with Bellman-Ford (SPFA); graph stays free of negative cycles
        from collections import deque
        INF = float("inf"); dist = [INF] * N; inq = [False] * N; prev = [None] * N; dist[S] = 0; q = deque([S])
        while q:
            u = q.popleft(); inq[u] = False
            for j, (v, cap, cost, _) in enumerate(graph[u]):
                if cap > 0 and dist[u] + cost < dist[v]:
                    dist[v] = dist[u] + cost; prev[v] = (u, j)
                    if not inq[v]: inq[v] = True; q.append(v)
        if dist[T] == INF or dist[T] >= 0: break
        f = INF; v = T
        while v != S:
            u, j = prev[v]; f = min(f, graph[u][j][1]); v = u
        v = T
        while v != S:
            u, j = prev[v]; graph[u][j][1] -= f; r = graph[u][j][3]; graph[v][r][1] += f; v = u
        total += -dist[T] * f
    return total


def brute(jobs, k):
    best = 0; n = len(jobs)
    for mask in range(1 << n):
        chosen = [jobs[i] for i in range(n) if mask >> i & 1]
        ev = sorted([(s, 1) for s, _, _ in chosen] + [(e, -1) for _, e, _ in chosen], key=lambda x: (x[0], x[1]))
        cur = peak = 0
        for _, d in ev:
            cur += d; peak = max(peak, cur)
        if peak <= k: best = max(best, sum(p for _, _, p in chosen))
    return best


def small(rng):
    n = rng.randint(0, 9); jobs = []
    for _ in range(n):
        s = rng.randint(0, 12); jobs.append([s, s + rng.randint(1, 6), rng.randint(1, 10)])
    return (jobs, rng.randint(1, 3))


def fixed():
    return [a for a, _ in EXAMPLES] + [([], 3), ([[0, 1, 5]], 1), ([[0, 2, 3], [2, 4, 3], [1, 3, 5]], 1), ([[0, 2, 3], [2, 4, 3], [1, 3, 5]], 2)]


def big(rng):
    out = []
    for k in (1, 3, 10):
        jobs = []
        for _ in range(300):
            s = rng.randint(0, 10**9 - 1); jobs.append([s, min(10**9, s + rng.randint(1, 10**8)), rng.randint(1, 10**6)])
        out.append((jobs, k))
    return out


EXAMPLES = [(([[0, 4, 5], [1, 3, 4], [3, 6, 4]], 1), 8), (([[0, 10, 9], [0, 5, 5], [5, 10, 5], [0, 10, 1]], 2), 19)]

WRONG = {
    "greedy_by_pay": """
def k_machine_schedule(jobs, k):
    chosen = []
    for s, e, p in sorted(jobs, key=lambda j: -j[2]):
        trial = chosen + [(s, e, p)]
        ev = sorted([(a, 1) for a, _, _ in trial] + [(b, -1) for _, b, _ in trial], key=lambda x: (x[0], x[1]))
        cur = peak = 0
        for _, d in ev: cur += d; peak = max(peak, cur)
        if peak <= k: chosen = trial
    return sum(p for _, _, p in chosen)
""",
    "repeat_single_machine_dp": """
def k_machine_schedule(jobs, k):
    import bisect
    left = list(jobs); total = 0
    for _ in range(k):
        js = sorted(left, key=lambda j: j[1]); ends = [j[1] for j in js]; n = len(js)
        dp = [0] * (n + 1); take = [False] * (n + 1)
        for i in range(1, n + 1):
            s, e, p = js[i - 1]; q = bisect.bisect_right(ends, s, 0, i - 1)
            if dp[q] + p > dp[i - 1]: dp[i] = dp[q] + p; take[i] = True
            else: dp[i] = dp[i - 1]
        total += dp[n]; used = set(); i = n
        while i > 0:
            if take[i]:
                used.add(i - 1); i = bisect.bisect_right(ends, js[i - 1][0], 0, i - 1)
            else: i -= 1
        left = [js[i] for i in range(n) if i not in used]
    return total
""",
}
