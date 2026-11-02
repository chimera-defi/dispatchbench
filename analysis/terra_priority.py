"""Appendix: gpt-6.1-terra priority, noise check and follow-up (exploratory, PLAN.md deviations 25–26).

Reads results/2026-11-02-terra-*.jsonl plus the earlier Terra and Sol rows. No model calls.
Prints markdown. Run: python3 -m analysis.terra_priority"""
import json, math, os, statistics
from analysis.summarize import cost, ROOT, money as usd, load

RES = os.path.join(ROOT, "results")
FAST_FN = "2026-11-02-terra-priority-function.jsonl"   # terra61-{low,high}-fast, repeats 1-5
NOISE_FN = "2026-11-02-terra-noise-function.jsonl"     # terra61-{low,high} default tier, repeats 6-15
FAST_AG = "2026-11-02-terra-priority-repo.jsonl"    # repo track: terra61-{low,high}-fast, sol61-high-fast
L7_FAST_FN = "2026-11-02-terra-l7-fast-function.jsonl"
FOLLOWUP_FN = "2026-11-02-terra-followup-function.jsonl"
FOLLOWUP_AG = "2026-11-02-terra-followup-repo.jsonl"
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


def page_summary():
    """Structured evidence for the main page, separate from its 60-try population."""
    old = [r for f in EARLIER_FN for r in rows(f)]
    noise, priority = rows(NOISE_FN), rows(FAST_FN)
    arms = ("terra61-low", "terra61-high")
    pooled = {c: stats(main_ladder(old + noise, c, range(1, 16))) for c in arms}
    standard = {c: stats(main_ladder(old, c, range(1, 6))) for c in arms}
    fast = {c: stats(main_ladder(priority, c + "-fast", range(1, 6))) for c in arms}
    a, b = (pooled[c] for c in arms)
    followup = {}
    for label, group in followup_sets().items():
        followup[label] = {}
        for c, rr in group.items():
            if label == "repo":
                rr = [dict(r, passed=bool(r.get("task_complete", r["visible_pass"] and r["hidden_pass"]))) for r in rr]
            followup[label][c] = stats(rr)
    p, q = (followup["p04"][c] for c in ("terra61-low", "sol61-high"))
    return dict(pooled=pooled, standard=standard, fast=fast, followup=followup,
                l7_fast=stats(rows(L7_FAST_FN)),
                noise_interval=newcombe(a["k"], a["n"], b["k"], b["n"]),
                p04_interval=newcombe(p["k"], p["n"], q["k"], q["n"]),
                time_cuts=[100 * (1 - fast[c]["med"] / standard[c]["med"]) for c in arms],
                sol_fast=stats(main_ladder(old, "sol61-high-fast", range(1, 6))))


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
    out += ["", "Every terra61 main-ladder miss in the deviation-25 comparison sets (config, problem, repeat, outcome): " + ("; ".join(map(str, sorted(fails))) or "none") + "."]
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


def standard_rows(rs, config, field, items):
    """Pool distinct standard-tier calls, including Sol's phase=fastmode control.

    Phase names do not identify service tier: sol61-high repeats 6–10 are
    standard-tier controls; sol61-high-fast is the separate priority arm.
    """
    return list({r["key"]: r for r in rs if r["config"] == config
                 and r[field] in items and r.get("service_tier", "default") == "default"}.values())


def followup_sets():
    from bench import problems
    fn = [r for f in EARLIER_FN + [NOISE_FN, FOLLOWUP_FN] for r in rows(f)]
    ag = rows("2026-10-22b-agentic.jsonl") + rows(FOLLOWUP_AG)
    sets = {}
    for label, source, field, items in (("L7", fn, "problem", problems.HARD),
                                        ("repo", ag, "task", {"t1_discount", "t2_cache_bugs", "t3_config_refs", "t4_retry_queue"}),
                                        ("p04", fn, "problem", {"p04_taller_within"})):
        sets[label] = {}
        for c in ("terra61-low", "terra61-high", "sol61-high"):
            rr = standard_rows(source, c, field, items)
            expected = {"L7": 15, "repo": 12 if c == "sol61-high" else 20,
                        "p04": 30 if c == "sol61-high" else 35}[label]
            if len(rr) != expected:
                raise ValueError(f"deviation 26 {label}/{c}: expected {expected} rows, got {len(rr)}")
            sets[label][c] = rr
    return sets


