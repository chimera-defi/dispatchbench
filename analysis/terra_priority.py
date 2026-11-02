"""Appendix: gpt-6.1-terra at the priority tier, the repo track, and the standard-tier noise check (exploratory, PLAN.md deviation 25).

Reads results/2026-11-02-terra-priority-*.jsonl plus the earlier Terra and Sol rows. No model calls.
Prints markdown. Run: python3 -m analysis.terra_priority"""
import json, math, os, statistics
from analysis.summarize import cost, ROOT, money as usd, load

RES = os.path.join(ROOT, "results")
FAST_FN = "2026-11-02-terra-priority-function.jsonl"   # terra61-{low,high}-fast, repeats 1-5
NOISE_FN = "2026-11-02-terra-noise-function.jsonl"     # terra61-{low,high} default tier, repeats 6-15
FAST_AG = "2026-11-02-terra-priority-repo.jsonl"    # repo track: terra61-{low,high}-fast, sol61-high-fast
EARLIER_FN = ["2026-10-28-terra-function.jsonl", "2026-10-22b-function.jsonl"]
Z = 1.959964


def rows(name):
    return load(os.path.join(RES, name))


def wilson(k, n):
    if n == 0: return (0.0, 1.0)
    p = k / n; d = 1 + Z * Z / n; c = p + Z * Z / (2 * n); h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def newcombe(k1, n1, k2, n2):
    """95% interval for p1 - p2 (Newcombe hybrid score)."""
    l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2); p1, p2 = k1 / n1, k2 / n2
    return (p1 - p2 - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), p1 - p2 + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2))


def fisher_two_sided(k1, n1, k2, n2):
    k = k1 + k2; n = n1 + n2
    pmf = lambda a: math.comb(n1, a) * math.comb(n2, k - a) / math.comb(n, k)
    obs = pmf(k1)
    return sum(pmf(a) for a in range(max(0, k - n2), min(n1, k) + 1) if pmf(a) <= obs * (1 + 1e-9))


def pct(x): return f"{100 * x:.1f}%"


def main_ladder(rs, config, reps=None):
    """Main-ladder p01-p12 rows of one config; one row per (problem, repeat), excluding the L7 hard set."""
    from bench import problems
    seen = {}
    for r in rs:
        if r["config"] != config or r["problem"] not in problems.MAIN: continue
        if reps and r["repeat"] not in reps: continue
        seen[(r["problem"], r["repeat"])] = r
    return list(seen.values())


def stats(rs):
    n = len(rs); k = sum(r["passed"] for r in rs); tot = sum(cost(r) or 0 for r in rs)
    return dict(n=n, k=k, ci=wilson(k, n), med=statistics.median(r["wall_s"] for r in rs),
                p90=sorted(r["wall_s"] for r in rs)[int(0.9 * (n - 1))], usd_pass=tot / k if k else None,
                tot=tot, errs=sum(bool(r["is_error"]) for r in rs))


def fn_line(label, s):
    return (f"| {label} | {s['k']}/{s['n']} | {pct(s['k'] / s['n'])} ({pct(s['ci'][0])}–{pct(s['ci'][1])}) | {s['med']:.1f} | {s['p90']:.1f} | "
            f"{usd(s['usd_pass']) if s['usd_pass'] else '–'} | {s['errs']} |")


