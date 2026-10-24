"""The dataset: one tidy table built from results/*.jsonl, one row per (config, set), plus an "all runs" roll-up per config.

Every chart and table should read this table (results/dataset.json) and the registry (analysis/configs.py), not recompute metrics from raw rows.
Metric code is not duplicated here: cost, fast-mode pricing and the bootstrap come from analysis.summarize and analysis.stats.
Sets (mutually exclusive; every row lands in exactly one, or this module raises):
  main ladder     rungs L1-L6, repeats 1-5, for a config that covers all 12 problems x 5 repeats (phases main, exploratory, escalation, fastmode)
  partial ladder  the same rows for a config that does not cover them all (for example sol61-xhigh, run on the rescue problems only)
  extra repeats   repeats 6-10 (the default-tier control for the fast-mode comparison)
  L7 set          phase hard
  calibration     phase calibration; warmup rows are dropped
  repo tasks      the agentic track
  rescue arms     appendix/luna_rescue.jsonl (35 attempts per arm on the rescue problems)
  pilot, pilot repo task, trim probe, harness bias   one set per file
A set in DERIVED (rescue set: a main-run config restricted to the 7 rescue problems, repeats 1-5) repeats rows already in another set, is flagged\nderived: true and is excluded from "all runs".\nColumns: id, derived, source, config, display, family, category, what, set, passes, n, pass_rate, ci95, usd_per_pass, claude_usd_per_pass,
codex_usd_per_pass, usd_per_call, spend, spend_claude, spend_codex, unknown_usd, median_s, p25_s, p75_s, tokens_in_mean, tokens_out_mean,
cost_kind, by_rung ({L1: [passed, n]}), groups (problems or tasks). No model calls. Run: python3 -m analysis.dataset"""
import json, os, statistics
from collections import defaultdict

from analysis import configs, stats
from analysis.luna_rescue import PIDS, claude_usd
from analysis.summarize import RES, ROOT, cost, load, scale

PATH = os.path.join(RES, "dataset.json")

import glob, re, copy, math
from datetime import datetime
from fractions import Fraction
from decimal import Decimal
from analysis import fast_gate, harness_bias, luna_rescue, summarize
from analysis.labels import pshort, plabel, DISP
from analysis.summarize import FAST_CONFIGS, FUNC, AGENT, ci_text, cost_uncached, pct

HOST_AGENTS_MD = "1.3k"  # host AGENTS.md, measured once by hand (bytes / 4)
MIN_PASS = 0.90
QUALITY = os.path.join(RES, "quality.jsonl")
NEW_CODEX = ("sol61-high", "sol56-high", "astra-medium", "luna56-high", "luna56-low")
GROWTH_MARGIN = 0.3

REPORT_PROBLEMS = 12; REPEATS = 5
DERIVED = ("rescue set",)  # slices of rows that are also in another set; never summed into "all runs"
# "all runs" pools only function-run sets: main/partial ladder, extra repeats,
# L7 set and calibration. Repo tasks, pilot, rescue arms, trim and harness-bias
# retain their own set names; the overlapping derived rescue set is excluded.
ALL_RUN_SETS = ("main ladder", "partial ladder", "extra repeats", "L7 set", "calibration")


def _mult(r):
    """Fast-mode multiplier: summarize.cost already applies it to the fast configs; pilot rows carry their tier."""
    if str(r.get("service_tier", "")).startswith("priority") and r.get("phase") == "pilot":
        return json.load(open(os.path.join(RES, "prices.json")))["fast_mode_multiplier"]
    return 1


def _usd(r, source):
    if source in ("rescue", "harness-bias") and "cost_usd" in r: return r["cost_usd"]
    if source == "pilot-agentic":
        c = r.get("builder_cost_usd")
        if c is None:
            from analysis.summarize import PRICES
            p = PRICES[r["builder"]]; c = ((r["builder_in"] - r["builder_cached"]) * p["input"] + r["builder_cached"] * p["cached_input"] + r["builder_out"] * p["output"]) / 1e6
        return c + ((r.get("review") or {}).get("cost_usd") or 0)
    if "cli" not in r: return r.get("cost_usd")
    return scale(cost(r), _mult(r))


def _claude(r, source, usd):
    if usd is None: return None
    if source == "rescue": return claude_usd(r)
    if source == "pilot-agentic": return usd if r["builder_kind"] == "claude" else (r.get("review") or {}).get("cost_usd") or 0
    return usd if str(r.get("cli", "")).startswith("claude") else 0.0


def _rows():
    """[(source, name, set, row dict with _usd/_claude/_pass/_sec/_group)] from every results file."""
    out = []
    def add(src, name, st, r, ok, sec, group, usd, tin, tout):
        out.append((src, name, st, {"ok": bool(ok), "sec": sec, "group": group, "usd": usd, "claude": _claude(r, src, usd), "in": tin, "out": tout, "cached": r.get("cached_tok") or r.get("builder_cached") or 0, "reasoning": r.get("reasoning_tok") or 0, "cli": r.get("cli", r.get("builder_kind", "")), "rung": r.get("rung")}))
    func = [r for r in load(os.path.join(RES, configs.SOURCES["main"][0])) if r["phase"] != "warmup"]
    cover = defaultdict(set)
    for r in func:
        if r["rung"] <= 6 and r["repeat"] <= REPEATS and r["phase"] != "calibration": cover[r["config"]].add((r["problem"], r["repeat"]))
    for r in func:
        c = r["config"]
        if r["phase"] == "hard": st = "L7 set"
        elif r["phase"] == "calibration": st = "calibration"
        elif r["repeat"] > REPEATS: st = "extra repeats"
        else: st = "main ladder" if len(cover[c]) == REPORT_PROBLEMS * REPEATS else "partial ladder"
        add("main", c, st, r, r["passed"], r["wall_s"], r["problem"], _usd(r, "main"), r["in_tok"], r["out_tok"])
        if r["problem"] in PIDS and r["phase"] in ("main", "exploratory", "fastmode") and r["repeat"] <= REPEATS:  # the same rows again, as the rescue-set baseline
            add("main", c, "rescue set", r, r["passed"], r["wall_s"], r["problem"], _usd(r, "main"), r["in_tok"], r["out_tok"])
    for r in load(os.path.join(RES, configs.SOURCES["agentic"][0])):
        add("agentic", r["config"], "repo tasks", r, r["hidden_pass"], r["wall_s"], r["task"], _usd(r, "agentic"), r["in_tok"], r["out_tok"])
    for r in load(os.path.join(RES, configs.SOURCES["trim"][0])):
        add("trim", r["config"], "trim probe", r, r["passed"], r["wall_s"], r["problem"], _usd(r, "trim"), r["in_tok"], r["out_tok"])
    for r in load(os.path.join(RES, configs.SOURCES["pilot"][0])):
        add("pilot", r["config"], "pilot", r, r["passed"], r["wall_s"], r["problem"], _usd(r, "pilot"), r["in_tok"], r["out_tok"])
    for r in load(os.path.join(RES, configs.SOURCES["rescue"][0])):
        add("rescue", r["config"], "rescue arms", r, r["passed"], r["wall_s"], r["problem"], _usd(r, "rescue"), r["in_tok"], r["out_tok"])
    for r in load(os.path.join(RES, configs.SOURCES["pilot-agentic"][0])):
        add("pilot-agentic", f"pipeline {r['pipeline']}", "pilot repo task", r, r["hidden_pass"], r["builder_wall_s"], f"round {r['round']}", _usd(r, "pilot-agentic"), r["builder_in"], r["builder_out"])
    for f in configs.SOURCES["harness-bias"]:
        for r in load(os.path.join(RES, f)):
            add("harness-bias", f"{r['config']} / {'Codex' if r['phase'] == 'codex_harness' else 'Claude'} harness", "harness bias", r, r["passed"], r["wall_s"], r["problem"], _usd(r, "harness-bias"), r["in_tok"], r["out_tok"])
    return out


def _quart(xs):
    q = statistics.quantiles(xs, n=4) if len(xs) > 1 else [xs[0]] * 3
    return q[0], q[2]


