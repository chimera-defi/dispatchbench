"""Hierarchical bootstrap and small helpers. Standard library only."""
import random
import statistics

N_BOOT = 10_000


def hier_boot(cells, n_boot=N_BOOT, seed=0):
    """cells: {problem: [0/1, ...]}. Resample problems, then attempts within each drawn problem.
    Returns (point, lo, hi) for the pooled pass rate, 95% percentile interval."""
    rng = random.Random(seed); keys = sorted(cells)
    point = sum(sum(v) for v in cells.values()) / sum(len(v) for v in cells.values())
    stats = []
    for _ in range(n_boot):
        s = n = 0
        for k in (rng.choice(keys) for _ in keys):
            v = cells[k]
            for _ in v:
                s += v[rng.randrange(len(v))]; n += 1
        stats.append(s / n)
    stats.sort()
    return point, stats[int(0.025 * n_boot)], stats[int(0.975 * n_boot) - 1]


def paired_boot(a, b, n_boot=N_BOOT, seed=0):
    """Difference in pass rate a - b on the problems both have. The same problems are drawn for both configs in each
    resample; attempts are resampled within each config. Returns (point, lo, hi, n_problems)."""
    rng = random.Random(seed); keys = sorted(set(a) & set(b))
    mean = lambda c, ks: sum(sum(c[k]) for k in ks) / sum(len(c[k]) for k in ks)
    point = mean(a, keys) - mean(b, keys); out = []
    for _ in range(n_boot):
        ks = [rng.choice(keys) for _ in keys]
        ra = [a[k][rng.randrange(len(a[k]))] for k in ks for _ in a[k]]
        rb = [b[k][rng.randrange(len(b[k]))] for k in ks for _ in b[k]]
        out.append(sum(ra) / len(ra) - sum(rb) / len(rb))
    out.sort()
    return point, out[int(0.025 * n_boot)], out[int(0.975 * n_boot) - 1], len(keys)


def p90(xs):
    """90th percentile, linear interpolation between order statistics (statistics.quantiles 'inclusive')."""
    return statistics.quantiles(xs, n=10, method="inclusive")[8] if len(xs) > 1 else xs[0]