def function_tables():
    old = [r for f in EARLIER_FN for r in rows(f)]
    fast = rows(FAST_FN); noise = rows(NOISE_FN)
    out = ["## 1. Function track, priority tier (⚡), p01–p12, repeats 1–5", "",
           "| config | passes | pass rate (95% Wilson) | median s | slow-call s | $ per pass (list, ⚡ ×2) | infra errors |", "|---|---|---|---|---|---|---|"]
    sets = [("terra61-low (standard)", main_ladder(old, "terra61-low", range(1, 6))),
            ("terra61-low ⚡", main_ladder(fast, "terra61-low-fast")),
            ("terra61-high (standard)", main_ladder(old, "terra61-high", range(1, 6))),
            ("terra61-high ⚡", main_ladder(fast, "terra61-high-fast")),
            ("sol61-high (standard)", main_ladder(old, "sol61-high", range(1, 6))),
            ("sol61-high ⚡", main_ladder(old, "sol61-high-fast", range(1, 6)))]
    for label, rs in sets:
        if rs: out.append(fn_line(label, stats(rs)))
    out += ["", "## 2. Noise check, standard tier: terra61-low vs terra61-high", "",
            "Reading rule (PLAN.md deviation 25): if the Newcombe interval for the difference contains 0 the gap is noise and no effort level wins on pass rate.", "",
            "| set | terra61-low | terra61-high | low − high (95% Newcombe) | Fisher p |", "|---|---|---|---|---|"]
    for label, reps in (("original repeats 1–5", range(1, 6)), ("new repeats 6–15", range(6, 16)), ("pooled 1–15", range(1, 16))):
        a = main_ladder(old + noise, "terra61-low", reps); b = main_ladder(old + noise, "terra61-high", reps)
        if not a or not b: continue
        ka, kb = sum(r["passed"] for r in a), sum(r["passed"] for r in b); lo, hi = newcombe(ka, len(a), kb, len(b))
        out.append(f"| {label} | {ka}/{len(a)} ({pct(ka / len(a))}; {pct(wilson(ka, len(a))[0])}–{pct(wilson(ka, len(a))[1])}) | "
                   f"{kb}/{len(b)} ({pct(kb / len(b))}; {pct(wilson(kb, len(b))[0])}–{pct(wilson(kb, len(b))[1])}) | "
                   f"{100 * (ka / len(a) - kb / len(b)):+.1f} pts ({100 * lo:+.1f} to {100 * hi:+.1f}) | {fisher_two_sided(ka, len(a), kb, len(b)):.3f} |")
    out += ["", "| pooled 1–15 | median s | slow-call s | $ per pass (list) |", "|---|---|---|---|"]
    for c in ("terra61-low", "terra61-high"):
        s = stats(main_ladder(old + noise, c, range(1, 16)))
        out.append(f"| {c} | {s['med']:.1f} | {s['p90']:.1f} | {usd(s['usd_pass'])} |")
    fails = [(r["config"], r["problem"], r["repeat"], r["outcome"]) for r in old + noise + fast
             if r["config"].startswith("terra61") and not r["passed"] and r["problem"][:3] in {f"p{i:02d}" for i in range(1, 13)}]
    out += ["", "Every terra61 main-ladder miss (config, problem, repeat, outcome): " + ("; ".join(map(str, sorted(fails))) or "none") + "."]
    return out


def repo_tables():
    ag = rows(FAST_AG)
    if not ag: return []
    base = [r for r in rows("2026-10-22b-agentic.jsonl") if r["config"] == "sol61-high"]
    out = ["", "## 3. Repo track (4 tasks, hidden suites)", "",
           "| config | task complete | hidden pass | median s | $ per complete task (list, ⚡ ×2) | misses (task, repeat) |", "|---|---|---|---|---|---|"]
    for label, rs in [(c + " ⚡", [r for r in ag if r["config"] == c]) for c in ("terra61-low-fast", "terra61-high-fast", "sol61-high-fast")] + [("sol61-high (standard, earlier rows)", base)]:
        if not rs: continue
        n = len(rs); done = [bool(r.get("task_complete", r["visible_pass"] and r["hidden_pass"])) for r in rs]; k = sum(done)
        mult = 2 if "⚡" in label else 1
        total = sum((((r["in_tok"] - r["cached_tok"]) * PR(r)["input"] + r["cached_tok"] * PR(r)["cached_input"] + r["out_tok"] * PR(r)["output"]) / 1e6) * mult for r in rs)
        lo, hi = wilson(k, n)
        miss = ", ".join(f"{r['task'][:2]}r{r['repeat']}" for r, ok in zip(rs, done) if not ok) or "none"
        out.append(f"| {label} | {k}/{n} ({pct(k / n)}; {pct(lo)}–{pct(hi)}) | {sum(bool(r['hidden_pass']) for r in rs)}/{n} | "
                   f"{statistics.median(r['wall_s'] for r in rs):.0f} | {usd(total / k) if k else '–'} | {miss} |")
    return out


def PR(r):
    return json.load(open(os.path.join(RES, "prices.json")))["models"][r["model"]]


if __name__ == "__main__":
    print("\n".join(function_tables() + repo_tables()))