def followup_tables():
    sets = followup_sets()
    out = ["", "## 4. Follow-up: L7, standard tier (exploratory, deviation 26)", "",
           "Terra p13–p15 repeats 1–5 against existing sol61-high L7 repeats 1–5. Function-test grading is unchanged.", "",
           "| config | passes | pass rate (95% Wilson) | median s | slow-call s | $ per pass (list) | infra errors |",
           "|---|---|---|---|---|---|---|"]
    for c, rr in sets["L7"].items():
        out.append(fn_line(c, stats(rr)))
    out += ["", "## Follow-up: L7 at priority tier (deviation 27)", "",
            "| config | passes | pass rate (95% Wilson) | median s | slow-call s | $ per pass (list, ⚡ ×2) | infra errors |",
            "|---|---|---|---|---|---|---|", fn_line("terra61-low ⚡", stats(rows(L7_FAST_FN)))]
    out += ["", "## 5. Follow-up: repo track, standard tier (exploratory, deviation 26)", "",
            "Terra t1–t4 repeats 1–5 against earlier default-tier sol61-high repeats 1–3. Cached hidden-suite verdicts; task complete requires visible and hidden passes.", "",
            "| config | task complete | hidden pass | median s | $ per complete task (list) | misses (task, repeat) |",
            "|---|---|---|---|---|---|"]
    for c, rr in sets["repo"].items():
        done = [dict(r, passed=bool(r.get("task_complete", r["visible_pass"] and r["hidden_pass"]))) for r in rr]
        s = stats(done)
        miss = ", ".join(f"{r['task'][:2]}r{r['repeat']}" for r in done if not r["passed"]) or "none"
        out.append(f"| {c} | {s['k']}/{s['n']} ({pct(s['k'] / s['n'])}; {pct(s['ci'][0])}–{pct(s['ci'][1])}) | "
                   f"{sum(bool(r['hidden_pass']) for r in rr)}/{s['n']} | {s['med']:.1f} | {usd(s['usd_pass']) if s['k'] else '–'} | {miss} |")
    out += ["", "## 6. Follow-up: p04 weak spot, all standard-tier rows (exploratory, deviation 26)", "",
            "Terra repeats 1–35; Sol repeats 1–30, including standard-tier phase=fastmode control repeats 6–10. Distinct call keys only; priority configs excluded.", "",
            "| config | passes | pass rate (95% Wilson) | median s | slow-call s | $ per pass (list) | infra errors |",
            "|---|---|---|---|---|---|---|"]
    for c, rr in sets["p04"].items():
        out.append(fn_line(c, stats(rr)))
    a, b = (stats(sets["p04"][c]) for c in ("terra61-low", "sol61-high"))
    lo, hi = newcombe(a["k"], a["n"], b["k"], b["n"])
    verdict = "real" if lo > 0 or hi < 0 else "not established as real"
    out += ["", f"terra61-low − sol61-high: {100 * (a['k'] / a['n'] - b['k'] / b['n']):+.1f} points; "
            f"95% Newcombe interval {100 * lo:+.1f} to {100 * hi:+.1f} points. "
            f"Per the fixed reading rule, the p04 weak spot is **{verdict}** "
            f"(the interval {'excludes' if lo > 0 or hi < 0 else 'contains'} 0)."]
    fn, ag = rows(FOLLOWUP_FN), rows(FOLLOWUP_AG)
    spend = {"L7": sum(cost(r) for r in fn if r["rung"] == 7),
             "repo": sum(cost(r) for r in ag),
             "p04": sum(cost(r) for r in fn if r["problem"] == "p04_taller_within")}
    total = sum(spend.values())
    out += ["", "## 7. Deviation-26 spend (list price)", "",
            f"90 new function calls + 40 repo runs: L7 ${spend['L7']:.6f}, repo ${spend['repo']:.6f}, "
            f"p04 ${spend['p04']:.6f}; total **${total:.6f}** against the $6 cap "
            f"(${6 - total:.6f} remaining). Earlier comparison rows are excluded. "
            "Token prices come from results/prices.json, with cached-input discounts; every new row is default tier."]
    return out


if __name__ == "__main__":
    print("\n".join(function_tables() + repo_tables() + followup_tables()))
