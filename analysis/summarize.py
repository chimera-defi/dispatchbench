"""Turn results/*.jsonl into results/summary.json and results/report/tables.md. No model calls.

Every number in the README and the report comes from summary.json, and every summary.json number is computed here
from rows in results/. Codex dollar figures are proxies (token counts x list price); Claude dollar figures are the
CLI's measured total_cost_usd."""
import json, os, statistics
from collections import defaultdict

from analysis.stats import hier_boot, paired_boot, p90
from analysis.labels import DISP, plabel, pshort

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
FUNC = os.path.join(RES, "2026-10-22b-function.jsonl")
AGENT = os.path.join(RES, "2026-10-22b-agentic.jsonl")
PILOT = os.path.join(RES, "2026-10-22-pilot.jsonl")
TRIM = os.path.join(RES, "2026-10-22b-trim.jsonl")
BASE = ["haiku-low", "haiku-medium", "sonnet-medium", "luna-low", "luna-medium", "sol61-medium"]
ESCALATE = {"haiku-high": "haiku-medium", "sonnet-high": "sonnet-medium", "luna-high": "luna-medium", "sol61-high": "sol61-medium"}
PAIRS = [("haiku-medium", "haiku-low"), ("luna-medium", "luna-low"), ("sonnet-medium", "haiku-medium"),
         ("sol61-medium", "luna-medium"), ("haiku-low", "luna-low"), ("sonnet-medium", "sol61-medium")]
BREAK_AT = 0.40


