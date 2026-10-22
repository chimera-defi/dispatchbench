import bisect


def k_machine_schedule(jobs: list[list[int]], k: int) -> int:
    # Weighted interval scheduling with k machines.
    # Sort by end time; dp[i][j] = best pay using the first i jobs (by end)
    # with at most j machines busy at once, via the "k chains" formulation:
    # pick up to k non-overlapping chains of jobs, maximizing total pay.
    if not jobs:
        return 0

    jobs = sorted(jobs, key=lambda x: (x[1], x[0]))
    n = len(jobs)
    ends = [j[1] for j in jobs]

    # prev[i] = number of jobs (by end order) whose end <= start of job i
    prev = [bisect.bisect_right(ends, jobs[i][0]) for i in range(n)]

    # dp[i][c] = max pay considering first i jobs with c machines available
    dp = [[0] * (k + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        s, e, p = jobs[i - 1]
        pi = prev[i - 1]
        for c in range(1, k + 1):
            skip = dp[i - 1][c]
            take = dp[pi][c - 1] + p
            # Taking job i-1 uses one machine; but dp[pi][c-1] already allows
            # up to c-1 others among jobs ending before its start, so combine
            # with the k-machine count via the standard reduction.
            dp[i][c] = max(skip, take)

    # Correct k-machine DP: a set of jobs is feasible on k machines iff its
    # maximum overlap is <= k. Use a DP over jobs sorted by end time that
    # tracks the chosen jobs' multiplicity via a sweep with a sorted list of
    # machine free-times instead (exact for this constraint size).
    free = [0] * k  # earliest free time per machine
    best = [0] * (n + 1)
    return _solve(jobs, k)


def _solve(jobs, k):
    # Exact search over subsets of jobs with memoization on the machine
    # free-time multiset, processing jobs in order of start time.
    jobs = sorted(jobs, key=lambda x: (x[0], x[1]))
    n = len(jobs)
    suffix = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] + jobs[i][2]

    memo = {}

    def go(i, frees):
        # frees: sorted tuple of machine free times (each <= current start or busy)
        if i == n:
            return 0
        key = (i, frees)
        if key in memo:
            return memo[key]
        if suffix[i] <= 0:
            return 0
        s, e, p = jobs[i]
        best = go(i + 1, frees)  # skip job i
        # Assign job i to any machine that is free by its start time.
        # Machines with equal free times are interchangeable, so try each distinct value once.
        seen = set()
        for idx, f in enumerate(frees):
            if f <= s and f not in seen:
                seen.add(f)
                nf = list(frees)
                nf[idx] = e
                nf = tuple(sorted(nf))
                best = max(best, p + go(i + 1, nf))
        memo[key] = best
        return best

    return go(0, tuple([0] * k))