def _row(src, name, st, rr):
    k = sum(x["ok"] for x in rr); n = len(rr); known = [x["usd"] for x in rr if x["usd"] is not None]
    cl = [x["claude"] for x in rr if x["claude"] is not None]; secs = [x["sec"] for x in rr]
    complete = len(known) == n; e = configs.entry(src, name) if (src, name) in configs.REGISTRY else {"id": f"{src}/{name}", "display": configs.display(name), "family": configs.family(name), "category": "?", "files": [], "what": ""}
    cells = defaultdict(list)
    for x in rr: cells[x["group"]].append(1 if x["ok"] else 0)
    ci = None
    if len(cells) > 1 and 0 < k < n: _, lo, hi = stats.hier_boot(dict(cells)); ci = [round(lo, 4), round(hi, 4)]
    by_rung = {}
    for x in rr:
        if x["rung"] is not None: g = by_rung.setdefault(f"L{x['rung']}", [0, 0]); g[0] += x["ok"]; g[1] += 1
    p25, p75 = _quart(secs)
    spend = sum(known); sc = sum(cl)
    return {"id": e["id"], "source": src, "config": name, "display": e["display"], "family": e["family"], "category": e["category"], "what": e["what"], "set": st, "derived": st in DERIVED, "files": e["files"],
            "passes": k, "n": n, "pass_rate": round(k / n, 4), "ci95": ci, "groups": len(cells),
            "usd_per_pass": round(spend / k, 6) if k and complete else None, "claude_usd_per_pass": round(sc / k, 6) if k and complete else None,
            "codex_usd_per_pass": round((spend - sc) / k, 6) if k and complete else None, "usd_per_call": round(spend / n, 6) if complete else None,
            "spend": round(spend, 6), "spend_claude": round(sc, 6), "spend_codex": round(spend - sc, 6), "unknown_usd": n - len(known),
            "median_s": round(statistics.median(secs), 2), "p25_s": round(p25, 2), "p75_s": round(p75, 2),
            "tokens_in_mean": round(statistics.mean(x["in"] or 0 for x in rr)), "tokens_out_mean": round(statistics.mean(x["out"] or 0 for x in rr)),
            "tokens_cached_mean": round(statistics.mean(x["cached"] for x in rr)),
            "tokens_reasoning_mean": round(statistics.mean(x["reasoning"] for x in rr)),
            "input_floor": list(min((x["in"] or 0, x["cached"]) for x in rr)),
            "p90_s": round(stats.p90(secs), 2), "max_s": round(max(secs), 2),
            "by_group": {g: {"passes": sum(v), "n": len(v)} for g, v in cells.items()},
            "misses": n - k, "ci95_plot": ci or ([0.05 ** (1 / len(cells)), 1.0] if k == n else [0.0, 0.0]),
            "usd_saved_per_pass": round((spend - sc) / k, 6) if k and complete else None,
            "usd_per_1k_tokens": (1000 * round(spend / n, 6) / (round(statistics.mean(x["in"] or 0 for x in rr)) + round(statistics.mean(x["out"] or 0 for x in rr)))) if complete and any((x["in"] or 0) + (x["out"] or 0) for x in rr) else None,
            "by_rung": dict(sorted(by_rung.items())), "cost_kind": "measured" if rr[0]["cli"].startswith("claude") else "proxy"}


def _base():
    groups = defaultdict(list)
    for src, name, st, x in _rows(): groups[(src, name, st)].append(x)
    rows = [_row(src, name, st, rr) for (src, name, st), rr in groups.items()]
    allr = defaultdict(list)
    for (src, name, st), rr in groups.items():
        if src == "main" and st in ALL_RUN_SETS: allr[(src, name)] += rr
    rows += [_row(src, name, "all runs", rr) for (src, name), rr in allr.items()]
    row_keys = [(r["config"], r["set"]) for r in rows]
    assert len(row_keys) == len(set(row_keys)), "duplicate (config, set) keys"
    order = {c: i for i, c in enumerate(configs.CATEGORIES)}
    rows.sort(key=lambda r: (r["set"] == "all runs", order.get(r["category"], 99), r["source"], r["set"], list(configs.REGISTRY).index((r["source"], r["config"])) if (r["source"], r["config"]) in configs.REGISTRY else 999))
    return {"generated_from": sorted({f for r in rows for f in r["files"]}), "sets": sorted({r["set"] for r in rows}), "rows": rows}


def keys(ds):
    return {(r["source"], r["config"]) for r in ds["rows"]}


def catalog_rows(ds):
    """One row per registry entry: function roll-ups, other sources' named sets."""
    return [r for r in ds["rows"] if r["set"] == "all runs" or r["source"] != "main" and not r["derived"]]


def get(ds, config, set_, source="main"):
    """The one row for (config, set); KeyError if the config never ran in that set."""
    return next(r for r in ds["rows"] if r["source"] == source and r["config"] == config and r["set"] == set_)


def usd(v, sig=2):
    """Two decimals from $1; otherwise significant figures without zero padding.

    Use sig=3 explicitly when a textual comparison needs the extra distinction.
    """
    if v is None: return "–"
    if v == 0: return "$0"
    if v >= 1: return f"${v:,.2f}"
    value = format(Decimal(f"{v:.{sig}g}"), "f")
    return "$" + (value.rstrip("0").rstrip(".") if "." in value else value)



class Facts(dict):
    def __missing__(self, k):
        raise KeyError(f"template uses unknown fact {{{{{k}}}}}")


def need(cond, why):
    """A sentence in the template depends on this holding. If the data change so that it no longer does, fail instead of printing a false sentence."""
    if not cond:
        raise AssertionError(f"template wording no longer matches the data: {why}")


def p1(d):
    """Signed points with one decimal and a real minus sign: +18.3, −3.3."""
    v = round(100 * d, 1)
    return ("+" if v > 0 else "−" if v < 0 else "") + f"{abs(v):.1f}"


def ci_pts(ci):
    return f"{p1(ci[0])} to {p1(ci[1])}"


def n(v):
    return f"{v:,}"


def x(a, b, d=1):
    return f"{a / b:.{d}f}×"


def about(v, step=10):
    return n(int(round(v / step) * step))


def paired(s, a, b):
    for d in s["paired"]:
        if (d["a"], d["b"]) == (a, b): return d
    raise KeyError((a, b))


def vs(s, c, b):
    return next(d for d in s["exploratory"][c]["vs"] if d["b"] == b)


def codex_orchestrator_status(rows):
    """Only attributed result rows count; running the tested config in Codex is not orchestration."""
    def is_codex(value):
        if isinstance(value, dict):
            return any(is_codex(value.get(k, "")) for k in ("cli", "model", "name"))
        return str(value).lower().startswith(("codex", "gpt-"))
    return "results available" if any(r.get("passed") is not None and is_codex(r.get("orchestrator", "")) for r in rows) else "not run yet"


def fairness_facts():
    """Page facts from committed appendix rows; never regenerate or grade the experiment."""
    rows = load(os.path.join(RES, "appendix", "harness_bias.jsonl"))
    result = harness_bias.pass_summary(rows)
    lo, hi = result['ci']
    need(result['missing'] == 0, "harness comparison has complete pairs")
    diff = result['diff']
    if lo <= 0 <= hi:
        answer = f"No bias of about {max(abs(lo), abs(hi)):.1f} or more was detectable."
        detail = "The confidence interval contains zero."
    else:
        need(0 < lo and 0 < diff < 0.15, "harness-bias result is a positive tilt below the 0.15 bias threshold")
        answer = "Slightly, but below the 0.15 we set as the bias threshold."
        detail = (f"Codex's harness helped luna-low more than haiku-low: the gap between them changed by {diff:+.3f}. "
                  "The confidence interval excludes zero but stays below 0.15, so we do not call it bias.")
    facts = dict(hb_answer=answer, hb_detail=detail, hb_ci=f"{lo:+.3f} to {hi:+.3f}",
                 hb_n_problems=str(len({r['problem'] for r in rows})),
                 hb_repeats=str(len({r['repeat'] for r in rows})))
    for harness, prefix in (('claude-one-shot', 'claude'), ('codex-tool-loop', 'codex')):
        for config in harness_bias.CFGS:
            cell = [r for r in rows if (r['harness'], r['config']) == (harness, config)]
            facts[f"hb_{prefix}_{config.replace('-', '_')}"] = f"{sum(r['passed'] for r in cell)}/{len(cell)}"
    codex = [r for r in rows if r['harness'] == 'codex-tool-loop']
    facts['hb_errors'] = str(sum(r['outcome'] == 'harness_error' for r in codex))
    need(not any(r['outcome'] == 'timeout' or re.search(r'timeout|timed out|exceeded', r.get('error') or '', re.I)
                 for r in codex), "Codex harness had no timeouts")
    # Codex harness ts is recorded before invocation; wall_s is that invocation's duration.
    start = min(datetime.fromisoformat(r['ts']).timestamp() for r in codex)
    end = max(datetime.fromisoformat(r['ts']).timestamp() + r['wall_s'] for r in codex)
    facts['hb_minutes'] = f"{(end - start) / 60:.0f}"
    return facts