def load(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


PRICES = json.load(open(os.path.join(RES, "prices.json")))["models"]


FAST_CONFIGS = ("sol61-high-fast", "astra-medium-fast")  # Codex priority tier: billed at the published fast-mode multiplier


def cost(r):
    """Cost with the fast-mode multiplier applied to priority-tier configs; list_cost is the unscaled price."""
    return scale(list_cost(r), fast_mult(r))


def list_cost(r):
    """Measured for Claude; proxy for Codex (uncached input, cached input and output at list price)."""
    if r["cli"].startswith("claude"):  # "claude" and the pilot's "claude-agent"
        return r.get("cost_usd")
    if r.get("is_error"): return None
    p = PRICES[r["model"]]
    return ((r["in_tok"] - r["cached_tok"]) * p["input"] + r["cached_tok"] * p["cached_input"] + r["out_tok"] * p["output"]) / 1e6


def cost_uncached(r):
    """Codex proxy with no prompt-cache discount: an upper bound that does not depend on how many tokens the provider cached."""
    return scale(_uncached(r), fast_mult(r))


def _uncached(r):
    if r["cli"].startswith("claude"):  # "claude" and the pilot's "claude-agent"
        return r.get("cost_usd")
    if r.get("is_error"): return None
    p = PRICES[r["model"]]
    return (r["in_tok"] * p["input"] + r["out_tok"] * p["output"]) / 1e6


def usd(values, divisor=1, digits=6):
    values = list(values)
    if not divisor or any(v is None for v in values): return None
    total = sum(values) / divisor
    return round(total, digits) if digits is not None else total


def money(value, digits=5):
    return "unknown" if value is None else f"{value:.{digits}f}"


def scale(value, factor):
    return None if value is None else value * factor


def ci_text(k, n, ci, clusters):
    """Bootstrap CI, except when every attempt passed: the bootstrap then collapses to 100-100, so report the exact
    one-sided 95% lower bound 0.05^(1/m) over the m problems or tasks. Using clusters, not attempts, keeps it conservative
    when attempts at one problem are correlated."""
    if n and k == n:
        return f"≥{pct(0.05 ** (1 / clusters))} (all passed)"
    return f"{pct(ci[0])}–{pct(ci[1])}"


def cells(rows, rungs=None):
    c = defaultdict(list)
    for r in rows:
        if rungs is None or r["rung"] in rungs:
            c[r["problem"]].append(1 if r["passed"] else 0)
    return dict(c)


def config_block(rows):
    walls = [r["wall_s"] for r in rows]; dollars = [cost(r) for r in rows]; passes = sum(r["passed"] for r in rows)
    pt, lo, hi = hier_boot(cells(rows))
    by_rung = {}
    for g in sorted({r["rung"] for r in rows}):
        rr = [r for r in rows if r["rung"] == g]
        by_rung[f"L{g}"] = {"passed": sum(r["passed"] for r in rr), "n": len(rr)}
    broke = next((k for k, v in by_rung.items() if v["passed"] / v["n"] <= BREAK_AT), None)
    outcomes = defaultdict(int)
    for r in rows: outcomes[r["outcome"]] += 1
    l12 = [r for r in rows if r["rung"] in (1, 2)]
    return {
        "cli": rows[0]["cli"], "model": rows[0]["model"], "effort": rows[0]["effort"], "n": len(rows), "passes": passes,
        "pass_at_1": round(pt, 4), "ci95": [round(lo, 4), round(hi, 4)], "by_rung": by_rung, "breaking_point": broke,
        "outcomes": dict(outcomes),
        "latency_s": {"median": round(statistics.median(walls), 2), "p25": round(statistics.quantiles(walls, n=4)[0], 2), "p75": round(statistics.quantiles(walls, n=4)[2], 2), "p90": round(p90(walls), 2), "max": round(max(walls), 2)},
        "tokens_mean": {k: round(statistics.mean(r[k] or 0 for r in rows)) for k in ("in_tok", "cached_tok", "out_tok", "reasoning_tok")},
        "input_floor": min((r["in_tok"], r["cached_tok"]) for r in rows),
        "usd_per_call": usd(dollars, len(dollars)), "usd_total": usd(dollars, digits=4),
        "usd_per_pass": usd(dollars, passes),
        "usd_per_pass_L1_L2": usd(map(cost, l12), sum(r["passed"] for r in l12)) if l12 and any(r["passed"] for r in l12) else None,
        "pass_L1_L2": [sum(r["passed"] for r in l12), len(l12)],
        "cost_kind": "measured" if rows[0]["cli"] == "claude" else "proxy",
    }


def pareto(points):
    """Configs not dominated on ($ per pass, pass@1): no other config is at least as cheap and at least as accurate,
    and strictly better on one of the two."""
    out = []
    for a, (x, y) in points.items():
        if not any((x2 <= x and y2 >= y) and (x2 < x or y2 > y) for b, (x2, y2) in points.items() if b != a):
            out.append(a)
    return sorted(out, key=lambda k: points[k][0])


def agentic_block(rows):
    out = {}
    for c in sorted({r["config"] for r in rows}):
        rr = [r for r in rows if r["config"] == c]
        by_task = {}
        for t in sorted({r["task"] for r in rr}):
            tt = [r for r in rr if r["task"] == t]
            by_task[t] = {"hidden_pass": sum(r["hidden_pass"] for r in tt), "n": len(tt),
                          "hidden_tests": [f"{r['hidden']['passed']}/{r['hidden']['passed'] + r['hidden']['failed']}" for r in tt]}
        pt, lo, hi = hier_boot({t: [1 if r["hidden_pass"] else 0 for r in rr if r["task"] == t] for t in by_task})
        dollars = [cost(r) for r in rr]; walls = [r["wall_s"] for r in rr]
        out[c] = {
            "cli": rr[0]["cli"], "model": rr[0]["model"], "n": len(rr), "hidden_pass": sum(r["hidden_pass"] for r in rr),
            "hidden_pass_rate": round(pt, 4), "ci95": [round(lo, 4), round(hi, 4)],
            "visible_pass": sum(r["visible_pass"] for r in rr), "task_complete": sum(r.get("task_complete", r["visible_pass"] and r["hidden_pass"]) for r in rr), "own_tests_written": sum(r["own_tests"] for r in rr),
            "tests_tampered_runs": sum(bool(r["tests_tampered"]) for r in rr), "delegate_calls": sum(r.get("delegate_calls") or 0 for r in rr),
            "errors": sum(r["is_error"] for r in rr), "by_task": by_task,
            "latency_s": {"median": round(statistics.median(walls), 1), "p90": round(p90(walls), 1)},
            "input_floor": min((r["in_tok"], r["cached_tok"]) for r in rr),
            "tokens_mean": {k: round(statistics.mean(r[k] or 0 for r in rr)) for k in ("in_tok", "cached_tok", "out_tok")},
            "usd_per_run": usd(dollars, len(dollars), 5), "usd_total": usd(dollars, digits=4),
            "usd_per_hidden_pass": usd(dollars, sum(r["hidden_pass"] for r in rr), 5) if any(r["hidden_pass"] for r in rr) else None,
            "cost_kind": "measured" if rr[0]["cli"] == "claude" else "proxy",
        }
    return out


def failures(rows):
    """Problems x configs, for every problem at least one config failed at least once. Each cell: passes, attempts and
    the outcome of each failed attempt (wrong answer, crash, timeout, no code)."""
    order = BASE + sorted({r["config"] for r in rows} - set(BASE))
    out = {}
    for p in sorted({r["problem"] for r in rows}):
        pr = [r for r in rows if r["problem"] == p]
        if all(r["passed"] for r in pr): continue
        cell = {}
        for c in order:
            cr = [r for r in pr if r["config"] == c]
            if cr:
                fails = defaultdict(int)
                for r in cr:
                    if not r["passed"]: fails[r["outcome"]] += 1
                cell[c] = {"passed": sum(r["passed"] for r in cr), "n": len(cr), "fails": dict(fails)}
        out[p] = {"rung": pr[0]["rung"], "cells": cell}
    return out


def pilot_reprice():
    """The pilot priced priority-tier Codex rows at 1.5x list; the published multiplier is 2x. Recompute both."""
    mult = json.load(open(os.path.join(RES, "prices.json")))["fast_mode_multiplier"]
    rows = [r for r in load(PILOT) if r["cli"] == "codex" and "priority" in (r.get("service_tier") or "") and r["model"] in PRICES]
    base = sum(cost(r) for r in rows)
    return {"rows": len(rows), "usd_at_1_5x": round(1.5 * base, 4), "usd_at_2x": round(mult * base, 4), "multiplier_source": "results/prices.json"}


def pilot_block():
    """Pilot (2026-10-22) per config. Each cell carries its n; n differs between configs (3 to 19 runs), so the table flags n != 9."""
    rows = load(PILOT); out = {}
    mult = json.load(open(os.path.join(RES, "prices.json")))["fast_mode_multiplier"]
    for c in dict.fromkeys(r["config"] for r in rows):
        rr = [r for r in rows if r["config"] == c]
        prio = rr[0]["cli"].startswith("codex") and (rr[0].get("service_tier") or "").startswith("priority")
        dollars = [r["cost_usd"] if r["cli"].startswith("claude") else scale(cost(r), mult if prio else 1) for r in rr]
        out[c] = {"cli": rr[0]["cli"], "model": rr[0]["model"], "effort": rr[0]["effort"], "passes": sum(bool(r["passed"]) for r in rr), "n": len(rr),
                  "problems": len({r["problem"] for r in rr}), "service_tier": rr[0].get("service_tier"), "ladder": rr[0]["phase"] == "ladder",
                  "input_floor": min(r["in_tok"] for r in rr), "median_s": round(statistics.median(r["wall_s"] for r in rr), 2),
                  "usd_per_call": usd(dollars, len(dollars))}
    return out


def pilot_fast():
    """Codex fast mode (priority tier) against the default tier: same model, harness and pilot problems, 3 rounds each."""
    rows = load(PILOT); mult = json.load(open(os.path.join(RES, "prices.json")))["fast_mode_multiplier"]
    probs = {r["problem"] for r in rows if r["config"] == "sol61-low-defa"}; out = {}
    for name, d, f in (("sol61-low", "sol61-low-defa", "sol61-low-prio"), ("luna-low", "luna-low-defa", "luna-low")):
        for tier, c, m in (("default", d, 1), ("fast", f, mult)):
            rr = [r for r in rows if r["config"] == c and r["problem"] in probs]
            out[f"{name}/{tier}"] = {"passes": sum(bool(r["passed"]) for r in rr), "n": len(rr), "median_s": round(statistics.median(r["wall_s"] for r in rr), 2),
                                     "usd_per_call": usd((scale(cost(r), m) for r in rr), len(rr))}
    return out


def fast_mult(r):
    """Priority-tier (fast mode) calls bill at the published multiplier."""
    return json.load(open(os.path.join(RES, "prices.json")))["fast_mode_multiplier"] if r["config"] in FAST_CONFIGS else 1


def fastmode_block(rows):
    """sol61-high in fast mode (priority tier) and at xhigh effort on the rescue set, against a default-tier sol61-high control run alongside them (repeats 6-10)."""
    mult = json.load(open(os.path.join(RES, "prices.json")))["fast_mode_multiplier"]; out = {}
    for c in ("sol61-high", "sol61-high-fast", "sol61-xhigh"):
        rr = [r for r in rows if r["phase"] == "fastmode" and r["config"] == c]
        if not rr: continue
        ps = sum(r["passed"] for r in rr)
        out[c] = {"passes": ps, "n": len(rr), "repeats": sorted({r["repeat"] for r in rr}), "median_s": round(statistics.median(r["wall_s"] for r in rr), 2),
                  "out_median": statistics.median(r["out_tok"] for r in rr), "usd_per_pass": usd(map(cost, rr), ps),
                  "usd_per_pass_list": usd(map(list_cost, rr), ps)}
    return out


def trim_block():
    """Codex input-floor probe on the pilot problems: per trim level, and the 3x3 pair step against haiku-low (tools off)."""
    rows = load(TRIM); out = {"floor": {}, "pair": {}}
    for r in rows:
        if r["step"] == "floor":
            out["floor"][r["config"]] = {"in_tok": r["in_tok"], "cached_tok": r["cached_tok"], "passed": r["passed"]}
    for c in dict.fromkeys(r["config"] for r in rows if r["step"] == "pair"):
        # the floor step's fizzbuzz round-1 call has the same cache key as the pair step's, so it is the same call and counts here
        rr = [r for r in rows if r["config"] == c]; dollars = [cost(r) for r in rr]
        out["pair"][c] = {"cli": rr[0]["cli"], "model": rr[0]["model"], "level": rr[0].get("level"), "passes": sum(r["passed"] for r in rr), "n": len(rr),
                          "errors": sum(bool(r["is_error"]) for r in rr), "uncached_calls": sum(r["cached_tok"] == 0 for r in rr), "in_median": round(statistics.median(r["in_tok"] for r in rr)),
                          "in_min": min(r["in_tok"] for r in rr), "cached_median": round(statistics.median(r["cached_tok"] or 0 for r in rr)),
                          "out_median": round(statistics.median(r["out_tok"] for r in rr)), "median_s": round(statistics.median(r["wall_s"] for r in rr), 2),
                          "p90_s": round(p90([r["wall_s"] for r in rr]), 2), "usd_per_call": usd(dollars, len(dollars)),
                          "cost_kind": "measured" if rr[0]["cli"] == "claude" else "proxy"}
    return out


def build():
    """Everything summarize writes, computed in memory: (summary, tables.md text, manifest). make audit calls this too."""
    rows = load(FUNC); agent = load(AGENT)
    main_rows = [r for r in rows if r["phase"] == "main"]
    s = {"generated_from": [os.path.relpath(p, ROOT) for p in (FUNC, AGENT) if os.path.exists(p)], "configs": {}, "phases": {}}
    for ph in sorted({r["phase"] for r in rows}):
        s["phases"][ph] = len([r for r in rows if r["phase"] == ph])
    for c in BASE:
        rr = [r for r in main_rows if r["config"] == c]
        if rr: s["configs"][c] = config_block(rr)
    s["problems"] = {}
    for p in sorted({r["problem"] for r in main_rows}):
        s["problems"][p] = {"rung": next(r["rung"] for r in main_rows if r["problem"] == p),
                            **{c: sum(r["passed"] for r in main_rows if r["problem"] == p and r["config"] == c) for c in BASE}}
    s["paired"] = []
    for a, b in PAIRS:
        ca = cells([r for r in main_rows if r["config"] == a]); cb = cells([r for r in main_rows if r["config"] == b])
        if ca and cb:
            d, lo, hi, n = paired_boot(ca, cb)
            s["paired"].append({"a": a, "b": b, "diff": round(d, 4), "ci95": [round(lo, 4), round(hi, 4)], "problems": n})
    esc = [r for r in rows if r["phase"] == "escalation"]
    s["escalation"] = []
    for c in sorted({r["config"] for r in esc}):
        er = [r for r in esc if r["config"] == c]; probs = sorted({r["problem"] for r in er}); base = ESCALATE[c]
        br = [r for r in main_rows if r["config"] == base and r["problem"] in probs]
        d, lo, hi, n = paired_boot(cells(er), cells(br))
        s["escalation"].append({"config": c, "vs": base, "problems": probs, "passes": sum(r["passed"] for r in er), "n": len(er),
                                "base_passes": sum(r["passed"] for r in br), "base_n": len(br), "diff": round(d, 4), "ci95": [round(lo, 4), round(hi, 4)],
                                "median_latency_s": round(statistics.median(r["wall_s"] for r in er), 2),
                                "usd_total": usd(map(cost, er), digits=4), "cost_kind": "measured" if er[0]["cli"] == "claude" else "proxy"})
    xr = [r for r in rows if r["phase"] == "exploratory"]
    s["exploratory"] = {}
    for c in sorted({r["config"] for r in xr}):
        # an exploratory config that the escalation step already ran on some problems reuses those cached calls
        rr = [r for r in rows if r["config"] == c and (r["phase"] in ("exploratory", "escalation") or (r["phase"] == "fastmode" and c == "sol61-high-fast"))]; blk = config_block(rr); blk["vs"] = []
        for base in ("luna-low", "haiku-low", "luna-medium"):
            cb = cells([r for r in main_rows if r["config"] == base])
            if cb:
                d, lo, hi, n = paired_boot(cells(rr), cb)
                blk["vs"].append({"b": base, "diff": round(d, 4), "ci95": [round(lo, 4), round(hi, 4)], "problems": n})
        er = [r for r in rr if r["passed"]]
        blk["usd_per_pass_uncached"] = usd(map(cost_uncached, rr), len(er))
        blk["by_problem"] = {p: sum(r["passed"] for r in rr if r["problem"] == p) for p in sorted({r["problem"] for r in rr})}  # heatmap columns
        s["exploratory"][c] = blk
    hr = [r for r in rows if r["phase"] == "hard"]
    s["hard"] = {}
    for c in sorted({r["config"] for r in hr}, key=lambda c: (-sum(r["passed"] for r in hr if r["config"] == c), c)):
        rr = [r for r in hr if r["config"] == c]; blk = config_block(rr)
        blk["by_problem"] = {p: sum(r["passed"] for r in rr if r["problem"] == p) for p in sorted({r["problem"] for r in rr})}
        s["hard"][c] = blk
    s["failures"] = failures([r for r in rows if r["phase"] in ("main", "exploratory", "escalation", "hard")])
    cfg = s["configs"]
    s["pareto"] = pareto({c: (v["usd_per_pass"], v["pass_at_1"]) for c, v in cfg.items() if v["usd_per_pass"]})
    s["agentic"] = agentic_block(agent) if agent else {}
    s["pilot_reprice"] = pilot_reprice()
    s["pilot"] = pilot_block()
    s["pilot_fast"] = pilot_fast()
    s["trim"] = trim_block()
    s["fastmode"] = fastmode_block(rows)
    claude_all = [r for r in rows if r["cli"] == "claude"] + [r for r in agent if r["cli"] == "claude"]
    s["spend"] = {"claude_measured_usd": usd((r.get("cost_usd") for r in claude_all), digits=4),
                  "claude_function_usd": usd((r.get("cost_usd") for r in rows if r["cli"] == "claude"), digits=4),
                  "claude_agentic_usd": usd((r.get("cost_usd") for r in agent if r["cli"] == "claude"), digits=4),
                  "codex_proxy_usd": usd((cost(r) for r in rows + agent if r["cli"] == "codex"), digits=4),
                  "codex_fastmode_usd": usd((cost(r) for r in rows if r["phase"] == "fastmode"), digits=4),
                  "calls": {"function": len(rows), "agentic": len(agent)}}
    s["hypotheses"] = hypotheses(s)
    return s, tables(s), manifest(rows, agent, s)


def main():
    s, tab, man = build()
    json.dump(s, open(os.path.join(RES, "summary.json"), "w"), indent=1)
    os.makedirs(os.path.join(RES, "report"), exist_ok=True)
    open(os.path.join(RES, "report", "tables.md"), "w").write(tab)
    json.dump(man, open(os.path.join(RES, "manifest.json"), "w"), indent=1)
    print(f"summary: {s['phases'].get('main', 0)} main rows, {s['phases'].get('escalation', 0)} escalation rows, {len(load(AGENT))} agentic rows -> results/summary.json, results/report/tables.md")


def manifest(rows, agent, s):
    """What produced the rows: CLI versions, harness flags, models, lanes, dates, call counts, errors (verbatim)."""
    from bench import run as R
    from bench.agentic import run as A
    allr = rows + agent
    errs = [{"key": r["key"][:12], "config": r["config"], "error": r["error"]} for r in allr if r.get("is_error") or r.get("error")]
    out = {"experiment": "2026-10-22b", "pre_registration": "PLAN.md (committed before any model call)",
            "cli_versions": sorted({f"{r['cli']} {r['cli_version']}" for r in allr}),
            "configs": {c: {"cli": v[0], "model": v[1], "effort": v[2]} for c, v in R.CONFIGS.items() if any(r["config"] == c for r in allr)},
            "flags": {"function": {"claude": R.CLAUDE_FLAGS, "codex": R.CODEX_FLAGS}, "agentic": {"claude": A.CLAUDE_FLAGS, "codex": A.CODEX_FLAGS}},
            "lanes": sorted({r["lanes"] for r in allr if r.get("lanes")}),
            "first_call_utc": min(r["ts"] for r in allr) if allr else None, "last_call_utc": max(r["ts"] for r in allr) if allr else None,
            "rows_by_phase": s["phases"], "agentic_runs": len(agent), "claude_budget_cap_usd": R.CLAUDE_BUDGET_USD, "spend": s["spend"],
            "errors": errs, "prices": "results/prices.json", "exploratory": exploratory_manifest()}
    sha = git_sha()
    if sha: out["git_sha"] = sha
    return out


def git_sha():
    import subprocess
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def exploratory_manifest():
    """Provenance for exploratory inputs, including the post-hoc appendix and pilots."""
    import glob
    from bench.plan_first import BUILDERS, PLANNER
    from bench.gated_repair import CONFIGS

    def entry(path, rows, script, configs=None, models=None):
        if configs is None:
            configs = {r["config"] for r in rows if r.get("config")}
            if not configs:
                configs = {"/".join(x for x in (r.get("pipeline"), r.get("builder")) if x) for r in rows}
        out = {"file": os.path.relpath(path, ROOT), "configs": sorted(configs),
               "producing_script": script}
        if any("ts" in r for r in rows):
            stamps = [r["ts"] for r in rows if r.get("ts")]
            if stamps:
                from datetime import datetime
                stamp_key = lambda x: datetime.fromisoformat(x.replace("Z", "+00:00"))
                out.update(first_timestamp=min(stamps, key=stamp_key), last_timestamp=max(stamps, key=stamp_key))
        versions = sorted({f"{k}={r[k]}" for r in rows for k in ("claude_cli", "codex_cli", "cli_version") if r.get(k)})
        if versions: out["cli_versions"] = versions
        if models is not None: out["models_efforts"] = models
        return out

    out = {}
    paths = [TRIM] + sorted(glob.glob(os.path.join(RES, "2026-10-22-pilot*.jsonl")))
    scripts = {TRIM: "bench/trim_probe.py", PILOT: "bench/pilot/bench.py",
               os.path.join(RES, "2026-10-22-pilot-agentic.jsonl"): "bench/pilot/agentic/e2e.py"}
    for path in paths:
        rr = load(path)
        if os.path.exists(path): out[os.path.relpath(path, ROOT)] = entry(path, rr, scripts.get(path, "none: rows only"))
    appendix = os.path.join(RES, "appendix", "luna_rescue.jsonl")
    grouped = defaultdict(list)
    for r in load(appendix):
        arm = r.get("arm", "unknown")
        # Historical B contains the two separately configured B1/B2 arms.
        if arm == "B": arm = next((x for x in ("B1", "B2") if str(r.get("config", "")).endswith(x)), "B")
        grouped[arm].append(r)
    for arm, rr in sorted(grouped.items()):
        key = f"{os.path.relpath(appendix, ROOT)}#{arm}"
        script = {"F": "bench/plan_first.py", "G": "bench/gated_repair.py"}.get(arm, "none: rows only")
        models = None
        if arm == "F": models = {"planner": {"model": PLANNER[0], "effort": PLANNER[1]},
                                  "builders": {c: {"model": v[0], "effort": v[1]} for c, v in BUILDERS.items()}}
        if arm == "G": models = {c: {"model": v[0], "effort": v[1]} for c, v in CONFIGS.items()}
        out[key] = entry(appendix, rr, script, models=models)
    return out


def hypotheses(s):
    cfg = s["configs"]; h = {}
    if not cfg: return h
    l12 = {c: v["pass_L1_L2"] for c, v in cfg.items()}
    h["H1"] = {"claim": "every base config >= 80% on L1-L2", "holds": all(p / n >= 0.8 for p, n in l12.values()),
               "data": {c: f"{p}/{n}" for c, (p, n) in l12.items()}}
    bp = {c: v["breaking_point"] for c, v in cfg.items()}
    pairs = [(a, b) for a, b in [("haiku-low", "haiku-medium"), ("luna-low", "luna-medium")] if a in bp and b in bp]
    if all(bp[a] is None and bp[b] is None for a, b in pairs):
        h["H2"] = {"claim": "within a model, higher effort moves the breaking point up by at least one rung, or removes it", "holds": None, "note": "not testable: no config in these pairs has a breaking point", "data": bp}
    else:
        rank = lambda x: 99 if x is None else int(x[1:])
        h["H2"] = {"claim": "within a model, higher effort moves the breaking point up by at least one rung, or removes it", "holds": all(rank(bp[b]) > rank(bp[a]) for a, b in pairs if bp[a] is not None), "data": bp}
    perfect = {c: v["usd_per_pass_L1_L2"] for c, v in cfg.items() if v["pass_L1_L2"][0] == v["pass_L1_L2"][1]}
    h["H3"] = {"claim": "among configs with 100% on L1-L2, luna-low has the lowest $ per pass there",
               "holds": "luna-low" in perfect and min(perfect, key=perfect.get) == "luna-low", "data": perfect}
    if "luna-low" not in perfect and "luna-low" in cfg:
        h["H3"]["note"] = f"luna-low was not 100% on L1-L2 ({'/'.join(map(str, cfg['luna-low']['pass_L1_L2']))}), so it is not in the set"
    low = {c: b for c, b in bp.items() if b is not None and int(b[1:]) <= 5}
    h["H4"] = {"claim": "at least one config breaks at or below L5", "holds": bool(low), "data": bp}
    ag = s.get("agentic") or {}
    if ag:
        cx = min(v["input_floor"][0] for v in ag.values() if v["cli"] == "codex"); cl = min(v["input_floor"][0] for v in ag.values() if v["cli"] == "claude")
        h["H5"] = {"claim": "agentic Codex min input tokens > Claude's", "holds": cx > cl, "data": {"codex_min_in": cx, "claude_min_in": cl}}
    return h


def pct(x):
    return f"{100 * x:.0f}%"


FAST_COLS = ('sol61-high', 'sol61-high-fast', 'astra-medium', 'astra-medium-fast')  # default tier beside fast mode


def tables(s):
    from analysis.dataset import usd as dataset_usd
    L = ["# Tables", "", "Generated by `analysis/summarize.py` from `results/`. Codex $ are proxies (tokens × list price); Claude $ are measured.", ""]
    L += ["## Function track, main run", "", "| config | pass@1 | 95% CI | breaking point | median s | p90 s | $/call | $/pass | $ kind |", "|---|---|---|---|---|---|---|---|---|"]
    for c, v in s["configs"].items():
        L.append(f"| {c} | {pct(v['pass_at_1'])} ({v['passes']}/{v['n']}) | {ci_text(v['passes'], v['n'], v['ci95'], len(s['problems']))} | {v['breaking_point'] or 'none ≤ L6'} | "
                 f"{v['latency_s']['median']} | {v['latency_s']['p90']} | {money(v['usd_per_call'], 5)} | {money(v['usd_per_pass'], 5)} | {v['cost_kind']} |")
    ex = s.get("exploratory") or {}
    fast_cols = {c: ex[c] for c in FAST_COLS if c in ex}  # the Codex pairs: default tier next to fast mode
    L += ["", "## Fast mode (⚡, Codex priority tier) against the default tier: same model and effort", "",
          "Fast-mode $ use the published multiplier (results/prices.json). Main ladder = p01–p12 (L1–L6), 60 calls each; L7 set = p13–p15, 15 calls each.", "",
          "| config | main ladder passed | $/pass | median s | L7 set passed | $/pass | median s |", "|---|---|---|---|---|---|---|"]
    for c, v in fast_cols.items():
        h = s["hard"].get(c)
        L.append(f"| {DISP(c)} | {v['passes']}/{v['n']} | {money(v['usd_per_pass'], 5)} | {v['latency_s']['median']} | "
                 + (f"{h['passes']}/{h['n']} | {money(h['usd_per_pass'], 5)} | {h['latency_s']['median']} |" if h else "not run | – | – |"))
    rungs = sorted({g for v in s["configs"].values() for g in v["by_rung"]})
    byrung = {**s["configs"], **fast_cols}
    L += ["", "## Passes by rung (out of 10: 2 problems × 5 repeats)", "", "| config | " + " | ".join(rungs) + " |", "|---|" + "---|" * len(rungs)]
    for c, v in byrung.items():
        L.append(f"| {DISP(c)} | " + " | ".join(f"{v['by_rung'][g]['passed']}/{v['by_rung'][g]['n']}" for g in rungs) + " |")
    L += ["", "## Passes per problem (out of 5)", "", "| problem | " + " | ".join(DISP(c) for c in byrung) + " |", "|---|" + "---|" * len(byrung)]
    for p, v in s["problems"].items():
        L.append(f"| {plabel(p, v['rung'])} | " + " | ".join(str(v[c]) if c in v else str(fast_cols[c]["by_problem"][p]) for c in byrung) + " |")
    L += ["", "## Paired differences in pass@1 (a − b, same problems)", "", "| a | b | diff | 95% CI |", "|---|---|---|---|"]
    for d in s["paired"]:
        L.append(f"| {d['a']} | {d['b']} | {100 * d['diff']:+.1f} pts | {100 * d['ci95'][0]:+.1f} to {100 * d['ci95'][1]:+.1f} |")
    L += ["", "## Tokens per call (mean) and input floor (minimum over calls)", "", "| config | input | of which cached | output | of which reasoning | input floor (cached) |", "|---|---|---|---|---|---|"]
    for c, v in s["configs"].items():
        t = v["tokens_mean"]
        L.append(f"| {c} | {t['in_tok']} | {t['cached_tok']} | {t['out_tok']} | {t['reasoning_tok']} | {v['input_floor'][0]} ({v['input_floor'][1]}) |")
    if s["escalation"]:
        L += ["", "## Escalation (subset only)", "",
              "The problems were chosen because the base config failed them, so this is a descriptive count on a selected subset, "
              "with no interval: three clusters are too few for a bootstrap, and the base rate is biased low by the selection.", "",
              "| config | vs | problems | passes | base passes | diff |", "|---|---|---|---|---|---|"]
        for e in s["escalation"]:
            L.append(f"| {e['config']} | {e['vs']} | {', '.join(pshort(q) for q in e['problems'])} | {e['passes']}/{e['n']} | {e['base_passes']}/{e['base_n']} | "
                     f"{100 * e['diff']:+.0f} pts |")
    for c, v in s.get("exploratory", {}).items():
        from bench.run import TRIM_LEVEL
        what = f"Codex trim level {TRIM_LEVEL[c]}" if c in TRIM_LEVEL else "stock harness"
        L += ["", f"## Exploratory, not pre-registered: {DISP(c)} ({what}, full ladder)", "",
              "By rung: " + ", ".join(f"{g} {b['passed']}/{b['n']}" for g, b in v["by_rung"].items()), "",
              "| config | pass@1 | 95% CI | breaking point | median s | p90 s | mean input | $/call | $/pass | $/pass, no cache discount | $ kind |", "|---|---|---|---|---|---|---|---|---|---|---|",
              f"| {DISP(c)} | {pct(v['pass_at_1'])} ({v['passes']}/{v['n']}) | {ci_text(v['passes'], v['n'], v['ci95'], len(s['problems']))} | {v['breaking_point'] or 'none ≤ L6'} | "
              f"{v['latency_s']['median']} | {v['latency_s']['p90']} | {v['tokens_mean']['in_tok']} | {money(v['usd_per_call'], 5)} | {money(v['usd_per_pass'], 5)} | {money(v['usd_per_pass_uncached'], 5)} | {v['cost_kind']} |", "",
              "| a | b | diff | 95% CI |", "|---|---|---|---|"]
        for d in v["vs"]:
            L.append(f"| {DISP(c)} | {d['b']} | {100 * d['diff']:+.1f} pts | {100 * d['ci95'][0]:+.1f} to {100 * d['ci95'][1]:+.1f} |")
    if s.get("hard"):
        probs = sorted({p for v in s["hard"].values() for p in v["by_problem"]})
        L += ["", "## L7, added after the main run (3 problems × 5 attempts)", "",
              "Not pre-registered (PLAN.md, deviation 16), so it is reported apart from L1–L6 and does not change any number above.", "",
              "| config | pass@1 | 95% CI | " + " | ".join(plabel(q, 7) for q in probs) + " | outcomes | median s | p90 s | mean reasoning tokens | $/call | $/pass | $ kind |",
              "|---|---|---|" + "---|" * len(probs) + "---|---|---|---|---|---|---|"]
        for c, v in s["hard"].items():
            oc = ", ".join(f"{k} {n}" for k, n in sorted(v["outcomes"].items()))
            L.append(f"| {DISP(c)} | {pct(v['pass_at_1'])} ({v['passes']}/{v['n']}) | {ci_text(v['passes'], v['n'], v['ci95'], len(probs))} | "
                     + " | ".join(f"{v['by_problem'].get(p, 0)}/5" for p in probs)
                     + f" | {oc} | {v['latency_s']['median']} | {v['latency_s']['p90']} | {v['tokens_mean']['reasoning_tok']} | {money(v['usd_per_call'], 5)} | "
                     + (money(v["usd_per_pass"], 5) if v["passes"] else "no pass") + f" | {v['cost_kind']} |")
    if s.get("failures"):
        cfgs = list(dict.fromkeys(c for f in s["failures"].values() for c in f["cells"]))
        L += ["", "## Where they fail", "",
              "Every problem on which at least one config failed at least once, over all phases (main, escalation, exploratory, L7). "
              "Cells show passes/attempts and, for the failures, the outcome: w = wrong answer, c = crash, t = timeout, n = no code. A dash means not run.", "",
              "| problem | " + " | ".join(DISP(c) for c in cfgs) + " |", "|---|" + "---|" * len(cfgs)]
        ab = {"wrong": "w", "crash": "c", "timeout": "t", "no_code": "n"}
        def cell(x):
            if not x: return "–"
            f = " ".join(f"{n}{ab.get(k, k)}" for k, n in sorted(x["fails"].items()))
            return f"{x['passed']}/{x['n']}" + (f" ({f})" if f else "")
        for p, f in s["failures"].items():
            L.append(f"| {plabel(p, f['rung'])} | " + " | ".join(cell(f["cells"].get(c)) for c in cfgs) + " |")
    if s["agentic"]:
        L += ["", "## Agentic track (hidden tests)", "", "| config | hidden pass | 95% CI | visible suite, incl. agent's own tests | complete task | median s | input floor | $/run | $ kind |", "|---|---|---|---|---|---|---|---|---|"]
        for c, v in s["agentic"].items():
            L.append(f"| {c} | {v['hidden_pass']}/{v['n']} | {ci_text(v['hidden_pass'], v['n'], v['ci95'], len(v['by_task']))} | {v['visible_pass']}/{v['n']} | {v['task_complete']}/{v['n']} | {v['latency_s']['median']} | "
                     f"{v['input_floor'][0]} | {money(v['usd_per_run'], 4)} | {v['cost_kind']} |")
        tasks = sorted({t for v in s["agentic"].values() for t in v["by_task"]})
        L += ["", "| config | " + " | ".join(tasks) + " |", "|---|" + "---|" * len(tasks)]
        for c, v in s["agentic"].items():
            L.append(f"| {c} | " + " | ".join(f"{v['by_task'][t]['hidden_pass']}/{v['by_task'][t]['n']} (tests {', '.join(v['by_task'][t]['hidden_tests'])})" for t in tasks) + " |")
    t = s.get("trim") or {}
    if t.get("floor"):
        L += ["", "## Codex input floor by trim level (fizzbuzz, one call each, low effort)", "",
              "Levels are cumulative. base = the function-track harness. nodoc = project_doc_max_bytes=0. noctx = environment and permission context off. "
              "nofeat = tool-adding features and web search off. mininst = one-line model_instructions_file (no longer stock Codex). noshell = shell and exec tools off.", "",
              ]
        from bench.trim_probe import LEVELS
        levels = [lv for lv in LEVELS if any(k.endswith("/" + lv) for k in t["floor"])]
        L += ["| model | " + " | ".join(levels) + " |", "|---|" + "---|" * len(levels)]
        for m in dict.fromkeys(k.split("/")[0] for k in t["floor"]):
            L.append(f"| {m} | " + " | ".join(f"{t['floor'][f'{m}/{lv}']['in_tok']:,}" if f"{m}/{lv}" in t["floor"] else "–" for lv in levels) + " |")
    if t.get("pair"):
        L += ["", "## Pilot problems, 3 rounds × 3 problems: stripped Codex vs haiku-low (tools off)", "",
              "| config | level | passes | median input | of which cached | min input | median output | median s | p90 s | $/call | $ kind |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for c, v in t["pair"].items():
            L.append(f"| {c} | {v['level'] or '–'} | {v['passes']}/{v['n']} | {v['in_median']:,} | {v['cached_median']:,} | {v['in_min']:,} | {v['out_median']:,} | {v['median_s']} | {v['p90_s']} | "
                     f"{money(v['usd_per_call'], 5)} | {v['cost_kind']} |")
    if s.get("pilot"):
        L += ["", "## Pilot (2026-10-22), for reference", "",
              "Well-known problems, so every config passed everything. Cells show passes/runs; † marks a cell whose n is not 9, so it does not read as a 9/9 equivalent. "
              "Priority-tier Codex $ use the published 2× fast-mode multiplier.", "",
              "| config | model | effort | passes | problems | tier | input floor | median s | $/call |", "|---|---|---|---|---|---|---|---|---|"]
        for c, v in s["pilot"].items():
            L.append(f"| {c} | {v['model']} | {v['effort']} | {v['passes']}/{v['n']}{'' if v['n'] == 9 else ' †'} | {v['problems']} | {v['service_tier']} | "
                     f"{v['input_floor']:,} | {v['median_s']} | {money(v['usd_per_call'], 5)} |")
        L += ["", "† n ≠ 9: these configs ran a different number of rounds or problems (3 problems × 3 rounds = 9 is the common cell).", "",
              "The pilot's Codex ladder records only the levels that were actually tested. Every model passed at low effort, so nothing escalated, "
              "and the ladder is not an intelligence ranking."]
    L += ["", "## Hypotheses", ""]
    for k, v in s["hypotheses"].items():
        verdict = {True: "holds", False: "does not hold", None: "not testable"}[v["holds"]]
        L.append(f"- {k} ({v['claim']}): {verdict}. Data: `{json.dumps(v['data'])}`" + (f" {v['note']}." if v.get("note") else ""))
    sp = s["spend"]
    L += ["", "## Spend", "", "Auxiliary runs and pilot excluded from the function + agentic totals.", "", f"- Claude CLI-reported cost (list basis), function + agentic only: ${money(sp['claude_measured_usd'], 2)} (function ${money(sp['claude_function_usd'], 2)}, agentic ${money(sp['claude_agentic_usd'], 2)}).",
          f"- Codex token-price estimate, function + agentic only: ${money(sp['codex_proxy_usd'], 2)}.",
          f"- Pilot repricing: {s['pilot_reprice']['rows']} priority-tier Codex rows cost {dataset_usd(s['pilot_reprice']['usd_at_1_5x'])} at the pilot's 1.5× and {dataset_usd(s['pilot_reprice']['usd_at_2x'])} at the published 2×.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