def _facts(s, arms):
    F = Facts(); cfg, ex, ag, hard = s["configs"], s["exploratory"], s["agentic"], s["hard"]
    rows = load(FUNC); agent = load(AGENT); main_rows = [r for r in rows if r["phase"] == "main"]
    every = {**cfg, **ex}
    nprob = len(s["problems"]); ntask = len(next(iter(ag.values()))["by_task"])
    F.update(n_problems=str(nprob), n_tasks=str(ntask), n_configs=str(len(cfg)), n_l7=str(len({p for v in hard.values() for p in v["by_problem"]})),
             repeats=str(cfg["haiku-low"]["n"] // nprob), n_calls=str(cfg["haiku-low"]["n"]), n_all_problems=str(nprob + len({p for v in hard.values() for p in v["by_problem"]})),
             agent_repeats=str(next(iter(ag.values()))["n"] // ntask), n_rungs=str(len(cfg["haiku-low"]["by_rung"])), per_rung=str(nprob // len(cfg["haiku-low"]["by_rung"])))
    need(all(v["n"] == cfg["haiku-low"]["n"] for v in every.values()), "every function-track config has the same number of calls")
    F["run_id"] = json.load(open(os.path.join(RES, "manifest.json")))["experiment"]
    attributed = (r for path in sorted(glob.glob(os.path.join(RES, "**", "*.jsonl"), recursive=True)) for r in load(path))
    F["codex_orchestrator_status"] = codex_orchestrator_status(attributed)
    F.update(fairness_facts())
    F["l7_n"] = str(len({p for v in hard.values() for p in v["by_problem"]}) * int(F["repeats"]))
    F["n_rescue_problems"] = str(len(luna_rescue.PIDS))
    F["older_generation"] = "5.6"
    F["quality_fast_note"] = quality_fast_note(s)
    F["budget_pass"] = pct(0.95); F["p90_percent"] = pct(0.90)
    F["host_agents_md"] = HOST_AGENTS_MD; F["min_pass"] = pct(MIN_PASS)
    F["rung_attempts"] = str(cfg["haiku-low"]["by_rung"]["L1"]["n"])
    sp = s["spend"]
    F["claude_usd"] = usd(sp['claude_measured_usd']); F["codex_usd"] = usd(sp['codex_proxy_usd'])
    for c, v in every.items():
        k = c.replace("-", "_")
        F[f"{k}_pass"] = pct(v["pass_at_1"]); F[f"{k}_k"] = f"{v['passes']}/{v['n']}"; F[f"{k}_upp"] = usd(v["usd_per_pass"])
        F[f"{k}_med"] = f"{v['latency_s']['median']:.1f}"; F[f"{k}_rsn"] = n(v["tokens_mean"]["reasoning_tok"]); F[f"{k}_rsn10"] = about(v["tokens_mean"]["reasoning_tok"])
        F[f"{k}_in"] = n(v["tokens_mean"]["in_tok"]); F[f"{k}_total"] = usd(v['usd_total'])
    F["haiku_low_passes"] = str(cfg["haiku-low"]["passes"])
    F["hh_passes"] = str(ex["haiku-high"]["passes"])
    F["model_names"] = f"luna = {cfg['luna-low']['model']}, sol61 = {ex['sol61-high']['model']}, astra = {ex['astra-medium']['model']}"
    F["ref_unit"] = f"{1:.2f}"
    missed = statistics.mean(1 - every[c]["pass_at_1"] for c in ("luna-low", "luna-low-bare", "luna-medium"))
    need(abs(missed - 1 / 4) < .04, "the cheapest points miss about a quarter")
    fraction = Fraction(missed).limit_denominator(4)
    F["cheap_miss_words"] = f"{fraction.numerator} answer in {fraction.denominator}"
    p04 = [r for r in rows if r["problem"] == "p04_taller_within" and r["phase"] in ("main", "exploratory")]
    counts = [sum(r["passed"] for r in p04 if r["config"] == c) for c in ("luna-low", "luna-medium", "luna-low-bare")]
    need(len(set(counts)) == 1, "three cheap luna configs have equal p04 passes")
    F["p04_passes"] = str(counts[0])
    # finding 1: effort budgets
    hl, ll, lm, lh = cfg["haiku-low"], cfg["luna-low"], cfg["luna-medium"], ex["luna-high"]
    need(ll["tokens_mean"]["reasoning_tok"] < 50 and lm["tokens_mean"]["reasoning_tok"] < 50, "luna low/medium barely reason")
    d = paired(s, "haiku-low", "luna-low"); F["hl_vs_ll"] = p1(d["diff"]); F["hl_vs_ll_ci"] = ci_pts(d["ci95"])
    d = vs(s, "luna-high", "haiku-low"); need(d["diff"] < 0, "luna-high below haiku-low")
    F["lh_below_hl"] = f"{abs(round(100 * d['diff'], 1)):.1f}"; F["lh_vs_hl_ci"] = ci_pts(d["ci95"])
    # finding 2: three problems
    for p in ("p04_taller_within", "p11_best_average", "p12_sheet"):
        F[f"{p[:3]}_luna"] = f"{s['problems'][p]['luna-low'] + s['problems'][p]['luna-medium']}/{2 * cfg['luna-low']['n'] // nprob}"
    e = next(e for e in s["escalation"] if e["config"] == "luna-high")
    F["esc_problems"] = ", ".join(plabel(p) for p in e["problems"])
    F["esc_k"] = f"{e['passes']}/{e['n']}"; F["esc_base"] = f"{e['base_passes']}/{e['base_n']}"; F["esc_vs"] = e["vs"]
    d = vs(s, "luna-high", "luna-medium"); F["lh_vs_lm"] = p1(d["diff"]); F["lh_vs_lm_ci"] = ci_pts(d["ci95"])
    # finding 3 and the token callout: stripped harness
    lb = ex["luna-low-bare"]
    F["in_cut"] = pct(1 - lb["tokens_mean"]["in_tok"] / ll["tokens_mean"]["in_tok"])
    need(1 - lb["tokens_mean"]["in_tok"] / ll["tokens_mean"]["in_tok"] > 0.5, "stripping the harness cuts input by more than half")
    d = vs(s, "luna-low-bare", "haiku-low"); F["lb_vs_hl"] = p1(d["diff"]); F["lb_vs_hl_ci"] = ci_pts(d["ci95"]); need(d["ci95"][1] == 0, "CI upper end touches zero")
    d = vs(s, "luna-low-bare", "luna-low"); F["lb_vs_ll"] = p1(d["diff"]); F["lb_vs_ll_ci"] = ci_pts(d["ci95"]); need(d["ci95"][0] < 0 < d["ci95"][1], "stripping changes nothing")
    need(lb["usd_per_pass"] < hl["usd_per_pass"] < lb["usd_per_pass_uncached"], "stripped luna cheaper than haiku only with the cache")
    F["lb_upp_nocache"] = usd(lb["usd_per_pass_uncached"]); F["lb_nocache_above"] = pct(lb["usd_per_pass_uncached"] / hl["usd_per_pass"] - 1)
    tr = s["trim"]["floor"]
    # finding 4: agentic
    need(all(v["hidden_pass"] == v["n"] for v in ag.values()), "every agentic run passed")
    F["ag_k"] = f"{ag['luna-low']['hidden_pass']}/{ag['luna-low']['n']}"; F["ag_runs"] = str(sum(v["n"] for v in ag.values()))
    for c, v in ag.items():
        k = c.replace("-", "_"); F[f"ag_{k}_usd"] = usd(v['usd_per_run']) if v["usd_per_run"] is not None and v["usd_per_run"] < 0.01 else usd(v['usd_per_run'])
        F[f"ag_{k}_med"] = f"{v['latency_s']['median']:.0f}"
    AG_BASE = ("luna-low", "haiku-low", "sonnet-medium", "sol61-medium")  # the four first run; sol61-high and astra-medium added 2026-10-23
    usds = [ag[c]["usd_per_run"] for c in AG_BASE]; F["ag_spread"] = f"{max(usds) / min(usds):.0f}×"
    others = [ag[c]["latency_s"]["median"] for c in AG_BASE if c != "sol61-medium"]
    need(max(others) - min(others) < 2, "the other three agentic medians are about equal"); F["ag_other_med"] = f"{statistics.mean(others):.0f}"
    at = json.load(open(os.path.join(RES, "agentic_tests.json")))
    for c in ("luna-low", "sol61-medium"):
        rr = [r for r in at if r["config"] == c]; k = c.replace("-", "_")
        F[f"host_{k}"] = str(sum(r["host_agents_md_commands"] for r in rr)); F[f"shell_{k}"] = str(sum(r["shell_commands"] for r in rr))
    need(not any(v["tests_tampered_runs"] for v in ag.values()), "no run edited the original tests")
    # routing rule
    sm = cfg["sonnet-medium"]; smh = hard["sonnet-medium"]
    need(sm["passes"] == sm["n"] and smh["passes"] == smh["n"], "sonnet-medium never failed")
    F["sm_all"] = f"{sm['passes'] + smh['passes']}/{sm['n'] + smh['n']}"; F["sm_vs_hl_x"] = f"{sm['usd_per_pass'] / hl['usd_per_pass']:.0f}×"
    # harness floor
    pr = s["trim"]["pair"]
    F["terra_call"] = usd(pr["terra/noshell"]["usd_per_call"]); F["terra_x"] = f"{pr['terra/noshell']['usd_per_call'] / pr['haiku']['usd_per_call']:.0f}×"
    # L7
    probs = sorted({p for v in hard.values() for p in v["by_problem"]}); F["l7_bound"] = pct(0.05 ** (1 / len(probs)))
    hh = hard["haiku-low"]; need(hh["outcomes"] == {"pass": hh["passes"], "timeout": hh["n"] - hh["passes"]}, "haiku-low L7 misses are all timeouts")
    hrows = [r for r in rows if r["phase"] == "hard" and r["config"] == "haiku-low" and not r["passed"]]
    need(len({r["problem"] for r in hrows}) == 1 and len({r["grade_detail"] for r in hrows}) == 1, "same p15 case")
    F["l7_hl_fail"] = str(len(hrows)); F["l7_hl_pass_p15"] = str(hh["by_problem"]["p15_paint_erase"])
    for c in ("luna-high", "sol61-medium", "sonnet-medium", "haiku-low"):
        F[f"l7_{c.replace('-', '_')}_upp"] = usd(hard[c]["usd_per_pass"]); F[f"l7_{c.replace('-', '_')}_med"] = f"{hard[c]['latency_s']['median']:.0f}"
    lo, hi = sorted([hard["sol61-medium"]["usd_per_pass"], hard["sonnet-medium"]["usd_per_pass"]]); F["l7_dear"] = f"{usd(lo)}–{usd(hi)}"
    L7_BASE = ("luna-high", "sol61-medium", "sonnet-medium", "haiku-low")  # the pre-registered L7 configs; the 2026-10-23 Codex additions are reported apart
    need(min(L7_BASE, key=lambda c: hard[c]["latency_s"]["median"]) == "sonnet-medium", "sonnet-medium fastest on L7")
    for c, base in (("haiku-low", cfg["haiku-low"]), ("luna-high", ex["luna-high"])):
        k = c.replace("-", "_"); a, b = base["tokens_mean"]["reasoning_tok"], hard[c]["tokens_mean"]["reasoning_tok"]
        F[f"l7_{k}_rsn_x"] = x(b, a); F[f"l7_{k}_rsn_a"] = n(a); F[f"l7_{k}_rsn_b"] = n(b)
    # where they fail
    lun = [r for r in rows if r["problem"] == "p12_sheet" and r["config"] in ("luna-low", "luna-medium", "luna-low-bare") and r["phase"] in ("main", "exploratory")]
    crash = [r for r in lun if r["outcome"] == "crash"]; rec = [r for r in crash if "RecursionError" in (r["grade_detail"] or "")]
    F["p12_luna_n"] = str(len(lun)); F["p12_parse"] = str(len(crash) - len(rec)); F["p12_rec"] = str(len(rec))
    need(all(r["grade_detail"].startswith("small") for r in crash if r not in rec), "parse errors are on small cases")
    hlp12 = [r for r in main_rows if r["problem"] == "p12_sheet" and r["config"] == "haiku-low" and not r["passed"]]
    need(len(hlp12) == 1 and "RecursionError" in hlp12[0]["grade_detail"], "haiku-low's p12 miss is the recursion limit")
    w04 = [r for r in rows if r["problem"] == "p04_taller_within" and r["config"] in ("luna-low", "luna-medium", "luna-low-bare") and r["outcome"] == "wrong" and r["phase"] in ("main", "exploratory")]
    F["p04_wrong"] = str(len(w04)); F["p04_wrong_ex1"] = str(sum(r["grade_detail"] == "small case 0" for r in w04))
    hl_all = [r for r in rows if r["config"] == "haiku-low" and r["phase"] in ("main", "hard")]
    oc = {k: sum(r["outcome"] == k for r in hl_all) for k in ("timeout", "crash", "wrong")}; need(oc["wrong"] == 0, "haiku-low never wrong")
    for name, phase in (("main", "main"), ("l7", "hard")):
        rr = [r for r in hl_all if r["phase"] == phase]
        F[f"hl_{name}_failures"] = f"{sum(r['outcome'] == 'timeout' for r in rr)} too slow, {sum(r['outcome'] == 'crash' for r in rr)} crash, {sum(r['outcome'] == 'wrong' for r in rr)} wrong outputs in {len(rr)} tries"
    worst = max(s["failures"], key=lambda p: sum(v["passed"] < v["n"] for v in s["failures"][p]["cells"].values()))
    misses = sum(v["passed"] < v["n"] for v in s["failures"][worst]["cells"].values())
    need(misses > 0 and worst in s["problems"], "the worst failure problem belongs to the main ladder")
    F["worst_failure"] = f"{plabel(worst)} has misses in {misses} of {len(every)} configs"
    F["hl_timeouts"] = str(oc["timeout"]); F["hl_crashes"] = str(oc["crash"]); F["hl_attempts"] = str(len(hl_all))
    hm = [r for r in main_rows if r["config"] == "haiku-medium" and not r["passed"]]
    need(len(hm) == 1 and hm[0]["outcome"] == "wrong" and hm[0]["problem"].startswith("p05"), "haiku-medium's one miss")
    # method and limitations
    F["bound_problems"] = pct(0.05 ** (1 / nprob)); F["bound_tasks"] = pct(0.05 ** (1 / ntask))
    from analysis.summarize import BREAK_AT; from analysis.stats import N_BOOT
    F["break_at"] = pct(BREAK_AT); F["n_boot"] = n(N_BOOT)
    F["lb_l2"] = f"{lb['by_rung']['L2']['passed']}/{lb['by_rung']['L2']['n']}"; F["lb_l3"] = f"{lb['by_rung']['L3']['passed']}/{lb['by_rung']['L3']['n']}"
    need(lb["breaking_point"] == "L2" and ll["breaking_point"] == "L6", "breaking points as described")
    p06 = [r for r in rows if r["config"] == "luna-low-bare" and r["problem"] == "p06_calc"]
    big = max(p06, key=lambda r: r["cached_tok"]); F["cache_max"] = f"{big['cached_tok'] / 1000:.1f}k"; need(min(r["cached_tok"] for r in p06) == 0, "some p06 call had no cache")
    F["cache_swing"] = f"{max(cost_uncached(r) / cost(r) for r in rows if r['cli'] == 'codex' and cost(r)):.1f}×"  # largest over every Codex call
    F["lanes"] = str(max(r["lanes"] for r in rows if r.get("lanes")))
    # appendix: luna rescue
    a = arms; F["rescue_n"] = str(a["luna-low"]["n"])
    for c, v in a.items():
        k = re.sub(r"\W", "_", c); F[f"r_{k}_k"] = f"{v['passes']}/{v['n']}"; F[f"r_{k}_upp"] = usd(v["usd_per_pass"]); F[f"r_{k}_s"] = f"{v['median_s']:.0f}s"
    b0, b1, b2, sc, ee = a["luna-low"], a["luna-low-noshell-B1"], a["luna-low-noshell-B2"], a["luna-low-selftest"], a["luna-low+haiku-low-repair"]
    F["r_b1_gain"] = str(b1["passes"] - b0["passes"]); F["r_b2_loss"] = str(b1["passes"] - b2["passes"])
    F["r_c_cost_x"] = x(sc["usd_per_pass"], b0["usd_per_pass"]); F["r_c_time_x"] = x(sc["median_s"], b0["median_s"])
    need(sc["usd_per_pass"] > a["haiku-low"]["usd_per_pass"] and sc["passes"] < a["haiku-low"]["passes"], "self-test costs more than haiku for fewer passes")
    F["r_e_luna"] = f"{sum(r['luna_passed'] for r in ee['rows'])}/{ee['n']}"; F["r_e_changed"] = str(sum(r["haiku_changed"] for r in ee["rows"]))
    F["r_e_haiku_share"] = pct(sum(r["haiku_cost_usd"] for r in ee["rows"]) / ee["usd_total"])
    F["orchestrator"] = "Claude Opus 5.5"  # the model that designed, ran and checked this benchmark; not a measured config
    hr, lr, hv, sm = a["luna-high-bare+haiku-on-fail"], a["luna-low+haiku-on-fail"], a["luna-high-bare+haiku-review-all"], a["sonnet-medium"]
    need(hv["passes"] == hv["n"] == sm["passes"], "luna-high + Haiku review and sonnet-medium never failed on the rescue set")
    hm = a["haiku-medium"]; need(hm["passes"] == hm["n"] and hm["usd_per_pass"] < hv["usd_per_pass"], "haiku-medium alone: no miss, cheaper than the pipeline")
    F["hm_vs_pipe_x"] = x(hv["usd_per_pass"], hm["usd_per_pass"]); F["r_pids"] = ", ".join(plabel(q) for q in luna_rescue.PIDS)
    F["sm_vs_hh_x"] = x(cfg["sonnet-medium"]["usd_per_pass"], ex["haiku-high"]["usd_per_pass"])
    F["sm_vs_hm_x"] = f"{cfg['sonnet-medium']['usd_per_pass'] / cfg['haiku-medium']['usd_per_pass']:.0f}×"
    hm7 = hard["haiku-medium"]; F["hm_l7_k"] = f"{hm7['passes']}/{hm7['n']}"
    F["hm_l7_miss"] = " and ".join(f"{v} {k}" for k, v in sorted(hm7["outcomes"].items()) if k != "pass") or "none"
    F["g_hi_fixed"] = str(sum(r["repaired"] for r in hr["rows"]))
    need(all(r["passed"] for r in hr["rows"] if r["repaired"]), "Haiku fixed every answer whose sample tests failed")
    fixed = int(F["g_hi_fixed"])
    F["g_hi_fixed_words"] = "both" if fixed == 2 else f"all {fixed}"
    F["g_hi_bad"] = str(sum(r["repaired"] for r in hr["rows"]) + hr["n"] - hr["passes"])
    need(a["haiku-low-plan+luna-high-bare"]["passes"] == a["luna-high-bare"]["passes"], "plan first leaves luna-high-bare passes unchanged")
    need(a["haiku-low-plan+luna-low"]["passes"] > a["luna-low"]["passes"], "planning helps luna-low")
    need(all(a["haiku-low-plan+" + c]["usd_per_pass"] > a[c + "+haiku-on-fail"]["usd_per_pass"] for c in ("luna-low", "luna-high-bare")), "both plan-first arms cost more than their corresponding check-after arms")
    F["g_hi_missed"] = str(hr["n"] - hr["passes"]); F["g_lo_fixed"] = str(sum(r["repaired"] for r in lr["rows"]))
    # appendix: the pilot (results/2026-10-22-pilot.jsonl) and the trim probe's pair step on three of its problems
    pl = s["pilot"]; prow = load(os.path.join(RES, "2026-10-22-pilot.jsonl"))
    need(all(v["passes"] == v["n"] for v in pl.values()), "every pilot run passed")
    F["pilot_configs"] = str(len(pl)); F["pilot_runs"] = str(sum(v["n"] for v in pl.values())); F["pilot_problems"] = str(len({r["problem"] for r in prow}))
    pf = s["pilot_fast"]; F["fast_mult"] = f'{json.load(open(os.path.join(RES, "prices.json")))["fast_mode_multiplier"]:g}×'
    F["fast_problems"] = str(len({r["problem"] for r in prow if r["config"] == "sol61-low-defa"})); F["fast_rounds"] = str(pf["sol61-low/default"]["n"] // int(F["fast_problems"]))
    assert all(v["passes"] == v["n"] for v in pf.values()), "fast-mode text says every call passed"
    for k, v in pf.items(): F[f"fast_{k.split('-')[0].rstrip('0123456789')}_{'def' if k.endswith('default') else 'fast'}"] = f"{v['median_s']:.1f}"
    F["pilot_r2_configs"] = str(sum(1 for v in pl.values() if v["problems"] > 3))
    need(all(v["passes"] == v["n"] for v in pr.values()), "every trim-probe pair config passed")
    F["pair_problems"] = str(len({r["problem"] for r in load(os.path.join(RES, "2026-10-22b-trim.jsonl")) if r["step"] == "pair"}))
    nf = pr["luna/nofeat"]; need(nf["usd_per_call"] > pr["luna/base"]["usd_per_call"], "tool features off costs more per call than stock")
    need(nf["uncached_calls"] > nf["n"] / 2 and pr["luna/base"]["uncached_calls"] == 0, "the costlier level is the one that missed the cache")
    F["nofeat_nocache"] = str(nf["uncached_calls"]); F["nofeat_calls"] = str(nf["n"])
    need(all(cfg[c]["by_rung"]["L1"]["passed"] == cfg[c]["by_rung"]["L1"]["n"] > cfg[c]["by_rung"]["L2"]["passed"] for c in ("luna-low", "luna-medium")), "luna low/medium pass L1 and already fail at L2")
    F["pilot_luna_call"] = usd(pr["luna/noshell"]["usd_per_call"]); F["pilot_haiku_call"] = usd(pr["haiku"]["usd_per_call"])
    F["pilot_luna_k"] = f"{pr['luna/noshell']['passes']}/{pr['luna/noshell']['n']}"
    q = [r for r in quality_rows() if r["outcome"] == "pass" and r["phase"] in ("main", "exploratory", "escalation") and r.get("time_ratio") is not None]
    F["q_rows"] = str(len([r for r in quality_rows() if r["outcome"] == "pass" and r["phase"] in ("main", "exploratory", "escalation")]))
    if q:
        w = max(q, key=lambda r: r["time_ratio"])
        F["q_worst_x"] = f"{w['time_ratio']:.0f}×"; F["q_worst_problem"] = plabel(w["problem"]); F["q_worst_cfg"] = DISP(w["config"])
        slow = [r for r in q if r["problem"] == w["problem"] and r["time_ratio"] >= 10]  # 10x: one config's extreme outlier must not hide the rest
        F["q_slow_n"] = str(len(slow)); F["q_slow_cfgs"] = str(len({r["config"] for r in slow})); F["q_slow_lo"] = f"{min(r['time_ratio'] for r in slow):.0f}×"
        need(w["ref_time_exp"] < 0.2, "the slowest problem's reference is near constant time"); F["q_worst_ref_exp"] = f"{w['ref_time_exp']:.2f}"
        need(len({r["config"] for r in slow}) > 1, "the slowest problem is slow across configs, not one config's outlier")
    fm = s.get("fastmode") or {}
    if len(fm) == 3:
        c0, cf, cx = fm["sol61-high"], fm["sol61-high-fast"], fm["sol61-xhigh"]
        need(c0["passes"] == cf["passes"] == cx["passes"] == c0["n"], "fast mode and xhigh pass every hard-set attempt, like the control")
        need(cf["median_s"] < c0["median_s"] < cx["median_s"], "fast mode is the quickest and xhigh the slowest")
        F["fm_n"] = str(c0["n"]); F["fm_rep_lo"] = str(min(c0["repeats"])); F["fm_rep_hi"] = str(max(c0["repeats"]))
        F["fm_ctrl_s"] = f"{c0['median_s']:.1f}"; F["fm_fast_s"] = f"{cf['median_s']:.1f}"; F["fm_x_s"] = f"{cx['median_s']:.1f}"
        F["fm_faster"] = f"{(1 - cf['median_s'] / c0['median_s']) * 100:.0f}%"
        F["fm_mult"] = f"{json.load(open(os.path.join(RES, 'prices.json')))['fast_mode_multiplier']:g}×"
        F["fm_x_cost"] = f"{cx['usd_per_pass'] / c0['usd_per_pass']:.1f}×"; F["fm_x_out"] = f"{cx['out_median'] / c0['out_median']:.1f}×"
        b = json.load(open(BLIND)) if os.path.exists(BLIND) else None
        if b:
            F["bl_n"] = str(len(b["items"])); F["bl_probs"] = str(len({i["problem"] for i in b["items"]})); F["bl_cfgs"] = str(len({i["config"] for i in b["items"]}))
            blk = {i["config"] for i in b["items"] if i["block"]}
            need(blk == {"sonnet-medium"}, "every solution the blind reader would block came from sonnet-medium")
            F["bl_blocks"] = str(sum(i["block"] for i in b["items"]))
            counts = {c: sum(i["config"] == c for i in b["items"]) for c in {i["config"] for i in b["items"]}}
            need(len(set(counts.values())) == 1, "blind read has the same sample size per config")
            F["blind_caption"] = f"Reader: {b['reviewer']}. Method: {b['method']}. Score: {b['scale'].replace('block =', 'would block =')}. {next(iter(counts.values()))} solutions per config."
    # fast mode on the main ladder and L7 (exploratory, 2026-10-24): same model and effort, priority tier
    for k, (b0, b1) in {"s61": ("sol61-high", "sol61-high-fast"), "ast": ("astra-medium", "astra-medium-fast")}.items():
        d, f = ex[b0], ex[b1]; dh, fh = hard[b0], hard[b1]
        need(d["passes"] == d["n"] == f["passes"] == f["n"] and dh["passes"] == dh["n"] == fh["passes"] == fh["n"], f"{b1} and {b0} never failed on the main ladder or L7")
        need(f["latency_s"]["median"] < d["latency_s"]["median"] and fh["latency_s"]["median"] < dh["latency_s"]["median"], f"{b1} is quicker than {b0}")
        need(f["usd_per_pass"] > d["usd_per_pass"], f"{b1} costs more per pass than {b0}")
        F[f"ff_{k}_k"] = f"{f['passes']}/{f['n']}"; F[f"ff_{k}_hk"] = f"{fh['passes']}/{fh['n']}"
        F[f"ff_{k}_upp"] = usd(f["usd_per_pass"]); F[f"ff_{k}_dupp"] = usd(d["usd_per_pass"])
        F[f"ff_{k}_med"] = f"{f['latency_s']['median']:.1f}"; F[f"ff_{k}_dmed"] = f"{d['latency_s']['median']:.1f}"
        F[f"ff_{k}_faster"] = f"{(1 - f['latency_s']['median'] / d['latency_s']['median']) * 100:.0f}%"; F[f"ff_{k}_x"] = x(f["usd_per_pass"], d["usd_per_pass"])
        # Cached statement-example replay is the evidence for this counterfactual pipeline.
        checked = fast_gate.summary()
        for c in (b0, b1):
            need(checked[c]["all"]["failures"] == 0, f"{c} pipeline would need a Haiku call and was not run")
        pm, ph = checked[b1]["main"]["pipeline"], checked[b1]["hard"]["pipeline"]
        dm = checked[b0]["main"]["pipeline"]
        for source, derived in ((f, pm), (fh, ph), (d, dm)):
            need(source["passes"] == derived["passes"] and source["n"] == derived["n"]
                 and source["usd_per_pass"] == round(derived["usd_per_pass"], 6)
                 and source["latency_s"]["median"] == round(derived["median_s"], 2), "derived pipeline equals its builder's ff numbers")
        F[f"pf_{k}_k"] = f"{pm['passes']}/{pm['n']}"; F[f"pf_{k}_hk"] = f"{ph['passes']}/{ph['n']}"
        F[f"pf_{k}_upp"] = usd(pm["usd_per_pass"]); F[f"pf_{k}_med"] = f"{pm['median_s']:.1f}"
        F[f"pf_{k}_dupp"] = usd(dm["usd_per_pass"]); F[f"pf_{k}_dmed"] = f"{dm['median_s']:.1f}"
        F[f"pf_{k}_fails"] = str(checked[b1]["all"]["failures"])
        F[f"pf_{k}_n_all"] = str(checked[b1]["main"]["n"] + checked[b1]["hard"]["n"])
        F[f"pf_{k}_status"] = checked[b1]["all"]["status"]
        need(all(F[f"pf_{k}_{field}"] == F[f"ff_{k}_{field}"] for field in ("k", "hk", "upp", "med", "dupp", "dmed")), "pf facts equal ff facts")
    need(min((c for c, v in every.items() if v["passes"] == v["n"]), key=lambda c: every[c]["latency_s"]["median"]) == "astra-medium-fast",
         "astra-medium fast is fastest among main-ladder configs with no misses")
    F["growth_margin"] = str(GROWTH_MARGIN)
    F["n_solutions"] = str(sum(1 for _, _, fs in os.walk(os.path.join(RES, "solutions")) for f in fs if f.endswith(".py")))
    # Codex additions (exploratory, run after the report at the operator's request)
    nr = [r for r in rows if r["config"] in NEW_CODEX and r["phase"] != "fastmode"]; F["new_date"] = min(r["ts"] for r in nr)[:10]; F["n_new_codex"] = str(len(NEW_CODEX))
    nu = sum(map(cost, nr + [r for r in agent if r["config"] in NEW_CODEX]))  # function and repo-task runs alike
    ffu = sum(map(cost, [r for r in rows if r["config"] in FAST_CONFIGS and r["phase"] != "fastmode"]))  # fast-mode runs on the main ladder and L7 (2026-10-24)
    F["codex_new_usd"] = usd(nu); F["codex_old_usd"] = usd(sp['codex_proxy_usd'] - nu - sp['codex_fastmode_usd'] - ffu); F["ff_usd"] = usd(ffu); F["fm_usd"] = usd(sp['codex_fastmode_usd'])
    for c in NEW_CODEX:
        k = "x_" + c.replace("-", "_"); e, h = ex[c], hard[c]
        F[k + "_k"] = f"{e['passes']}/{e['n']}"; F[k + "_upp"] = usd(e["usd_per_pass"]); F[k + "_med"] = f"{e['latency_s']['median']:.1f}"
        F[k + "_hk"] = f"{h['passes']}/{h['n']}"; F[k + "_hupp"] = usd(h["usd_per_pass"])
    for c in ("luna-high", "sol61-medium"):
        F["x_base_" + c.replace("-", "_") + "_hk"] = f"{hard[c]['passes']}/{hard[c]['n']}" if c in hard else "–"
    need(all(ex[c]["passes"] == ex[c]["n"] for c in ("sol56-high", "astra-medium")), "sol56-high and astra-medium never failed L1-L6")
    need(hard["luna-high"]["passes"] > hard["luna56-high"]["passes"] and ex["luna56-high"]["usd_per_pass"] > ex["luna-high"]["usd_per_pass"], "gpt-6 luna-high beats 5.6 luna-high on L7 and costs less")
    need(hard["astra-medium"]["passes"] == hard["astra-medium"]["n"] > hard["sol56-high"]["passes"], "astra perfect on L7, sol56-high not")
    F["x_sol56_vs_hm"] = f"{ex['sol56-high']['usd_per_pass'] / cfg['haiku-medium']['usd_per_pass']:.0f}×"
    sm_all = cfg["sonnet-medium"]["usd_per_pass"]; perfect = [c for c in list(cfg) + list(ex) if (cfg.get(c) or ex[c])["passes"] == (cfg.get(c) or ex[c])["n"] and c in hard and hard[c]["passes"] == hard[c]["n"]]
    need(sorted(perfect) == ["astra-medium", "astra-medium-fast", "haiku-high", "sol61-high", "sol61-high-fast", "sonnet-medium"] and min(ex[c]["usd_per_pass"] for c in ("astra-medium", "sol61-high")) > sm_all > ex["haiku-high"]["usd_per_pass"],
         "haiku-high is the cheapest config with no miss anywhere, then sonnet-medium; astra-medium and sol61-high the only others")
    # haiku-high (exploratory, added 2026-10-24): the parity question, the cheapest config with no miss against the others
    hx, hxh, smh7 = ex["haiku-high"], hard["haiku-high"], hard["sonnet-medium"]
    F["hh_k"] = f"{hx['passes']}/{hx['n']}"; F["hh_hk"] = f"{hxh['passes']}/{hxh['n']}"; F["hh_upp"] = usd(hx["usd_per_pass"]); F["hh_hupp"] = usd(hxh["usd_per_pass"])
    F["hh_med"] = f"{hx['latency_s']['median']:.1f}"; F["hh_p90"] = f"{hx['latency_s']['p90']:.0f}"; F["hh_hmed"] = f"{hxh['latency_s']['median']:.0f}"
    F["hh_vs_hm"] = x(hx["usd_per_pass"], cfg["haiku-medium"]["usd_per_pass"]); F["hh_out_x"] = x(hx["tokens_mean"]["out_tok"], cfg["haiku-medium"]["tokens_mean"]["out_tok"])
    for k, c in (("sm", "sonnet-medium"), ("s61h", "sol61-high"), ("astra", "astra-medium")):
        v = cfg.get(c) or ex[c]; F[f"hh_{k}_x"] = f"{v['usd_per_pass'] / hx['usd_per_pass']:.0f}×"; F[f"hh_{k}_hx"] = f"{hard[c]['usd_per_pass'] / hxh['usd_per_pass']:.0f}×"
        F[f"l7_{k}_med"] = f"{hard[c]['latency_s']['median']:.0f}"
    need(hx["latency_s"]["median"] < min(ex[c]["latency_s"]["median"] for c in ("astra-medium", "sol61-high")) and hx["latency_s"]["median"] > cfg["sonnet-medium"]["latency_s"]["median"],
         "haiku-high is faster than both Codex flagships on L1-L6, slower than sonnet-medium")
    need(hxh["latency_s"]["median"] < min(hard[c]["latency_s"]["median"] for c in ("astra-medium", "sol61-high")) and hxh["latency_s"]["median"] > smh7["latency_s"]["median"],
         "haiku-high is faster than both Codex flagships on L7, slower than sonnet-medium")
    hmx = cfg["haiku-medium"]; need(hmx["passes"] < hmx["n"] and hm7["passes"] < hm7["n"], "haiku-medium misses on L1-L6 and L7; haiku-high is where parity starts")
    need(all(ag[c]["hidden_pass"] == ag[c]["n"] for c in ("astra-medium", "sol61-high")), "both trusted Codex configs passed every repo task")
    F["x_s61h_vs_sm"] = x(ex["sol61-high"]["usd_per_pass"], sm_all)
    # trusted Codex builders: who bills what. Codex calls bill the Codex subscription, so their Claude $ is zero by construction.
    ah, sh = ex["astra-medium"], ex["sol61-high"]
    F["x_astra_vs_s61h"] = x(ah["usd_per_pass"], sh["usd_per_pass"])
    need(ah["latency_s"]["median"] < sh["latency_s"]["median"] and ag["astra-medium"]["latency_s"]["median"] < ag["sol61-high"]["latency_s"]["median"], "astra faster than sol61-high")
    F["ag_n"] = str(ag["sol61-high"]["n"]); F["claude_zero"] = "$0"
    F["ag_hh_k"] = f"{ag['haiku-high']['hidden_pass']}/{ag['haiku-high']['n']}"
    F["ag_claude_med"] = f"{statistics.mean(ag[c]['latency_s']['median'] for c in ('haiku-low', 'sonnet-medium')):.0f}"
    ga = arms
    for c in ("sol61-high+haiku-on-fail", "astra-medium+haiku-on-fail"):
        g = ga[c]; need(g["passes"] == g["n"] and not any(r["repaired"] for r in g["rows"]), f"{c} never failed and never called Haiku on the rescue set"); F["g_" + c.split("-")[0] + "_repairs"] = str(sum(r["repaired"] for r in g["rows"]))
        F["g_" + c.split("-")[0] + "_cupp"] = usd(g["claude_usd_per_pass"])
    F["x_astra_vs_sm"] = f"{ex['astra-medium']['usd_per_pass'] / sm_all:.0f}×"
    F["x_l56_vs_lh"] = x(ex["luna56-high"]["usd_per_pass"], ex["luna-high"]["usd_per_pass"])
    F["ag_sm_k"] = f"{ag['sonnet-medium']['hidden_pass']}/{ag['sonnet-medium']['n']}"
    for k, c in (("hl", "haiku-low"), ("sm", "sonnet-medium")):
        F[f"l7_{k}_k"] = f"{hard[c]['passes']}/{hard[c]['n']}"
    F["ci_level"] = "95%"
    F["repeat_lo"] = str(min(r["repeat"] for r in main_rows))
    F["r_luna_high_bare_miss"] = str(a["luna-high-bare"]["n"] - a["luna-high-bare"]["passes"])
    F["n_exploratory"] = str(len(ex)); F["exploratory_names"] = ", ".join(map(DISP, ex))
    expected = lambda rung: "Easy" if rung == 1 else "Medium" if rung <= 3 else "Hard"
    disagree = [p for p, v in s["problems"].items() if configs.LC[p] != expected(v["rung"])]
    need(disagree, "some LeetCode badges disagree with rung order")
    F["badge_disagreements"] = ", ".join(f"{plabel(p, s['problems'][p]['rung'])} is {configs.LC[p]}" for p in disagree)
    return F


def md_table(head, rows, bold=None):
    """Persist table cells, including derived numbers, before rendering."""
    return {"head": head, "rows": rows}


def _tables(s, arms):
    T = {}; cfg, ex = s["configs"], s["exploratory"]; nprob = len(s["problems"])
    T["result"] = md_table(["config", "pass@1", "95% CI", "median s", "p90 s", "$ per pass", f"total $ ({cfg['haiku-low']['n']} calls)", "$ kind"],
                           [[DISP(c) + (" †" if c in ex else ""), f"{pct(v['pass_at_1'])} ({v['passes']}/{v['n']})", ci_text(v["passes"], v["n"], v["ci95"], nprob),
                             f"{v['latency_s']['median']:.1f}", f"{v['latency_s']['p90']:.1f}", f"{usd(v['usd_per_pass'])}", f"{usd(v['usd_total'])}", v["cost_kind"]]
                            for c, v in {**cfg, **ex}.items()])
    T["result_detail"] = md_table(["set", "config", "95% CI", "p90 s", f"total $ ({cfg['haiku-low']['n']} calls)", "$ kind"],
                                  [["Ladder", DISP(c) + (" (exploratory)" if c in ex else ""), ci_text(v["passes"], v["n"], v["ci95"], nprob),
                                    f"{v['latency_s']['p90']:.1f}", usd(v["usd_total"]), v["cost_kind"]]
                                   for c, v in {**cfg, **ex}.items()])
    T["tokens"] = md_table(["config", "mean input", "of which cached", "mean output", "of which reasoning", "$ per 1k tokens"],
                           [[DISP(c) + (" †" if c in ex else ""), n(v["tokens_mean"]["in_tok"]), n(v["tokens_mean"]["cached_tok"]), n(v["tokens_mean"]["out_tok"]),
                             n(v["tokens_mean"]["reasoning_tok"]), usd(v["usd_per_1k_tokens"])]
                            for c, v in {**cfg, **ex}.items()])
    from bench.trim_probe import LEVELS
    fl = s["trim"]["floor"]; names = {"base": "stock harness", "nodoc": "+ no project docs", "noctx": "+ no env/permission context", "nofeat": "+ tool features off",
                                       "mininst": "+ one-line system prompt", "noshell": "+ shell tools off"}
    lv = [l for l in LEVELS if any(k.endswith("/" + l) for k in fl)]
    T["floor"] = md_table(["model"] + [names[l] for l in lv],
                          [[{"luna": "gpt-6-luna", "terra": "gpt-5.6-terra"}[m]] + [n(fl[f"{m}/{l}"]["in_tok"]) for l in lv] for m in dict.fromkeys(k.split("/")[0] for k in fl)])
    hard = s["hard"]; hp = sorted({p for v in hard.values() for p in v["by_problem"]})
    T["l7"] = md_table(["config", "passed", "95% CI"] + [p[:3] for p in hp] + ["median s", "mean reasoning tokens", "$ per pass", "$ kind"],
                       [[c, f"{v['passes']}/{v['n']}", ci_text(v["passes"], v["n"], v["ci95"], len(hp))] + [f"{v['by_problem'].get(p, 0)}/5" for p in hp]
                        + [f"{v['latency_s']['median']:.1f}", n(v["tokens_mean"]["reasoning_tok"]), f"{usd(v['usd_per_pass'])}", v["cost_kind"]] for c, v in hard.items()])
    fail = s["failures"]; cols = list(dict.fromkeys(c for f in fail.values() for c in f["cells"]))
    ab = {"wrong": "w", "crash": "c", "timeout": "t", "no_code": "n"}

    def cell(d):
        if not d: return "–"
        f = " ".join(f"{k}{ab[o]}" for o, k in sorted(d["fails"].items()))
        k = f"**{d['passed']}**" if d["passed"] * 5 <= 2 * d["n"] else str(d["passed"])
        return k + (f" ({f})" if f else "")
    T["fail"] = md_table(["problem"] + cols, [[f"{p[:3]} L{f['rung']}"] + [cell(f["cells"].get(c)) for c in cols] for p, f in fail.items()])
    ag = s["agentic"]; at = json.load(open(os.path.join(RES, "agentic_tests.json")))
    T["agentic"] = md_table(["config", "hidden tests passed", "complete task", "runs that wrote the requested test file", "test functions added", "median s", "$ per run", "$ kind"],
                            [[c, f"{v['hidden_pass']}/{v['n']}", f"{v['task_complete']}/{v['n']}", f"{v['own_tests_written']}/{v['n']}",
                              (lambda rr: "no transcripts" if not rr else str(sum(r["test_functions_added"] for r in rr)) if all(r["test_functions_added"] is not None for r in rr)
                               else f"≥{sum(r['test_functions_lower_bound'] for r in rr)}")([r for r in at if r["config"] == c]),
                              f"{v['latency_s']['median']:.1f}", f"{usd(v['usd_per_run'])}", v["cost_kind"]] for c, v in sorted(ag.items(), key=lambda kv: (kv[1]["usd_per_run"] is None, kv[1]["usd_per_run"] or 0))])
    a = arms
    T["rescue"] = md_table(["config", "passed", "$ per pass", "median s"], [[v["label"], f"{v['passes']}/{v['n']}", f"{usd(v['usd_per_pass'])}", f"{v['median_s']:.1f}"] for v in a.values()])
    pr = s["trim"]["pair"]; lab = {"haiku": "haiku-low, tools off", "luna/base": "luna-low, stock harness", "luna/nofeat": "luna-low, tool features off", "luna/noshell": "luna-low, stripped"}
    T["pilot"] = md_table(["config", "passes", "median input", "median s", "$ per call", "$ kind"],
                          [[lab[c], f"{v['passes']}/{v['n']}", n(v["in_median"]), f"{v['median_s']:.1f}", f"{usd(v['usd_per_call'])}", v["cost_kind"]] for c, v in pr.items() if c in lab])
    T["quality"] = quality_table(s)
    T["fastmode"], T["blind"] = fastmode_tables(s)
    T["configs"] = md_table(["config", "CLI", "model", "effort"], [[c, {"claude": "Claude Code", "codex": "Codex CLI"}[v["cli"]], v["model"], v["effort"]] for c, v in cfg.items()])
    return T


def quality_rows():
    return [json.loads(l) for l in open(QUALITY)] if os.path.exists(QUALITY) else []


def quality_fast_note(s):
    """Describe quality coverage by phase, without confusing the two fast runs."""
    q = [r for r in quality_rows() if r.get("outcome") == "pass"]
    parts = []
    for c in ("sol61-high-fast", "astra-medium-fast"):
        main = [r for r in q if r["config"] == c and r["phase"] in ("main", "exploratory", "escalation")]
        parts.append(f"{DISP(c)}: {len(main)} main-ladder passing solutions scored in this table." if main else f"{DISP(c)}: main-ladder solutions not scored.")
        rescue = [r for r in q if r["config"] == c and r["phase"] == "fastmode"]
        if rescue:
            parts.append(f"Its separate {len(rescue)}-attempt {configs.set_label("rescue set").removesuffix(" set")} run is scored in the ‘Codex fast mode and xhigh’ table below.")
        else:
            parts.append(f"No separate {configs.set_label('rescue set').removesuffix(' set')}-run quality scores are available.")
    return " ".join(parts)


def quality_table(s):
    q = [r for r in quality_rows() if r.get("phase") in ("main", "exploratory", "escalation") and r.get("outcome") == "pass"]
    if not q: return "_results/quality.jsonl not generated yet._"
    med = lambda xs: statistics.median(xs) if xs else None
    order = list(s["configs"]) + list(s["exploratory"])
    out = []
    for c in order:
        rr = [r for r in q if r["config"] == c]  # luna-high's 15 escalation calls are part of its full-ladder run (same cache keys)
        if not rr: continue
        need(len(rr) == (s["configs"].get(c) or s["exploratory"][c])["passes"], f"quality rows cover every passing {c} solution")
        tr = [r["time_ratio"] for r in rr if r.get("time_ratio") is not None]; mr = [r["mem_ratio"] for r in rr if r.get("mem_ratio") is not None]
        slow = sum(1 for r in rr if r.get("time_exp") is not None and r.get("ref_time_exp") is not None and r["time_exp"] - r["ref_time_exp"] > GROWTH_MARGIN)
        out.append([DISP(c) + (" †" if c in s["exploratory"] else ""), str(len(rr)), f"{med([r['loc'] for r in rr]):.0f}", f"{med([r['cc_max'] for r in rr]):.0f}",
                    f"{sum(r['lint_warnings'] for r in rr) / len(rr):.2f}", f"{med(tr):.2f}" if tr else "–", f"{slow}", f"{med(mr):.2f}" if mr else "–"])
    return md_table(["config", "passing solutions", "median LOC", "median max complexity", "lint warnings per solution", "time vs ref",
                     "worse growth", "mem vs ref"], out)


BLIND = os.path.join(ROOT, "results", "appendix", "blind_readability.json")
FM_LABEL = {"sol61-high": "sol61-high, default tier (separate control run, repeats {lo}-{hi})", "sol61-high-fast": "sol61-high ⚡", "sol61-xhigh": "sol61-xhigh, default tier"}


def fastmode_tables(s):
    fm = s.get("fastmode") or {}
    if not fm: return "_no fast-mode runs yet._", "_no blind read yet._"
    q = [r for r in quality_rows() if r.get("phase") == "fastmode" and r.get("outcome") == "pass"]; out = []
    for c, v in fm.items():
        rr = [r for r in q if r["config"] == c]; need(len(rr) == v["passes"], f"quality rows cover every passing fast-mode {c} solution")
        tr = [r["time_ratio"] for r in rr if r.get("time_ratio") is not None]
        out.append([FM_LABEL[c].format(lo=min(v["repeats"]), hi=max(v["repeats"])), f"{v['passes']}/{v['n']}", f"{v['median_s']:.1f}", n(v["out_median"]), f"{usd(v['usd_per_pass'])}",
                    f"{statistics.median(r['loc'] for r in rr):.0f}", f"{statistics.median(r['cc_max'] for r in rr):.0f}",
                    f"{sum(r['lint_warnings'] for r in rr) / len(rr):.2f}", f"{statistics.median(tr):.2f}" if tr else "–"])
    t1 = md_table(["config", "passed", "median s", "median output tokens", "$ per pass (proxy)", "median LOC", "median max complexity",
                   "lint per solution", "time vs ref"], out)
    b = json.load(open(BLIND)) if os.path.exists(BLIND) else None
    if not b: return t1, "_no blind read yet._"
    cs = sorted({i["config"] for i in b["items"]}, key=lambda c: -statistics.mean(i["score"] for i in b["items"] if i["config"] == c))
    t2 = md_table(["config", "solutions read", "mean score (1 to 10)", "would block"],
                  [[c, str(sum(1 for i in b["items"] if i["config"] == c)), f"{statistics.mean(i['score'] for i in b['items'] if i['config'] == c):.2f}",
                    str(sum(i["block"] for i in b["items"] if i["config"] == c))] for c in cs])
    return t1, t2


def _project(ds, summary):
    """Enrich the canonical rows, then expose the historical layout as a read-only view.

    summarize supplies paired statistics and experiment-specific metadata, never
    a second on-disk input. Shared measurements always come from the tidy rows.
    """
    summary = copy.deepcopy(summary)
    for block, source, set_ in (("configs", "main", "main ladder"), ("exploratory", "main", "main ladder"),
                                ("hard", "main", "L7 set"), ("agentic", "agentic", "repo tasks")):
        for c, v in summary[block].items():
            r = get(ds, c, set_, source)
            r.update({k: v[k] for k in ("cli", "model", "effort", "outcomes", "breaking_point") if k in v})
            v.update({"n": r["n"], "passes": r["passes"], "pass_at_1": r["pass_rate"], "misses": r["misses"],
                      "ci95": r["ci95"] or [r["pass_rate"], r["pass_rate"]], "ci95_plot": r["ci95_plot"],
                      "usd_per_pass": r["usd_per_pass"], "usd_text": usd(r["usd_per_pass"]), "usd_per_call": r["usd_per_call"], "usd_total": r["spend"],
                      "claude_usd_per_pass": r["claude_usd_per_pass"], "usd_saved_per_pass": r["usd_saved_per_pass"],
                      "usd_per_1k_tokens": r["usd_per_1k_tokens"], "by_group": r["by_group"],
                      "input_floor": r["input_floor"], "cost_kind": r["cost_kind"],
                      "latency_s": {"median": r["median_s"], "p25": r["p25_s"], "p75": r["p75_s"], "p90": r["p90_s"], "max": r["max_s"]},
                      "tokens_mean": {"in_tok": r["tokens_in_mean"], "cached_tok": r["tokens_cached_mean"],
                                      "out_tok": r["tokens_out_mean"], "reasoning_tok": r["tokens_reasoning_mean"]},
                      "by_rung": {g: {"passed": k, "n": n} for g, (k, n) in r["by_rung"].items()}})
            if block == "agentic":
                v.update(hidden_pass=r["passes"], hidden_pass_rate=r["pass_rate"], usd_per_run=r["usd_per_call"])
            # Additional numeric evidence is retained on the canonical row too.
            r["details"] = {k: v[k] for k in v if k not in ("latency_s", "tokens_mean", "by_rung", "by_group")}
    return summary


def _rescue(ds, arms, checked):
    """Keep measured arms on their own rows; only derived fast arms use a builder slice."""
    out = {}
    for c, a in arms.items():
        source, set_ = ("rescue", "rescue arms") if ("rescue", c) in configs.REGISTRY else ("main", "rescue set")
        r = get(ds, c, set_, source)
        a.update({k: r[k] for k in ("passes", "n", "pass_rate", "usd_per_pass", "claude_usd_per_pass", "median_s",
                                  "p25_s", "p75_s", "misses", "usd_saved_per_pass")})
        a["usd_total"] = r["spend"]
        a["derived"] = r["derived"]
        a["metrics_from"] = {"source": source, "config": c, "set": set_}
        out[c] = {k: v for k, v in a.items() if k != "rows"}
    for c in ("sol61-high-fast", "astra-medium-fast"):
        evidence = checked[c]
        need(evidence["all"]["failures"] == 0, f"{c} would need a Haiku call; pipeline was not run")
        p = evidence["rescue"]["pipeline"]; r = get(ds, c, "rescue set")
        need(p is not None and p["passes"] == r["passes"] and p["n"] == r["n"]
             and round(p["usd_per_pass"], 6) == r["usd_per_pass"]
             and round(p["median_s"], 2) == r["median_s"], f"{c} derived pipeline equals its builder")
        out[c + "+haiku-on-fail"] = dict(out[c], derived=True, derived_note=evidence["rescue"]["status"],
                                         derived_from={"source": "main", "config": c, "set": "rescue set"})
    return out


def _currency_ticks(values):
    """Dollar axis labels for every subset of the explorer, formatted once here.

    Axis bounds depend only on the selected min/max and linear/log mode. Keep
    the browser's geometry interactive without giving it another dollar formatter.
    """
    labels = {0.0: usd(0)}
    for low in values:
        for high in values:
            if low > high: continue
            lo, hi = low / 1.5, high * 1.5
            for e in range(math.floor(math.log10(lo)), math.ceil(math.log10(hi)) + 1):
                for m in (1, 2, 5):
                    v = m * 10 ** e
                    if lo * .999 <= v <= hi * 1.001: labels[v] = usd(v)
            pad = (high - low or abs(high) or 1) * .12
            lo, hi = max(0, low - pad), high + pad
            step = 10 ** math.floor(math.log10((hi - lo) / 5))
            step *= next(m for m in (1, 2, 2.5, 5, 10) if (hi - lo) / (m * step) <= 6)
            v = math.ceil(lo / step) * step
            while v <= hi + 1e-12:
                v = float(f"{v:.10g}")
                labels[v] = usd(v)
                v += step
    return sorted(labels.items())


def build(summary=None):
    ds = _base()
    if summary is None: summary, _, _ = summarize.build()
    s = _project(ds, summary)
    arms = luna_rescue.arms(); checked = fast_gate.summary()
    ds["rescue"] = _rescue(ds, arms, checked)
    ds["derived_pipelines"] = checked
    ds["design"] = {"rescue_problems": PIDS, "per_rung": len(s["problems"]) // len(s["configs"]["haiku-low"]["by_rung"]),
                    "fast_mode_multiplier": json.load(open(os.path.join(RES, "prices.json")))["fast_mode_multiplier"],
                    "host_agents_md": HOST_AGENTS_MD, "min_pass": MIN_PASS,
                    "usd_ticks": _currency_ticks([v["usd_per_pass"] for v in {**s["configs"], **s["exploratory"]}.values()])}
    s["design"] = ds["design"]
    ds["categories"] = {cat: {"n_configs": len(rr), "spend": sum(r["spend"] for r in rr)}
                        for cat in configs.CATEGORIES
                        if (rr := [r for r in catalog_rows(ds) if r["category"] == cat])}
    ds["report"] = s
    ds["facts"] = _facts(s, arms)
    ds["tables"] = _tables(s, arms)
    return ds


def view(ds):
    """Cached report-shaped projections of the canonical config/set rows."""
    return {**ds["report"], "rescue": ds["rescue"]}


def read():
    return json.load(open(PATH))


def text(ds):
    return json.dumps(ds, indent=1, ensure_ascii=False) + "\n"


def main():
    ds = build(); open(PATH, "w").write(text(ds))
    print(f"dataset: {len(ds['rows'])} rows, {len(keys(ds))} configs -> results/dataset.json")


if __name__ == "__main__":
    main()
