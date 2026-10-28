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

from analysis import configs, grok, stats
from analysis.luna_rescue import PIDS, claude_usd
from analysis.summarize import RES, ROOT, cost, load, scale

PATH = os.path.join(RES, "dataset.json")
FACTS_USED = os.path.join(RES, "report", "facts_used.json")  # facts the page renders; landcheck compares it with base
SEMI_URL = "https://newsletter.semianalysis.com/p/anthropic-subscriptions-offer-5x"

import re, copy, math
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
TERRA_TRIGGER = {"gap_points": 10, "ratio": (0.5, 2.0)}  # PLAN.md deviation 23: run terra high in fast mode only if this fires

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
    if source in ("rescue", "harness-bias") and r.get("cost_usd") is not None: return r["cost_usd"]
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


def _harness_rows():
    return summarize.harness_rows(load(os.path.join(RES, "appendix", "harness_bias.jsonl")))


def _rows():
    """[(source, name, set, row dict with _usd/_claude/_pass/_sec/_group)] from every results file."""
    out = []
    def add(src, name, st, r, ok, sec, group, usd, tin, tout):
        out.append((src, name, st, {"ok": bool(ok), "sec": sec, "group": group, "usd": usd, "claude": _claude(r, src, usd), "in": tin, "out": tout, "cached": r.get("cached_tok") or r.get("builder_cached") or 0, "reasoning": r.get("reasoning_tok") or 0, "cli": r.get("cli", r.get("builder_kind", "")), "rung": r.get("rung"), "file": r.get("_file")}))
    func = [r for r in summarize.function_rows() if r["phase"] != "warmup"]
    cover = defaultdict(set)
    for r in func:
        if r["rung"] <= 6 and r["repeat"] <= REPEATS and r["phase"] != "calibration": cover[r["config"]].add((r["problem"], r["repeat"]))
    for r in func:
        c = r["config"]
        if r["phase"] == "hard": st = "L7 set"
        elif r["phase"] == "calibration": st = "calibration"
        elif r["repeat"] > REPEATS: st = "extra repeats"
        else: st = "main ladder" if c not in configs.GROK_CONFIGS and len(cover[c]) == REPORT_PROBLEMS * REPEATS else "partial ladder"
        add("main", c, st, r, r["passed"], r["wall_s"], r["problem"], _usd(r, "main"), r["in_tok"], r["out_tok"])
        if c not in configs.GROK_CONFIGS and r["problem"] in PIDS and r["phase"] in ("main", "exploratory", "fastmode") and r["repeat"] <= REPEATS:  # the same rows again, as the rescue-set baseline
            add("main", c, "rescue set", r, r["passed"], r["wall_s"], r["problem"], _usd(r, "main"), r["in_tok"], r["out_tok"])
    for r in summarize.agentic_rows():
        add("agentic", r["config"], "repo tasks", r, r["hidden_pass"], r["wall_s"], r["task"], _usd(r, "agentic"), r["in_tok"], r["out_tok"])
    for r in load(os.path.join(RES, configs.SOURCES["trim"][0])):
        add("trim", r["config"], "trim probe", r, r["passed"], r["wall_s"], r["problem"], _usd(r, "trim"), r["in_tok"], r["out_tok"])
    for r in load(os.path.join(RES, configs.SOURCES["pilot"][0])):
        add("pilot", r["config"], "pilot", r, r["passed"], r["wall_s"], r["problem"], _usd(r, "pilot"), r["in_tok"], r["out_tok"])
    for r in summarize.rescue_rows():
        add("rescue", r["config"], "rescue arms", r, r["passed"], r["wall_s"], r["problem"], _usd(r, "rescue"), r["in_tok"], r["out_tok"])
    for r in load(os.path.join(RES, configs.SOURCES["pilot-agentic"][0])):
        add("pilot-agentic", f"pipeline {r['pipeline']}", "pilot repo task", r, r["hidden_pass"], r["builder_wall_s"], f"round {r['round']}", _usd(r, "pilot-agentic"), r["builder_in"], r["builder_out"])
    for f in configs.SOURCES["harness-bias"]:
        for r in (_harness_rows() if f == configs.SOURCES["harness-bias"][0] else load(os.path.join(RES, f))):
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
    sg = sum(x["usd"] for x in rr if x["cli"] == "grok" and x["usd"] is not None)
    return {"id": e["id"], "source": src, "config": name, "display": e["display"], "family": e["family"], "category": e["category"], "what": e["what"], "set": st, "derived": st in DERIVED, "files": sorted({x["file"] for x in rr if x["file"]}) or e["files"],
            "passes": k, "n": n, "pass_rate": round(k / n, 4), "ci95": ci, "groups": len(cells),
            "usd_per_pass": round(spend / k, 6) if k and complete else None, "claude_usd_per_pass": round(sc / k, 6) if k and complete else None,
            "codex_usd_per_pass": round((spend - sc - sg) / k, 6) if k and complete else None, "usd_per_call": round(spend / n, 6) if complete else None,
            "spend": round(spend, 6), "spend_claude": round(sc, 6), "spend_codex": round(spend - sc - sg, 6), "unknown_usd": n - len(known),
            **({"spend_grok": round(sg, 6)} if rr[0]["cli"] == "grok" else {}),
            "median_s": round(statistics.median(secs), 2), "p25_s": round(p25, 2), "p75_s": round(p75, 2),
            "tokens_in_mean": round(statistics.mean(x["in"] or 0 for x in rr)), "tokens_out_mean": round(statistics.mean(x["out"] or 0 for x in rr)),
            "tokens_cached_mean": round(statistics.mean(x["cached"] for x in rr)),
            "tokens_reasoning_mean": round(statistics.mean(x["reasoning"] for x in rr)),
            "input_floor": list(min((x["in"] or 0, x["cached"]) for x in rr)),
            "p90_s": round(stats.p90(secs), 2), "max_s": round(max(secs), 2),
            "by_group": {g: {"passes": sum(v), "n": len(v)} for g, v in cells.items()},
            "misses": n - k, "ci95_plot": ci or ([0.05 ** (1 / len(cells)), 1.0] if k == n else [0.0, 0.0]),
            "usd_saved_per_pass": round((spend - sc - sg) / k, 6) if k and complete else None,
            "usd_per_1k_tokens": (1000 * round(spend / n, 6) / (round(statistics.mean(x["in"] or 0 for x in rr)) + round(statistics.mean(x["out"] or 0 for x in rr)))) if complete and any((x["in"] or 0) + (x["out"] or 0) for x in rr) else None,
            "by_rung": dict(sorted(by_rung.items())), "cost_kind": "unmetered" if rr[0]["cli"] == "devin" else "measured" if summarize.measured(rr[0]) else "proxy"}


def _base():
    groups = defaultdict(list)
    for src, name, st, x in _rows(): groups[(src, name, st)].append(x)
    rows = [_row(src, name, st, rr) for (src, name, st), rr in groups.items()]
    need(all(not r["unknown_usd"] or r["config"] in configs.DEVIN_CONFIGS for r in rows), "every table row (except the Devin free tier, which reports no tokens or cost) has complete measured or proxy costs")
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


def usd(v, sig=2, tick=False):
    """Two decimals from $1; otherwise `sig` significant figures.

    Values keep trailing zeros so neighbours read at the same precision ($0.00090 beside $0.00089).
    Axis ticks (tick=True) drop them. Use sig=3 when a comparison needs the extra distinction.
    """
    if v is None: return "–"
    if v == 0: return "$0"
    if v >= 1: return f"${v:,.2f}"
    d = Decimal(f"{v:.{sig}g}")
    value = format(d, "f")
    if tick:
        return "$" + (value.rstrip("0").rstrip(".") if "." in value else value)
    places = max(0, sig - 1 - d.adjusted())
    return f"${d:.{places}f}"



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


def x(a, b, d=1, *, money=False, sig=2):
    # money/sig are kept for call sites; the ratio uses raw values so it matches the dataset
    return f"{a / b:.{d}f}×"


def about(v, step=10):
    return n(int(round(v / step) * step))


def paired(s, a, b):
    for d in s["paired"]:
        if (d["a"], d["b"]) == (a, b): return d
    raise KeyError((a, b))


def vs(s, c, b):
    return next(d for d in s["exploratory"][c]["vs"] if d["b"] == b)


def fairness_facts():
    """Page facts from committed appendix rows; never regenerate or grade the experiment."""
    rows = _harness_rows()
    result = harness_bias.pass_summary(rows)
    lo, hi = result['ci']
    need(result['missing'] == 0, "harness comparison has complete pairs")
    diff = result['diff']
    if lo <= 0 <= hi:
        answer = f"No bias of about {max(abs(lo), abs(hi)):.1f} or more was detectable."
        detail = "The confidence interval contains zero."
        takeaway = "The data do not establish a change in the models' pass-rate gap."
        uncertainty = "The interval includes zero bias."
    else:
        need(0 < lo and 0 < diff < 0.15, "harness-bias result is a positive tilt below the 0.15 bias threshold")
        answer = "Slightly."
        lifts = {}
        for config in harness_bias.CFGS:
            rates = {}
            for harness in ('claude-one-shot', 'codex-tool-loop'):
                cell = [r for r in rows if (r['harness'], r['config']) == (harness, config)]
                rates[harness] = sum(r['passed'] for r in cell) / len(cell)
            lifts[config] = rates['codex-tool-loop'] - rates['claude-one-shot']
        need(all(v > 0 for v in lifts.values()) and lifts['luna-low'] > lifts['haiku-low'],
             "both agent loops beat the one-shot runner, luna more")
        takeaway = "Both vendor agent CLIs improved pass rates. Codex CLI helped luna-low more."
        detail = (f"The pass-rate gap moved by {100 * diff:.0f} points. "
                  f"We pre-set {100 * .15:.0f} points as the bar for calling it bias.")
        uncertainty = "The interval excludes zero. " + (
            "It also permits bias above our threshold." if hi > 0.15 else "It stays below our threshold.")
    facts = dict(hb_answer=answer, hb_detail=detail, hb_diff=f"{diff:+.3f}", hb_takeaway=takeaway, hb_uncertainty=uncertainty, hb_ci=f"{lo:+.3f} to {hi:+.3f}",
                 hb_n_problems=str(len({r['problem'] for r in rows})),
                 hb_repeats=str(len({r['repeat'] for r in rows})))
    for harness, prefix in (('claude-one-shot', 'claude'), ('codex-tool-loop', 'codex')):
        for config in harness_bias.CFGS:
            cell = [r for r in rows if (r['harness'], r['config']) == (harness, config)]
            facts[f"hb_{prefix}_{config.replace('-', '_')}"] = f"{sum(r['passed'] for r in cell)}/{len(cell)}"
    improved = all(int(facts[f"hb_codex_{c.replace('-', '_')}"].split('/')[0]) >
                   int(facts[f"hb_claude_{c.replace('-', '_')}"].split('/')[0]) for c in harness_bias.CFGS)
    facts.update(hb_diff_points=f"{100 * diff:.0f}", hb_bar_points=f"{100 * .15:.0f}",
                 hb_range_points=f"{100 * lo:.0f} to {100 * hi:.0f}")
    for c in harness_bias.CFGS:
        one = [r for r in rows if r['config'] == c and r['harness'] == 'claude-one-shot']
        agent = [r for r in rows if r['config'] == c and r['harness'] == 'codex-tool-loop']
        key = c.replace('-', '_')
        facts[f'hb_{key}_gain'] = str(sum(r['passed'] for r in agent) - sum(r['passed'] for r in one))
        facts[f'hb_{key}_change'] = f"{sum(r['passed'] for r in one)}→{sum(r['passed'] for r in agent)}"
        facts[f'hb_{key}_n'] = str(len(one))
    if lo > 0:
        facts['hb_answer'] = f"Slightly: the gap moved {facts['hb_diff_points']} points."
        facts['hb_takeaway'] = (
            f"luna-low: {facts['hb_luna_low_change']} of {facts['hb_luna_low_n']} inside Codex CLI. "
            f"haiku-low: {facts['hb_haiku_low_change']} of {facts['hb_haiku_low_n']} inside Claude Code.")
        facts['hb_detail'] = (
            f"Gap moved {facts['hb_diff_points']} points "
            f"({95}% range {facts['hb_range_points']}); bias threshold was {facts['hb_bar_points']}.")
        facts['hb_uncertainty'] = "A bigger bias is possible."
    facts['hb_summary'] = " ".join(facts[k] for k in ('hb_takeaway', 'hb_detail'))
    facts['hb_qa'] = ([f"A: {facts['hb_answer']}",
        f"Inside Codex CLI, luna-low went from {facts['hb_claude_luna_low'].split('/')[0]} "
        f"to {facts['hb_codex_luna_low'].split('/')[0]} passes.",
        f"Inside Claude Code, haiku-low went from {facts['hb_claude_haiku_low'].split('/')[0]} "
        f"to {facts['hb_codex_haiku_low'].split('/')[0]} passes.",
        f"The gap moved {facts['hb_diff_points']} points, below our {facts['hb_bar_points']}-point bias threshold.",
        f"The {95}% range is {facts['hb_range_points']} points.",
        "A larger bias is possible."] if lo > 0 else [facts['hb_answer']])
    facts['hb_conclusion'] = ("Vendor agent CLIs improved both models." if improved
                              else "The runner comparison uses paired attempts.")
    for harness, key in (('claude-one-shot', 'one'), ('codex-tool-loop', 'agent')):
        for oc in ('wrong', 'crash'):
            facts[f'hb_luna_{oc}_{key}'] = str(sum(r['outcome'] == oc for r in rows if (r['harness'], r['config']) == (harness, 'luna-low')))
    need(int(facts['hb_luna_wrong_agent']) < int(facts['hb_luna_wrong_one']) and int(facts['hb_luna_crash_agent']) < int(facts['hb_luna_crash_one']),
         "the tool loop cut luna-low's wrong outputs and crashes")
    need(all(int(facts[f'hb_{h}_haiku_low'].split('/')[0]) > int(facts[f'hb_{h}_luna_low'].split('/')[0]) for h in ('claude', 'codex')),
         "haiku-low led luna-low in both runners")
    codex = [r for r in rows if r['harness'] == 'codex-tool-loop']
    facts['hb_errors'] = str(sum(r['outcome'] == 'harness_error' for r in codex))
    facts['hb_full_calls'] = str(len(rows))
    need(len(rows) == sum(len([r for r in rows if r['config'] == c and r['harness'] == h])
                         for c in harness_bias.CFGS for h in ('claude-one-shot', 'codex-tool-loop')),
         "full harness run counts every paired call")
    need(not any(r['outcome'] == 'timeout' or re.search(r'timeout|timed out|exceeded', r.get('error') or '', re.I)
                 for r in codex), "agent-CLI run had no timeouts")
    # Codex harness ts is recorded before invocation; wall_s is that invocation's duration.
    start = min(datetime.fromisoformat(r['ts']).timestamp() for r in codex)
    end = max(datetime.fromisoformat(r['ts']).timestamp() + r['wall_s'] for r in codex)
    facts['hb_minutes'] = f"{(end - start) / 60:.0f}"
    return facts


def _facts(s, arms):
    F = Facts(); cfg, ex, ag, hard = s["configs"], s["exploratory"], s["agentic"], s["hard"]
    rows = summarize.function_rows(); agent = summarize.agentic_rows(); main_rows = [r for r in rows if r["phase"] == "main"]
    every = {**cfg, **{c: v for c, v in ex.items() if c not in configs.ONE_REPEAT + configs.DEVIN_CONFIGS}}  # one-repeat extras are tables-only; Devin has 1 repeat and no $
    nprob = len(s["problems"]); ntask = len(next(iter(ag.values()))["by_task"])
    F.update(n_ladder_configs=str(len(every)), n_problems=str(nprob), n_tasks=str(ntask), n_configs=str(len(cfg)), n_l7=str(len({p for v in hard.values() for p in v["by_problem"]})),
             repeats=str(cfg["haiku-low"]["n"] // nprob), n_calls=str(cfg["haiku-low"]["n"]), n_all_problems=str(nprob + len({p for v in hard.values() for p in v["by_problem"]})),
             agent_repeats=str(next(iter(ag.values()))["n"] // ntask), n_rungs=str(len(cfg["haiku-low"]["by_rung"])), per_rung=str(nprob // len(cfg["haiku-low"]["by_rung"])))
    need(all(v["n"] == cfg["haiku-low"]["n"] for v in every.values()), "every function-track config has the same number of calls")
    F.update(fairness_facts())
    # Models and versions: one CLI version per vendor across the function track.
    by_cli = defaultdict(set)
    for r in rows:
        if r["config"] not in configs.GROK_CONFIGS and not r["config"].startswith("terra") and r["cli"] != "devin": by_cli[r["cli"], r["cli_version"]].add(r["model"])
    need(len({cli for cli, _ in by_cli}) == len(by_cli) == 2, "one CLI version per vendor")
    vers = dict(by_cli)
    F["versions_claude"] = next(f"Main bench, Claude Code {v}: {', '.join(sorted(m))}." for (c, v), m in vers.items() if c == "claude")
    F["versions_codex"] = next(f"Main bench, Codex CLI {v}: {', '.join(sorted(m))}." for (c, v), m in vers.items() if c == "codex")
    terra = defaultdict(set)  # the Terra rows (2026-10-28) ran on a later Codex build
    for r in rows:
        if r["config"].startswith("terra"): terra[r["cli_version"]].add(r["model"])
    F["versions_codex"] += "".join(f" Terra rows, Codex CLI {v}: {', '.join(sorted(m))}." for v, m in sorted(terra.items()))
    # The Codex-built bench (Whose bench?) also ran newer CLI builds.
    norm = lambda v: v.replace("codex-cli ", "").replace(" (Claude Code)", "")
    extra = defaultdict(set)
    for name in ("harness_bias", "codex_harness"):
        for r in load(os.path.join(RES, "appendix", f"{name}.jsonl")):
            v = norm(r["cli_version"])
            if (r["cli"], v) not in by_cli: extra[r["cli"]].add(v)
    need(set(extra) == {"claude", "codex"}, "Codex-built bench used other CLI builds on both sides")
    F["versions_extra"] = (f"Whose bench? also used Codex CLI {', '.join(sorted(extra['codex']))}"
                           f" and Claude Code {', '.join(sorted(extra['claude']))}.")
    dated = rows + agent + [r for source, paths in configs.SOURCES.items() if source not in ("main", "agentic")
                            for path in paths for r in load(os.path.join(RES, path))]
    days = sorted(r["ts"][:10] for r in dated if r.get("ts"))
    F["run_dates"] = f"All calls ran {days[0]} to {days[-1]}."
    F["cite"] = f"Cite as: DispatchBench ({days[-1][:4]}), github.com/chimera-defi/dispatchbench."
    # Function-track Codex calls never used a tool, so none could read the reference solutions.
    terra_rows = [r for r in rows if r["cli"] == "codex" and r["config"].startswith("terra")]
    func = [r for r in rows if r["cli"] == "codex" and not r["config"].startswith("terra")]
    need(all(isinstance(r.get("tool_items"), int) for r in func + terra_rows), "every function-track Codex row records tool_items")
    need(not any(r["tool_items"] for r in func), "no function-track Codex call used a tool")
    F["codex_tool_free"] = f"{n(len(func))} of {n(len(func))}"
    logged = [r for r in terra_rows if r["tool_items"]]  # the raw event type was not kept, only the count
    F["terra_tool_note"] = (f"Terra (added later) is the exception: {len(logged)} of {len(terra_rows)} calls logged one item that was not a message or reasoning, "
                            f"so a tool may have run. {sum(r['passed'] for r in logged)} of those {len(logged)} passed. The raw item type was not kept." if logged else "")
    # Held-out router: per problem, the cheapest config that passed tries 1-3; scored on tries 4-5.
    ladder = [r for r in rows if r["config"] in every and r["phase"] in ("main", "exploratory", "fastmode") and r["repeat"] <= REPEATS and r["rung"] <= 6]
    cell = defaultdict(list)
    for r in ladder: cell[(r["config"], r["problem"])].append(r)
    full = {c for c in {c for c, _ in cell} if sum(len(v) for (cc, _), v in cell.items() if cc == c) == REPORT_PROBLEMS * REPEATS}
    FIT = 3; F["router_fit"] = f"1–{FIT}"; F["router_held"] = f"{FIT + 1}–{REPEATS}"
    k = tot = spent = 0
    for p in sorted({p for _, p in cell}):
        sure = [(statistics.mean(_usd(r, "main") for r in cell[(c, p)] if r["repeat"] <= FIT), c) for c in full
                if all(r["passed"] for r in cell[(c, p)] if r["repeat"] <= FIT)]
        test = [r for r in cell[(min(sure)[1], p)] if r["repeat"] > FIT]
        k += sum(r["passed"] for r in test); tot += len(test); spent += sum(_usd(r, "main") for r in test)
    hh = [r for (c, _), v in cell.items() if c == "haiku-high" for r in v]
    need(all(r["passed"] for r in hh), "haiku-high, the reference, never missed on the main ladder")
    need(tot == REPORT_PROBLEMS * (REPEATS - FIT), "the router is scored on every held-out try")
    F["router_k"] = f"{k}/{tot}"; F["router_share"] = f"{round(100 * (spent / k) / (sum(_usd(r, 'main') for r in hh) / len(hh)), -1):.0f}%"
    # Smallest paired gap that separated from zero; every smaller gap did not.
    sep = [d for d in s["paired"] if d["ci95"][0] > 0 or d["ci95"][1] < 0]
    need(sep and all(abs(d["diff"]) < min(abs(x["diff"]) for x in sep) for d in s["paired"] if d not in sep), "paired gaps separate only above a threshold")
    F["sep_gap"] = f"{round(100 * min(abs(d['diff']) for d in sep))}"
    F["nosep_gap"] = f"{round(100 * max(abs(d['diff']) for d in s['paired'] if d not in sep))}"
    F.update(main_set_label=configs.set_label("main ladder"), l7_set_label=configs.set_label("L7 set"))
    F["l7_n"] = str(len({p for v in hard.values() for p in v["by_problem"]}) * int(F["repeats"]))
    F["n_rescue_problems"] = str(len(luna_rescue.PIDS))
    rule = ('luna-low', 'luna-medium', 'luna-low-bare')
    raw = rows
    missed = {r['problem'] for r in raw if r["config"] in rule and r['problem'] in s['problems'] and not r['passed']}
    need(missed == set(luna_rescue.PIDS), "the rescue set is exactly the problems luna-low, luna-medium or luna-low-bare missed")
    F["rescue_rule"] = "luna-low, luna-medium or luna-low-bare missed"
    F["older_generation"] = "5.6"
    F["quality_fast_note"] = quality_fast_note(s)
    F["quality_fast_items"] = "".join(f"<li>{part}</li>" for part in quality_fast_parts(s))
    F["exploratory_items"] = "".join(f"<li>{DISP(c)}</li>" for c in ex)
    F["l7_problem_items"] = "".join(f"<li>{plabel(p)}</li>" for p in sorted({p for v in hard.values() for p in v["by_problem"]}))
    F["p90_percent"] = pct(0.90)
    F["host_agents_md"] = HOST_AGENTS_MD; F["min_pass"] = pct(MIN_PASS)
    F["rung_attempts"] = str(cfg["haiku-low"]["by_rung"]["L1"]["n"])
    sp = s["spend"]
    F["claude_usd"] = usd(sp['claude_measured_usd']); F["codex_usd"] = usd(sp['codex_proxy_usd'])
    # Round the estimated total to the nearest five dollars for the front page.
    F["codex_usd_rounded"] = f"${round(sp['codex_proxy_usd']):.0f}"
    F["agentic_fast_caption"] = ("⚡ configs are included" if any(c.endswith("-fast") for c in ag) else "No ⚡ repo-task data")
    for c, v in every.items():
        k = c.replace("-", "_")
        F[f"{k}_pass"] = pct(v["pass_at_1"]); F[f"{k}_k"] = f"{v['passes']}/{v['n']}"; F[f"{k}_upp"] = usd(v["usd_per_pass"])
        F[f"{k}_med"] = f"{v['latency_s']['median']:.1f}"; F[f"{k}_rsn"] = n(v["tokens_mean"]["reasoning_tok"]); F[f"{k}_rsn10"] = about(v["tokens_mean"]["reasoning_tok"])
        F[f"{k}_in"] = n(v["tokens_mean"]["in_tok"])
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
    F["escalation_problem_items"] = "".join(f"<li>{plabel(p)}</li>" for p in e["problems"])
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
    others = [ag[c]["latency_s"]["median"] for c in ("haiku-low", "sonnet-medium")]
    need(max(others) - min(others) < 2 and ag["luna-low"]["latency_s"]["median"] < min(others),
         "the two Claude medians are close; luna-low is faster")
    F["ag_other_med"] = f"{statistics.mean(others):.0f}"
    need(not any(v["tests_tampered_runs"] for v in ag.values()), "no run edited the original tests")
    # routing rule
    sm = cfg["sonnet-medium"]; smh = hard["sonnet-medium"]
    need(sm["passes"] == sm["n"] and smh["passes"] == smh["n"], "sonnet-medium never failed")
    F["sm_all"] = f"{sm['passes'] + smh['passes']}/{sm['n'] + smh['n']}"; F["sm_vs_hl_x"] = f"{sm['usd_per_pass'] / hl['usd_per_pass']:.0f}×"
    # harness floor
    pr = s["trim"]["pair"]
    F["terra_call"] = usd(pr["terra/noshell"]["usd_per_call"]); F["terra_x"] = f"{pr['terra/noshell']['usd_per_call'] / pr['haiku']['usd_per_call']:.0f}×"
    # L7
    probs = sorted({p for v in hard.values() for p in v["by_problem"]})
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
        F[f"hl_{name}_failures"] = f"{sum(r['outcome'] == 'timeout' for r in rr)} too slow, {sum(r['outcome'] == 'crash' for r in rr)} crash in {len(rr)} tries"
    worst = max(s["failures"], key=lambda p: sum(v["passed"] < v["n"] for v in s["failures"][p]["cells"].values()))
    misses = sum(v["passed"] < v["n"] for v in s["failures"][worst]["cells"].values())
    need(misses > 0 and worst in s["problems"], "the worst failure problem belongs to the main ladder")
    F["worst_failure"] = f"{plabel(worst)} has misses in {misses} of {len(every)} configs"
    F["hl_main_timeouts"] = str(sum(r["outcome"] == "timeout" for r in hl_all if r["phase"] == "main"))
    F["hl_main_misses"] = str(hl["n"] - hl["passes"])
    F["hl_main_crashes"] = str(sum(r["outcome"] == "crash" for r in hl_all if r["phase"] == "main"))
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
    need(F["orchestrator"].startswith("Claude ")
         and any(r.get("harness") == "codex-designed" for r in load(os.path.join(RES, "appendix", "codex_harness.jsonl"))),
         "Claude designed and ran the bench; Codex built its own harness, not the whole experiment")
    F["bench_authorship"] = "Claude designed and ran this bench; Codex built only its own harness."
    hr, lr, hv, sm = a["luna-high-bare+haiku-on-fail"], a["luna-low+haiku-on-fail"], a["luna-high-bare+haiku-review-all"], a["sonnet-medium"]
    need(hv["passes"] == hv["n"] == sm["passes"], "luna-high + Haiku review and sonnet-medium never failed on the rescue set")
    hm = a["haiku-medium"]; need(hm["passes"] == hm["n"] and hm["usd_per_pass"] < hv["usd_per_pass"], "haiku-medium alone: no miss, cheaper than the pipeline")
    F["hm_vs_pipe_x"] = x(hv["usd_per_pass"], hm["usd_per_pass"])
    F["sm_vs_hh_x"] = x(cfg["sonnet-medium"]["usd_per_pass"], ex["haiku-high"]["usd_per_pass"], money=True)
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
    need(int(F["g_lo_fixed"]) > fixed and lr["passes"] - a["luna-low"]["passes"] > hr["passes"] - a["luna-high-bare"]["passes"] > 0,
         "luna-low triggers more sample-test repairs and gains more passes than luna-high-bare")
    # appendix: the pilot (results/2026-10-22-pilot.jsonl) and the trim probe's pair step on three of its problems
    pl = s["pilot"]; prow = load(os.path.join(RES, "2026-10-22-pilot.jsonl"))
    need(all(v["passes"] == v["n"] for v in pl.values()), "every pilot run passed")
    F["pilot_configs"] = str(len(pl)); F["pilot_runs"] = str(sum(v["n"] for v in pl.values())); F["pilot_problems"] = str(len({r["problem"] for r in prow}))
    pf = s["pilot_fast"]; F["fast_mult"] = f'{json.load(open(os.path.join(RES, "prices.json")))["fast_mode_multiplier"]:g}×'
    F["fast_problems"] = str(len({r["problem"] for r in prow if r["config"] == "sol61-low-defa"})); F["fast_rounds"] = str(pf["sol61-low/default"]["n"] // int(F["fast_problems"]))
    assert all(v["passes"] == v["n"] for v in pf.values()), "fast-mode text says every call passed"
    for k, v in pf.items(): F[f"fast_{k.split('-')[0].rstrip('0123456789')}_{'def' if k.endswith('default') else 'fast'}"] = f"{v['median_s']:.1f}"
    F["fast_luna_change"] = (f"stayed at {F['fast_luna_def']} s" if F["fast_luna_def"] == F["fast_luna_fast"]
                             else f"changed from {F['fast_luna_def']} s to {F['fast_luna_fast']} s")
    F["pilot_r2_configs"] = str(sum(1 for v in pl.values() if v["problems"] > 3))
    need(all(v["passes"] == v["n"] for v in pr.values()), "every trim-probe pair config passed")
    F["pair_problems"] = str(len({r["problem"] for r in load(os.path.join(RES, "2026-10-22b-trim.jsonl")) if r["step"] == "pair"}))
    nf = pr["luna/nofeat"]; need(nf["usd_per_call"] > pr["luna/base"]["usd_per_call"], "tool features off costs more per call than stock")
    need(nf["uncached_calls"] > nf["n"] / 2 and pr["luna/base"]["uncached_calls"] == 0, "the costlier level is the one that missed the cache")
    F["nofeat_nocache"] = str(nf["uncached_calls"]); F["nofeat_calls"] = str(nf["n"])
    need(all(cfg[c]["by_rung"]["L1"]["passed"] == cfg[c]["by_rung"]["L1"]["n"] > cfg[c]["by_rung"]["L2"]["passed"] for c in ("luna-low", "luna-medium")), "luna low/medium pass L1 and already fail at L2")
    F["pilot_luna_call"] = usd(pr["luna/noshell"]["usd_per_call"]); F["pilot_haiku_call"] = usd(pr["haiku"]["usd_per_call"])
    F["pilot_luna_k"] = f"{pr['luna/noshell']['passes']}/{pr['luna/noshell']['n']}"
    SLOW_X = 10
    q = [r for r in quality_rows() if r["outcome"] == "pass" and r["phase"] in ("main", "exploratory", "escalation") and r.get("time_ratio") is not None]
    F["q_rows"] = str(len([r for r in quality_rows() if r["outcome"] == "pass" and r["phase"] in ("main", "exploratory", "escalation")]))
    if q:
        w = max(q, key=lambda r: r["time_ratio"])
        F["q_worst_x"] = f"{w['time_ratio']:.0f}×"; F["q_worst_problem"] = plabel(w["problem"]); F["q_worst_cfg"] = DISP(w["config"])
        slow = [r for r in q if r["problem"] == w["problem"] and r["time_ratio"] >= SLOW_X]  # 10x: one config's extreme outlier must not hide the rest
        F["q_slow_bar"] = f"{SLOW_X}×"; F["q_slow_n"] = str(len(slow)); F["q_slow_cfgs"] = str(len({r["config"] for r in slow})); F["q_slow_lo"] = f"{min(r['time_ratio'] for r in slow):.0f}×"
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
        need({r["problem"] for r in rows if r["phase"] == "fastmode"} == set(luna_rescue.PIDS), "the fast-mode runs use the retest problems")
        F["fm_mult"] = f"{json.load(open(os.path.join(RES, 'prices.json')))['fast_mode_multiplier']:g}×"
        qx = {c: [r for r in quality_rows() if r.get("phase") == "fastmode" and r.get("outcome") == "pass" and r["config"] == c] for c in ("sol61-high", "sol61-xhigh")}
        med = lambda c, k: statistics.median(r[k] for r in qx[c])
        need(all(med("sol61-xhigh", k) >= med("sol61-high", k) for k in ("loc", "cc_max", "lint_warnings")), "xhigh code is no better: LOC, complexity and lint no lower than high")
        F["fm_x_cost"] = x(cx["usd_per_pass"], c0["usd_per_pass"], money=True, sig=3); F["fm_x_out"] = f"{cx['out_median'] / c0['out_median']:.1f}×"
        b = json.load(open(BLIND)) if os.path.exists(BLIND) else None
        if b:
            F["bl_n"] = str(len(b["items"])); F["bl_probs"] = str(len({i["problem"] for i in b["items"]})); F["bl_cfgs"] = str(len({i["config"] for i in b["items"]}))
            blk = {i["config"] for i in b["items"] if i["block"]}
            need(blk == {"sonnet-medium"}, "every solution the blind reader would block came from sonnet-medium")
            F["bl_blocks"] = str(sum(i["block"] for i in b["items"]))
            counts = {c: sum(i["config"] == c for i in b["items"]) for c in {i["config"] for i in b["items"]}}
            need(len(set(counts.values())) == 1, "blind read has the same sample size per config")
            sentence_case = lambda t: ". ".join(part[0].upper() + part[1:] for part in t.split("; "))
            method = b['method'].replace("; the reviewer saw code only", "").replace("A-E", "A–E")
            scale = re.sub(r";?\s*block =[^;]*", "", b["scale"]).replace("1-10", "1–10")
            need("block = would not merge as is" in b["scale"], "blind-review blocks mean would not merge as is")
            F["blind_caption"] = (f"Reader: {b['reviewer']}. Method: {sentence_case(method)}. "
                                  f"Score: {sentence_case(scale)}. {next(iter(counts.values()))} solutions per config. "
                                  "Would block = would not merge as is.")
            scores = {c: statistics.mean(i['score'] for i in b['items'] if i['config'] == c) for c in counts}
            others = [v for c, v in scores.items() if c != 'sonnet-medium']
            F['bl_sonnet_score'] = f"{scores['sonnet-medium']:.1f}/{10}"
            F['bl_other_scores'] = f"{min(others):g}–{max(others):g}"
            need(scores['sonnet-medium'] < min(others), 'Sonnet scored lowest in the blind read')
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
    F["codex_new_usd"] = usd(nu); F["codex_old_usd"] = usd(sp['codex_proxy_usd'] - nu - sp['codex_fastmode_usd'] - ffu); F["ff_usd"] = usd(ffu); F["fx_usd"] = usd(sp['codex_fastmode_usd'] + ffu)
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
    # Winner: the Codex pick against the Claude config that matches it (both perfect on L1-L6 and L7)
    for k, c in (("s61h", "sol61-high"), ("s61f", "sol61-high-fast")):
        v = ex[c]; need(v["passes"] == v["n"] and v["latency_s"]["median"] > hx["latency_s"]["median"] and v["usd_per_pass"] > hx["usd_per_pass"], f"{c} matches haiku-high's passes but is slower and dearer")
        F[f"{k}_hh_t"] = f"{v['latency_s']['median'] / hx['latency_s']['median']:.1f}×"; F[f"{k}_hh_c"] = f"{v['usd_per_pass'] / hx['usd_per_pass']:.0f}×"
    # trusted Codex builders: who bills what. Codex calls bill the Codex subscription, so their Claude $ is zero by construction.
    ah, sh = ex["astra-medium"], ex["sol61-high"]
    F["x_astra_vs_s61h"] = x(ah["usd_per_pass"], sh["usd_per_pass"])
    need(ah["latency_s"]["median"] < sh["latency_s"]["median"] and ag["astra-medium"]["latency_s"]["median"] < ag["sol61-high"]["latency_s"]["median"], "astra faster than sol61-high")
    F["ag_n"] = str(ag["sol61-high"]["n"]); F["claude_zero"] = usd(0)
    F["ag_hh_k"] = f"{ag['haiku-high']['hidden_pass']}/{ag['haiku-high']['n']}"
    F["ag_claude_med"] = f"{statistics.mean(ag[c]['latency_s']['median'] for c in ('haiku-low', 'sonnet-medium')):.0f}"
    ga = arms
    for c in ("sol61-high+haiku-on-fail", "astra-medium+haiku-on-fail"):
        g = ga[c]; need(g["passes"] == g["n"] and not any(r["repaired"] for r in g["rows"]), f"{c} never failed and never called Haiku on the rescue set"); F["g_" + c.split("-")[0] + "_repairs"] = str(sum(r["repaired"] for r in g["rows"]))
        F["g_" + c.split("-")[0] + "_cupp"] = usd(g["claude_usd_per_pass"])
    F["x_astra_vs_sm"] = f"{ex['astra-medium']['usd_per_pass'] / sm_all:.0f}×"
    F["x_l56_vs_lh"] = x(ex["luna56-high"]["usd_per_pass"], ex["luna-high"]["usd_per_pass"])
    for k, c in (("hl", "haiku-low"), ("sm", "sonnet-medium")):
        F[f"l7_{k}_k"] = f"{hard[c]['passes']}/{hard[c]['n']}"
    F["ci_level"] = "95%"
    F["r_luna_high_bare_miss"] = str(a["luna-high-bare"]["n"] - a["luna-high-bare"]["passes"])
    F["n_exploratory"] = str(len(ex))
    expected = lambda rung: "Easy" if rung == 1 else "Medium" if rung <= 3 else "Hard"
    disagree = [p for p, v in s["problems"].items() if configs.LC[p] != expected(v["rung"])]
    need(disagree, "some LeetCode badges disagree with rung order")
    F["badge_disagreement_items"] = "".join(f"<li>{plabel(p, s['problems'][p]['rung'])} is {configs.LC[p]}.</li>" for p in disagree)
    low, medium = every['luna-low'], every['luna-medium']
    need(medium['usd_per_pass'] <= low['usd_per_pass'] and medium['passes'] > low['passes'],
         "luna-medium dominates luna-low")
    need(usd(medium['usd_per_pass'], sig=1) == usd(low['usd_per_pass'], sig=1), "luna prices round identically")
    F['frontier_caption'] = (
        f"luna-low is not a best trade-off: luna-medium costs the same, {usd(medium['usd_per_pass'], sig=1)} per pass. "
        f"It passes {medium['passes']}/{medium['n']} to luna-low's {low['passes']}/{low['n']}. "
        f"{configs.set_label('main ladder', capital=True)} only; every point counts.")
    if s.get("grok"):
        shown = [c for c in s["grok"] if c not in configs.CHART_HIDDEN]
        covered = sorted({p for c in shown for p in s["grok"][c].get("by_problem", {})})
        hidden = [c for c in s["grok"] if c in configs.CHART_HIDDEN]
        if covered:
            span = f"all {len(covered)} problems" if len(covered) == len(s["problems"]) else f"{len(covered)} of {len(s['problems'])} problems"
            part = ""
            if hidden:
                own = sorted({p for c in hidden for p in s["grok"][c]["by_problem"]})
                part = f" {', '.join(hidden)} ({own[0][:3]}–{own[-1][:3]} only) is not plotted."
            F["grok_chart_note"] = f"Grok: black hexagons, {span}, outside the best-trade-off line.{part}"
            F["frontier_caption"] += " " + F["grok_chart_note"]
    F['winner_caption'] = (
        f"Numbers: the {nprob}-problem {configs.set_label('main ladder')}, {hl['n']} tries per config. "
        "Time = median seconds. ~ = estimated from tokens; Claude costs are measured.")
    F['winner_other_routes'] = [
        f"⚡ = fast mode: same answers, about {F['fm_mult']} list price, faster.",
]
    gap = every['haiku-high']['latency_s']['median'] - cfg['sonnet-medium']['latency_s']['median']
    need(gap > 0, "sonnet-medium is faster than the budget pick haiku-high")
    F['speed_why'] = f"No misses. {gap:.1f} s faster than haiku-high."
    tied = ('sol61-high', 'astra-medium', 'haiku-high', 'sonnet-medium')
    perfect = {c for c in every if every[c]['passes'] == every[c]['n'] and c in hard and hard[c]['passes'] == hard[c]['n']
               and c in ag and ag[c]['hidden_pass'] == ag[c]['n']}
    need(perfect == set(tied), "exactly these configs pass every main, L7 and repo try")
    need(all(every[c]['passes'] == every[c]['n'] and hard[c]['passes'] == hard[c]['n'] for c in ('sol61-high-fast', 'astra-medium-fast')),
         "both ⚡ variants pass every main and L7 try")
    need(every['haiku-high']['usd_per_pass'] < min(every[c]['usd_per_pass'] for c in tied + ('sol61-high-fast', 'astra-medium-fast') if c != 'haiku-high'),
         "haiku-high is the cheapest of these")
    word = {3: "Three", 4: "Four", 5: "Five"}[len(tied)]
    F['winner_line'] = (f"{word} configs passed every try in every set: haiku-high, sonnet-medium, sol61-high and astra-medium. "
                        f"haiku-high is the cheapest, at {F['hh_upp']} per pass.")
    F['winner_intro'], F['winner_price'] = F['winner_line'].split('. ', 1)
    F['winner_intro'] += '.'
    F['winner_default'] = f"Default delegate on Codex quota: {DISP('sol61-high-fast')}."
    F['winner_budget'] = f"Cheapest without misses: {DISP('haiku-high')}."
    F['winner_speed'] = f"For speed, pick {DISP('sonnet-medium')}."
    nl7 = hard['sonnet-medium']['n']
    need(all(v['passes'] == v['n'] == nl7 for c, v in hard.items() if c in tied), "every tied config is perfect on the same number of L7 tries")
    F['l7_bound'] = f"{nl7}/{nl7}"; F['l7_lo'] = ci_text(nl7, nl7, None, len(probs)).split()[0].lstrip("≥")  # same bound as the tables: over problems, not tries
    need(all(v['hidden_pass'] == v['n'] for v in ag.values()), "every repo-task run passed, so repo tasks only rank cost and speed")
    F['budget_why'] = f"Cheapest with no misses. haiku-low costs less but misses {hl['n'] - hl['passes']} of {hl['n']}"
    F['model_names'] += (f". luna56 = {ex['luna56-high']['model']}, "
                         f"sol56 = {ex['sol56-high']['model']} (older generation)")
    need(a['luna-low-noshell-B1']['passes'] > a['luna-low']['passes'] > a['luna-low-noshell-B2']['passes'], "B1 improves over plain luna-low; B2 passes less often")
    F['noshell_comparison'] = (f"On the {configs.set_label('rescue set')}, B1 passed {a['luna-low-noshell-B1']['passes']}/{a['luna-low']['n']}. "
                               f"Plain luna-low passed {a['luna-low']['passes']}; B2 passed {a['luna-low-noshell-B2']['passes']}.")
    F['verdict_key'] = (
        "✓ pick = a Winner pick. 0 misses / missed N = raw miss count, no ranking. "
        "beaten = another row is as cheap and passes as often. "
        f"trade-off = pricier but passes more. avoid = below {F['min_pass'] }.")
    F['dropped_pipeline_models'] = " and ".join(dict.fromkeys(
        DISP(c.split('+')[0].removesuffix('-fast')) for c in configs.PLAIN_PIPELINE_DUPLICATES)) + " (normal and ⚡)"
    F['l7_config_count'] = str(len(hard))
    absent = [DISP(c) for c in every if c not in hard]
    F['l7_absent'] = ", ".join(absent[:-1]) + " and " + absent[-1] if len(absent) > 1 else "".join(absent)
    rung_configs = list(cfg) + [c for c in ("sol61-high", "sol61-high-fast", "astra-medium", "astra-medium-fast") if c in ex]
    at = {}
    for c in rung_configs:
        if every[c]['breaking_point']: at.setdefault(every[c]['breaking_point'], []).append(DISP(c))
    F['rung_breaks'] = "; ".join(f"{' and '.join(cs)} break{'s' if len(cs) == 1 else ''} at {b}" for b, cs in at.items())
    F['bare_rung_break'] = lb['breaking_point']
    F['rung_caption'] = (f"Passes per rung. Tint = a miss; red = {F['break_at']} or less, the breaking point. "
                         f"{configs.set_label('L7 set').split()[0]} excluded.")
    F['pipes_caption'] = (f"Bar length = passes out of {F['rescue_n']}. "
                          "Text by each bar = passes · $ per pass · median seconds.")
    sf, hf = every['sol61-high-fast'], hard['sol61-high-fast']
    need(sf['passes'] == sf['n'] and hf['passes'] == hf['n'], "sol61-high ⚡ passes every main and L7 try")
    F['default_route_scope'] = (f"Tested with plain sol61-high: {F['r_sol61_high_haiku_on_fail_k']} on the "
                                f"{configs.set_label('rescue set')}. Haiku never ran.")
    gain = {m: int(F[f'hb_codex_{m}'].split('/')[0]) - int(F[f'hb_claude_{m}'].split('/')[0]) for m in ('luna_low', 'haiku_low')}
    need(gain['luna_low'] > gain['haiku_low'] > 0, "Codex CLI lifted luna-low more than Claude Code lifted haiku-low")
    F['hb_conclusion_copy'] = (f"Codex CLI lifted luna-low by {gain['luna_low']} passes. haiku-low gained {gain['haiku_low']}, near its ceiling. "
                               "No pick changes.")
    F['l7_set_description'] = (f"{configs.set_label('L7 set')}: " + ", ".join(plabel(p) for p in probs)
                               + f"; scored separately. Added after every strong config passed L{max(v['rung'] for v in s['problems'].values())}.")
    return F


def md_table(head, rows, bold=None):
    """Persist table cells, including derived numbers, before rendering."""
    return {"head": head, "rows": rows}


def _tables(s, arms):
    T = {}; cfg, ex = s["configs"], s["exploratory"]; nprob = len(s["problems"])
    if s.get("grok"):
        T["grok"] = md_table(["config", "coverage", "passed", "$ per pass", "total $ (CLI-measured)", "median s"],
            [[DISP(c), f'{len(v["by_problem"])} of {nprob} problems', f'{pct(v["pass_at_1"])} ({v["passes"]}/{v["n"]})',
              usd(v["usd_per_pass"]), usd(v["usd_total"]), f'{v["latency_s"]["median"]:.1f}'] for c, v in s["grok"].items()])
    T["result"] = md_table(["config", "pass rate", "95% CI", "median s", "slow-call time s", "$ per pass", f"total $ ({cfg['haiku-low']['n']} calls)", "$ kind"],
                           [[DISP(c) + (" †" if c in ex else ""), f"{pct(v['pass_at_1'])} ({v['passes']}/{v['n']})", ci_text(v["passes"], v["n"], v["ci95"], nprob),
                             f"{v['latency_s']['median']:.1f}", f"{v['latency_s']['p90']:.1f}", f"{usd(v['usd_per_pass'])}", f"{usd(v['usd_total'])}", v["cost_kind"]]
                            for c, v in {**cfg, **ex}.items()])
    T["result_detail"] = md_table(["config", "pass rate 95% CI", "slow-call time s", f"total $ ({cfg['haiku-low']['n']} calls)"],
                                  [[DISP(c) + (" †" if c in ex else ""), ci_text(v["passes"], v["n"], v["ci95"], nprob),
                                    f"{v['latency_s']['p90']:.1f}", ("~" if v["cost_kind"] == "proxy" else "") + usd(v["usd_total"])]
                                   for c, v in sorted({**cfg, **ex}.items(), key=lambda pair: configs.low_context(pair[0]))])
    T["tokens"] = md_table(["config", "mean input", "of which cached", "mean output", "of which reasoning", "$ per 1k tokens"],
                           [[DISP(c) + (" †" if c in ex else "")] + (["–"] * 5 if v["cost_kind"] == "unmetered" else [n(v["tokens_mean"]["in_tok"]), n(v["tokens_mean"]["cached_tok"]), n(v["tokens_mean"]["out_tok"]),
                             n(v["tokens_mean"]["reasoning_tok"]), usd(v["usd_per_1k_tokens"])])
                            for c, v in {**cfg, **ex}.items()])
    from bench.trim_probe import LEVELS
    fl = s["trim"]["floor"]; names = {"base": "stock harness", "nodoc": "+ no project docs", "noctx": "+ no env/permission context", "nofeat": "+ tool features off",
                                       "mininst": "+ one-line system prompt", "noshell": "+ shell tools off"}
    lv = [l for l in LEVELS if any(k.endswith("/" + l) for k in fl)]
    T["floor"] = md_table(["model"] + [names[l] for l in lv],
                          [[{"luna": "gpt-6-luna", "terra": "gpt-5.6-terra"}[m]] + [n(fl[f"{m}/{l}"]["in_tok"]) for l in lv] for m in dict.fromkeys(k.split("/")[0] for k in fl)])
    hard = s["hard"]; hp = sorted({p for v in hard.values() for p in v["by_problem"]})
    T["l7"] = md_table(["config", "passed", "95% CI"] + [plabel(p) for p in hp] + ["median s", "mean reasoning tokens", "$ per pass", "$ kind"],
                       [[c, f"{v['passes']}/{v['n']}", ci_text(v["passes"], v["n"], v["ci95"], len(hp))] + [f"{v['by_problem'].get(p, 0)}/5" for p in hp]
                        + [f"{v['latency_s']['median']:.1f}", n(v["tokens_mean"]["reasoning_tok"]), f"{usd(v['usd_per_pass'])}", v["cost_kind"]] for c, v in hard.items()])
    fail = s["failures"]; cols = list(dict.fromkeys(c for f in fail.values() for c in f["cells"]))
    ab = {"wrong": "w", "crash": "c", "timeout": "t", "no_code": "n"}

    def cell(d):
        if not d: return "–"
        f = " ".join(f"{k}{ab[o]}" for o, k in sorted(d["fails"].items()))
        k = f"**{d['passed']}**" if d["passed"] * 5 <= 2 * d["n"] else str(d["passed"])
        return k + (f" ({f})" if f else "")
    T["fail"] = md_table(["problem"] + cols, [[plabel(p, f["rung"])] + [cell(f["cells"].get(c)) for c in cols] for p, f in fail.items()])
    ag = s["agentic"]; selected_keys = {r["key"] for r in summarize.agentic_rows()}
    at = [r for r in json.load(open(os.path.join(RES, "agentic_tests.json"))) if r["key"] in selected_keys]
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


def method_appendix(ds):
    """Pooled harness outcomes and failure counts, with their scopes stated on the page."""
    identity = lambda r: tuple(r[k] for k in ("config", "phase", "problem", "repeat"))
    comparison = []
    for track, original in (("function", load(FUNC)), ("harness_bias", _harness_rows())):
        old = {identity(r): r for r in original}
        clean = load(os.path.join(RES, "appendix", "isolation", f"{track}.jsonl"))
        need(len({identity(r) for r in clean}) == len(clean), f"unique clean {track} calls")
        need(all(identity(r) in old for r in clean), f"clean {track} calls match original rows")
        comparison.extend((r, old[identity(r)]) for r in clean)
    isolation = {"calls_matched": len(comparison),
                 "passes_isolated": sum(r["passed"] for r, _ in comparison),
                 "passes_original": sum(r["passed"] for _, r in comparison)}
    for key, expected in (("calls_matched", 995), ("passes_isolated", 889), ("passes_original", 890)):
        need(isolation[key] == expected, f"computed isolation comparison {key} is {expected}")
        ds["facts"]["isolation_" + key] = str(isolation[key])
    # The paired run only (60 tries per cell), so both benches compare like for like.
    rows = _harness_rows()
    bench = {'claude-one-shot': "Claude's bench", 'codex-tool-loop': "Codex's bench"}
    cell, cells = {}, []
    for c in harness_bias.CFGS:
        for h, name in bench.items():
            rs = [r for r in rows if (r['harness'], r['config']) == (h, c)]
            cli = '' if h == 'claude-one-shot' else (' (Claude Code)' if c.startswith('haiku') else ' (Codex CLI)')
            passes = sum(r['passed'] for r in rs)
            need(passes > 0, f"{c} has passes on {h} for per-pass measures")
            cell[c, h] = dict(usd=sum(r['cost_usd'] for r in rs), seconds=sum(r['wall_s'] for r in rs), passes=passes)
            cell[c, h].update(upp=cell[c, h]['usd'] / passes, tpp=cell[c, h]['seconds'] / passes)
            cells.append([c, name + cli, f"{passes}/{len(rs)}",
                          ('~' if c.startswith('luna') else '') + usd(cell[c, h]['upp']),
                          f"{cell[c, h]['tpp']:.1f}"])
    ds['tables']['harness_strengths'] = md_table(['model', 'bench', 'passed', '$ per pass', 'time per pass (s)'], cells)
    one, loop = cell['luna-low', 'claude-one-shot'], cell['luna-low', 'codex-tool-loop']
    need(loop['upp'] > 2 * one['upp'] and loop['tpp'] > 2 * one['tpp'], "Codex's bench costs luna-low over 2x in $ and time per pass")
    # Codex's first step: replay a subset of our main-run cells before the paired run.
    sub = [r for r in load(os.path.join(RES, "appendix", "codex_harness.jsonl")) if r['repeat'] <= 2]
    ours = {(r['config'], r['problem'], r['repeat']): r['passed'] for r in summarize.function_rows() if r['phase'] == 'main'}
    need(sub and all(r['passed'] and ours[r['config'], r['problem'], r['repeat']] for r in sub),
         "every subset cell passed on both benches")
    ds['facts']['hb_subset'] = f"It first replayed {len(sub)} of our {' and '.join(sorted({r['config'] for r in sub}))} results. All passed on both."
    hh1, hh2 = cell['haiku-low', 'claude-one-shot'], cell['haiku-low', 'codex-tool-loop']
    need(0.8 < hh2['tpp'] / hh1['tpp'] < 1.25 and hh2['upp'] / hh1['upp'] < 1.5,
         "Codex's bench barely moved haiku-low's time and cost per pass")
    ds['facts']['hb_haiku_cost'] = (f"haiku-low cost {hh2['upp'] / hh1['upp']:.1f}× as much per pass. "
                                     f"Time per pass was {hh2['tpp'] / hh1['tpp']:.1f}× as long.")
    tot = lambda h: sum(cell[c, h]['usd'] for c in harness_bias.CFGS) / sum(cell[c, h]['passes'] for c in harness_bias.CFGS)
    ds['facts']['hb_total_x'] = f"{tot('codex-tool-loop') / tot('claude-one-shot'):.1f}×"
    ds['facts']['hb_luna_cost'] = (f"luna-low cost {loop['upp'] / one['upp']:.1f}× as much per pass. "
                                    f"Time per pass was {loop['tpp'] / one['tpp']:.1f}× as long.")
    s = ds['report']
    counts = []
    for key, label in (('configs', 'main ladder'), ('hard', 'L7 set')):
        v = s[key]['haiku-low']
        counts.append([configs.set_label(label), v['n'], v['outcomes'].get('timeout', 0),
                       v['outcomes'].get('crash', 0), v['outcomes'].get('wrong', 0)])
    ds['tables']['haiku_failures'] = md_table(['set', 'tries', 'too slow', 'crashes', 'wrong outputs'], counts)


def quality_rows():
    selected = {r["key"] for r in summarize.function_rows()}
    return [r for l in open(QUALITY) if (r := json.loads(l))["key"] in selected] if os.path.exists(QUALITY) else []


def quality_fast_parts(s):
    """Keep main-ladder and separate subset scores apart."""
    q = [r for r in quality_rows() if r.get("outcome") == "pass"]
    names = ("sol61-high-fast", "astra-medium-fast")
    main = {c: sum(r["config"] == c and r["phase"] in ("main", "exploratory", "escalation") for r in q) for c in names}
    subset = {c: sum(r["config"] == c and r["phase"] == "fastmode" for r in q) for c in names}
    first = (f"{DISP(names[0])} and {DISP(names[1])}: main-ladder solutions not scored."
             if not any(main.values()) else " ".join(f"{DISP(c)}: {main[c]} main-ladder solutions scored." for c in names))
    short = configs.set_label('rescue set').removesuffix(' set')
    second = " ".join(f"{DISP(c)}'s {subset[c]}-attempt {short} run is scored below;" if subset[c]
                      else f"{DISP(c)} has no {short} scores." for c in names)
    return [first, second]


def quality_fast_note(s):
    return " ".join(quality_fast_parts(s))


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
        out.append([FM_LABEL[c].format(lo=min(v["repeats"]), hi=max(v["repeats"])), f"{v['passes']}/{v['n']}", f"{v['median_s']:.1f}", n(v["out_median"]), f"{usd(v['usd_per_pass'], sig=3)}",
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
                                ("hard", "main", "L7 set"), ("agentic", "agentic", "repo tasks"), ("grok", "main", "partial ladder")):
        for c, v in summary.get(block, {}).items():
            r = get(ds, c, "partial ladder" if block == "exploratory" and c in configs.ONE_REPEAT + configs.DEVIN_CONFIGS else set_, source)
            r.update({k: v[k] for k in ("cli", "model", "effort", "outcomes", "breaking_point") if k in v})
            v.update({"n": r["n"], "passes": r["passes"], "pass_at_1": r["pass_rate"], "misses": r["misses"],
                      "ci95": r["ci95"] or [r["pass_rate"], r["pass_rate"]], "ci95_plot": r["ci95_plot"],
                      "usd_per_pass": r["usd_per_pass"], "usd_text": usd(r["usd_per_pass"]), "usd_per_call": r["usd_per_call"], "usd_total": None if r["cost_kind"] == "unmetered" else r["spend"],
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


def joined_names(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def _equivalents(ds):
    """Codex vs Claude: for each Claude config, the cheapest Codex config on the main ladder that passes at least as often."""
    rows = [r for r in ds["rows"] if r["source"] == "main" and r["set"] == "main ladder" and r["usd_per_pass"]]
    claude = sorted((r for r in rows if r["family"] == "Claude"), key=lambda r: (r["pass_rate"], r["usd_per_pass"]))
    codex = [r for r in rows if r["family"] == "Codex"]
    pct = lambda r: f'{r["pass_rate"]:.0%}'
    out, pairs = [], []
    for r in claude:
        m = min((q for q in codex if q["pass_rate"] >= r["pass_rate"]), key=lambda q: q["usd_per_pass"])
        pairs.append((r, m))
        # one column per measure, "Claude → Codex", so both sides stay visible on a narrow screen
        out.append([f'{r["display"]} → {m["display"]}', f'{pct(r)} → {pct(m)}', f'{usd(r["usd_per_pass"])} → ~{usd(m["usd_per_pass"])}',
                    f'{r["median_s"]:.0f} → {m["median_s"]:.0f}'])
    ds["tables"]["equiv"] = md_table(["Claude → Codex match", "passed", "$ per pass", "median s"], out)
    undercut = [(r, m) for r, m in pairs if m["usd_per_pass"] <= r["usd_per_pass"]]
    need(undercut and len(undercut) < len(pairs), "some, not all, cheapest Codex matches cost less per pass at list price")
    slower = [(r, m) for r, m in pairs if m["median_s"] > r["median_s"]]
    need(slower and len(slower) < len(pairs), "some, not all, cheapest Codex matches are slower")
    top = [r for r in claude if r["pass_rate"] == 1]
    tops = {m["config"] for r, m in pairs if r["pass_rate"] == 1}
    need(len(tops) == 1 and top, "the 100% Claude configs share one cheapest Codex match")
    tm = next(m for r, m in pairs if r["pass_rate"] == 1)
    F = ds["facts"]
    fast = min((q for q in codex if q["pass_rate"] == 1), key=lambda q: q["median_s"])
    need(fast["usd_per_pass"] > tm["usd_per_pass"], "the fastest 100% Codex config costs more than the cheapest")
    F["equiv_fastest"] = f'Fastest Codex at 100%: {fast["display"]}, {fast["median_s"]:.0f} s. It costs {usd(fast["usd_per_pass"])} per pass.'
    lo = claude[0]  # best Codex config at no more than 1.5x the weakest Claude config's price
    near = max((q for q in codex if q["usd_per_pass"] <= 1.5 * lo["usd_per_pass"]), key=lambda q: q["pass_rate"])
    need(near["pass_rate"] < lo["pass_rate"], f"{near['config']} passes less often than {lo['config']}")
    F["equiv_near"] = f'At {lo["display"]}\'s price, the best Codex is {near["display"]}: {pct(near)} to {pct(lo)}.'
    # The other way: every Codex config, matched to the cheapest Claude config that passes at least as often.
    back = []
    for q in sorted(codex, key=lambda q: (q["pass_rate"], q["usd_per_pass"])):
        m = min((r for r in claude if r["pass_rate"] >= q["pass_rate"]), key=lambda r: r["usd_per_pass"])
        back.append((q, m))
    ds["tables"]["equiv_back"] = md_table(["Codex → Claude match", "passed", "$ per pass", "median s"],
        [[f'{q["display"]} → {m["display"]}', f'{pct(q)} → {pct(m)}', f'~{usd(q["usd_per_pass"])} → {usd(m["usd_per_pass"])}',
          f'{q["median_s"]:.0f} → {m["median_s"]:.0f}'] for q, m in back])
    ds["tables"]["equiv_all"] = md_table(["Config → cheapest match", "passed", "$ per pass", "median s"],
                                         ds["tables"]["equiv_back"]["rows"] + out)
    forward = {r['config']: m for r, m in pairs}
    reverse = {q['config']: m for q, m in back}
    need({c: m['config'] for c, m in forward.items()} == {
        'haiku-low': 'terra61-high', 'haiku-medium': 'terra61-low',
        'haiku-high': 'terra61-low', 'sonnet-medium': 'terra61-low'},
         "Winner Claude-to-Codex summary covers every cheapest main-ladder pass-rate match")
    need(reverse['sol61-medium']['config'] == 'haiku-medium' and reverse['sol61-high']['config'] == 'haiku-high'
         and reverse['terra61-low']['config'] == 'haiku-high' and reverse['terra61-high']['config'] == 'haiku-medium',
         "Winner Codex-to-Claude summary uses the cheapest main-ladder pass-rate matches")
    groups = {}
    for r, m in pairs:
        groups.setdefault(m["display"], []).append(r["display"])
    F['winner_claude_to_codex'] = (
        "Cheapest main-ladder pass-rate matches, Claude → Codex: "
        + ". ".join(f"{joined_names(names)} → {match}" for match, names in groups.items()) + ".")
    F['winner_codex_to_claude'] = (
        "Cheapest main-ladder pass-rate matches, Codex → Claude: "
        + "; ".join(f"{DISP(c)} → {reverse[c]['display']}" for c in ('terra61-low', 'terra61-high', 'sol61-medium', 'sol61-high')) + ".")
    cheaper = [q for q, m in back if m["usd_per_pass"] < q["usd_per_pass"]]
    dearer = [q for q, m in back if m["usd_per_pass"] >= q["usd_per_pass"]]
    need(dearer and all(q["display"].startswith("luna-") for q in dearer), "only luna configs undercut their Claude match on price")
    need(all(q["usd_per_pass"] < m["usd_per_pass"] for q, m in back if q in dearer),
         "every luna price exception strictly undercuts its Claude match")
    need(all(m["pass_rate"] > q["pass_rate"] for q, m in back if q in dearer), "and each of those passes less often than its match")
    need(len(pairs) == len(claude) and len(back) == len(codex), "the merged match table covers both vendors in both directions")
    need(cheaper and len(cheaper) + len(dearer) == len(back), "every reverse match has a pinned price comparison")
    F["equiv_takeaway"] = (
        f'All {len(pairs)} Claude configs have Codex matches. {len(pairs) - len(undercut)} of {len(pairs)} cost more at list price; '
        + joined_names([f'{m["display"]} costs less than {r["display"]}' for r, m in undercut]) + ". "
        f'{len(slower)} of {len(pairs)} also run slower. '
        + " ".join(f'{m["display"]} runs faster than {joined_names(ns)}.' for m, ns in
                   ((m, [r["display"] for r2, m2 in pairs if m2 is m and m2["median_s"] <= r2["median_s"] for r in [r2]])
                    for m in {id(m): m for _, m in pairs}.values()) if ns) + " "
        f'All {len(back)} Codex configs have Claude matches. Claude is cheaper for {len(cheaper)}. '
        'Only luna undercuts its Claude match, with more misses.')
    F["equiv_back_takeaway"] = (f'Every Codex config has a Claude match. It is cheaper for {len(cheaper)} of {len(back)}. '
                                'Only luna (not luna56) costs less, and it misses more.')



def _interesting(ds):
    """Findings the operator flagged as worth sharing. Each line is computed and pinned."""
    F, ml = ds["facts"], "main ladder"
    hl, hh = (get(ds, c, ml) for c in ("haiku-low", "haiku-high"))
    need(hl["passes"] < hl["n"] == hh["n"] == hh["passes"] and hl["usd_per_pass"] < hh["usd_per_pass"],
         "haiku-high avoids cheaper haiku-low's main-ladder misses")
    F["winner_fallback"] = (f'Codex out? Use haiku-high: {hh["passes"]}/{hh["n"]} passed on the main ladder. '
                            f'It costs {usd(hh["usd_per_pass"])} per pass, cheapest among configs with no misses.')
    checks = ds["derived_pipelines"]
    need(all(checks[c]["all"]["n"] > 0 and checks[c]["all"]["failures"] == 0
             and checks[c]["rescue"]["pipeline"] is not None
             for c in ("sol61-high-fast", "astra-medium-fast")),
         "fast-mode pipelines equal their builders because every cached example check passed")
    repairs = sum(checks[c]["all"]["failures"] for c in ("sol61-high-fast", "astra-medium-fast"))
    need(repairs == 0, "Haiku made zero repairs in the derived fast-mode arms")
    F["fast_pipeline_note"] = ("Fast-mode pipelines equal their builders because every example check passed. "
                               f"Haiku made {repairs} repairs.")
    for c in ("sol61-high", "astra-medium"):
        pipe, plain = get(ds, c + "+haiku-on-fail", "rescue arms", "rescue"), get(ds, c, "rescue set")
        need(pipe["spend_claude"] == 0 and pipe["passes"] == plain["passes"], f"{c} →H fail: Haiku never ran and passes match the plain row")
    fast, old, new = (get(ds, c, ml) for c in ("sol61-high-fast", "sol56-high", "sol61-high"))
    need(fast["pass_rate"] == old["pass_rate"] == new["pass_rate"] == 1, "sol61-high, its ⚡ run and sol56-high all pass every main try")
    need(old["median_s"] < fast["median_s"] < new["median_s"], "older sol56-high beats sol61-high ⚡ on speed, which beats plain sol61-high")
    need(old["usd_per_pass"] < 1.25 * fast["usd_per_pass"], "sol56-high costs under 25% more than sol61-high ⚡")
    need(new["usd_per_pass"] < fast["usd_per_pass"] < old["usd_per_pass"], "plain sol61-high is the cheapest of the three, sol56-high the dearest")
    F["int_sol"] = " ".join([
        f'sol56-high is a generation older than sol61-high. Both pass every main-ladder try.',
        f'sol56-high takes {old["median_s"]:.1f} s at ~{usd(old["usd_per_pass"])} per pass.',
        f'sol61-high takes {new["median_s"]:.1f} s at ~{usd(new["usd_per_pass"])}. ⚡ cuts that to {fast["median_s"]:.1f} s, at ~{usd(fast["usd_per_pass"])}.',
        'So the newer model is cheaper but slower. ⚡ does not close the gap.'])
    # Terra (2026-10-28, operator question). Fast mode is tried only if the pre-registered trigger fires (PLAN.md, deviation 23).
    tl, th, s56 = (get(ds, c, ml) for c in ("terra61-low", "terra61-high", "sol56-high"))
    gap = 100 * (tl["pass_rate"] - th["pass_rate"]); ratio = th["median_s"] / s56["median_s"]
    fired = abs(gap) >= TERRA_TRIGGER["gap_points"] or not TERRA_TRIGGER["ratio"][0] <= ratio <= TERRA_TRIGGER["ratio"][1]
    need(not fired and th["median_s"] < s56["median_s"] and th["pass_rate"] < s56["pass_rate"] == 1 and tl["pass_rate"] == 1 and tl["median_s"] < s56["median_s"],
         "terra61-high is faster than sol56-high but misses; terra61-low matches its pass rate and is faster; the fast-mode trigger did not fire")
    misses = sorted((r["problem"], r["repeat"]) for r in summarize.function_rows() if r["config"] == "terra61-high" and not r["passed"])
    miss_problems = sorted({p for p, _ in misses}); mplabel = ", ".join(pshort(p) for p in miss_problems)
    t56 = {c: get(ds, c, "partial ladder") for c in configs.ONE_REPEAT}
    F["int_terra"] = " ".join([
        "Sol 6.1 high on fast was slower than Sol 5.6 high — does Terra high match or beat Sol 5.6 high on speed and pass rate?",
        f'It is faster but misses. terra61-high takes {th["median_s"]:.1f} s to sol56-high\'s {s56["median_s"]:.1f} s, '
        f'and passes {th["passes"]}/{th["n"]} to {s56["passes"]}/{s56["n"]}. '
        f'The {th["n"] - th["passes"]} misses are on {mplabel} (repeats {", ".join(str(r) for _, r in misses)}).',
        f'terra61-low matches sol56-high at {tl["passes"]}/{tl["n"]} and is faster, {tl["median_s"]:.1f} s.',
        f'Cost per pass, list-price estimates: terra61-low ~{usd(tl["usd_per_pass"])}, terra61-high ~{usd(th["usd_per_pass"])}, '
        f'sol56-high ~{usd(s56["usd_per_pass"])}.',
        f'Fast mode was not tried. The trigger was a low/high gap of {TERRA_TRIGGER["gap_points"]} points or more, '
        f'or terra high outside {TERRA_TRIGGER["ratio"][0]:g}–{TERRA_TRIGGER["ratio"][1]:g}× of sol56-high\'s median. '
        f'The gap is {gap:.1f} points and the ratio is {ratio:.2f}×, so it did not fire.',
        f'Extra data, one repeat each: gpt-5.6-terra passed {t56["terra56-high"]["passes"]}/{t56["terra56-high"]["n"]} at high '
        f'and {t56["terra56-low"]["passes"]}/{t56["terra56-low"]["n"]} at low.'])
    lo, hl = get(ds, "luna-low", ml), get(ds, "haiku-low", ml)
    need(lo["usd_per_pass"] < hl["usd_per_pass"] and lo["pass_rate"] < hl["pass_rate"], "luna-low is cheaper per pass than haiku-low but passes less")
    F["int_luna"] = (f'luna-low is cheaper per pass than haiku-low: ~{usd(lo["usd_per_pass"])} to {usd(hl["usd_per_pass"])}. '
                     f'But it passes {lo["pass_rate"]:.0%} to {hl["pass_rate"]:.0%}.')
    hh, sh = (get(ds, c, ml) for c in ("haiku-high", "sol61-high"))
    need(hh["pass_rate"] == sh["pass_rate"] == 1, "haiku-high and sol61-high pass every main-ladder try")
    need(0 < hh["usd_per_pass"] < sh["usd_per_pass"], "haiku-high costs less per pass than sol61-high on the main ladder")
    semi_repo = {c: get(ds, c, "repo tasks", "agentic") for c in
                 ("luna-low", "haiku-low", "haiku-high", "sonnet-medium", "sol61-medium", "sol61-high", "astra-medium")}
    need(all(semi_repo[c]["passes"] == semi_repo[c]["n"] for c in ("haiku-high", "sol61-high", "luna-low")),
         "haiku-high, sol61-high and luna-low pass every repo task")
    rh, rs, rl = (semi_repo[c] for c in ("haiku-high", "sol61-high", "luna-low"))
    need(0 < rh["usd_per_pass"] < rs["usd_per_pass"], "haiku-high costs less per pass than sol61-high on repo tasks")
    need(all(rl["usd_per_pass"] < r["usd_per_pass"] for c, r in semi_repo.items() if c != "luna-low"),
         "luna-low is the cheapest per pass among all repo-task configs")
    main_gap, repo_gap = round(sh["usd_per_pass"] / hh["usd_per_pass"]), round(rs["usd_per_pass"] / rh["usd_per_pass"])
    F["int_semi"] = (f'<a href="{SEMI_URL}">SemiAnalysis</a>: Anthropic plans give ~5× OpenAI\'s API-priced value at the Opus/Sol tier. '
                     'We price list-rate calls, not plan quotas, so we can’t test that. '
                     f'At list price, haiku-high beats sol61-high ~{main_gap}× per pass; tiers differ. '
                     f'On repo tasks the gap is ~{repo_gap}×. '
                     'But luna-low was cheapest there and passed every repo task.')
    rp = {c: get(ds, c, "repo tasks", "agentic") for c in ("sol61-high", "astra-medium", "sonnet-medium", "haiku-low")}
    need(all(v["passes"] == v["n"] for v in rp.values()), "all four pass every repo task")
    need(min(rp["sol61-high"]["median_s"], rp["astra-medium"]["median_s"]) > 2 * max(rp["sonnet-medium"]["median_s"], rp["haiku-low"]["median_s"]),
         "both Codex picks take over twice the fast Claude medians on repo tasks")
    F["int_repo"] = (f'On repo edits, sol61-high took {rp["sol61-high"]["median_s"]:.0f} s; astra-medium took {rp["astra-medium"]["median_s"]:.0f} s. '
                     f'sonnet-medium and haiku-low took about {rp["sonnet-medium"]["median_s"]:.0f} s. '
                     'Both Codex picks took over twice as long. All passed every hidden test.')
    harness_rows = _harness_rows()
    comparisons = {}
    for c in harness_bias.CFGS:
        cells = []
        for h in ('claude-one-shot', 'codex-tool-loop'):
            rr = [r for r in harness_rows if (r['config'], r['harness']) == (c, h)]
            passed = sum(r['passed'] for r in rr)
            need(passed > 0, f"{c} has passes in {h}")
            cells.append(dict(passes=passed, n=len(rr), upp=sum(r['cost_usd'] for r in rr) / passed,
                              median=statistics.median(r['wall_s'] for r in rr)))
        one, loop = cells
        need(one['n'] == loop['n'] and loop['passes'] > one['passes'], f"Codex's bench improved {c}")
        comparisons[c] = one, loop, loop['upp'] / one['upp'], loop['median'] / one['median']
    lo, la, lc, lt = comparisons['luna-low']
    ho, ha, hc, ht = comparisons['haiku-low']
    need(2.5 <= lc < 3.5 and 2.5 <= lt < 3.5, "luna-low costs about three times per pass and takes about three times the median time")
    need(1 < hc < 1.2 and 0.95 < ht < 1.05, "haiku-low costs slightly more per pass with the same median time")
    F["int_harness"] = ("On Codex's bench, both families gained. "
                        f"luna-low rose from {lo['passes']} to {la['passes']} passes. "
                        f"It cost ~{lc:.0f}× per pass and took ~{lt:.0f}× the median time. "
                        f"haiku-low rose from {ho['passes']} to {ha['passes']} passes. "
                        f"It cost ~{hc:.1f}× per pass, with the same median time.")
    # Build history lives in the existing fair-section narrative, not graded rows.
    template = open(os.path.join(ROOT, "docs", "page.tmpl.md")).read()
    history = template.split('<summary>How Codex built its bench</summary>', 1)[1].split('</details>', 1)[0]
    bugs = re.search(r'Its dry runs missed (\w+) sandbox bugs\. A live call found them; Codex fixed both\.', history)
    need(bugs is not None and bugs[1] == "two" and 'A final "plan and reorient" nudge changed no code.' in history,
         "the recorded bench-build history reports two dry-run misses found live and a code-neutral nudge")
    F["int_build"] = (f'Codex\'s bench dry runs missed {dict(two=2)[bugs[1]]} sandbox bugs; a live call found them. '
                      'Its "plan and reorient" nudge changed no code.')
    cheap, dear = (get(ds, c, "L7 set") for c in ("luna-high", "sol56-high"))
    need(cheap["passes"] == cheap["n"] == dear["n"] > dear["passes"]
         and 0 < cheap["usd_per_pass"] < dear["usd_per_pass"],
         "luna-high beats sol56-high on L7 passes and estimated cost")
    F["int_l7"] = (f'On L7, luna-high passed {cheap["passes"]}/{cheap["n"]}; sol56-high missed. '
                   f'luna-high cost ~{usd(cheap["usd_per_pass"])} per pass versus sol56-high\'s ~{usd(dear["usd_per_pass"])}.')
    stock, trim = (get(ds, c, "trim probe", "trim") for c in ("luna/base", "luna/nofeat"))
    need(stock["passes"] == stock["n"] == trim["n"] == trim["passes"]
         and trim["tokens_in_mean"] < stock["tokens_in_mean"] and trim["usd_per_call"] > 2 * stock["usd_per_call"],
         "tool-feature trimming reduces mean input but more than doubles estimated call cost at equal passes")
    F["int_trim"] = (f'Disabling luna-low\'s tool features cut input {1 - trim["tokens_in_mean"] / stock["tokens_in_mean"]:.0%}, '
                     f'yet raised estimated cost {x(trim["usd_per_call"], stock["usd_per_call"])}.')


def build(summary=None):
    from bench.problems.p13_xor_ring import STATEMENT as xor_statement
    ds = _base()
    if summary is None: summary, _, _ = summarize.build()
    s = _project(ds, summary)
    arms = luna_rescue.arms(); checked = fast_gate.summary()
    ds["rescue"] = _rescue(ds, arms, checked)
    ds["derived_pipelines"] = checked
    ds["design"] = {"rescue_problems": PIDS, "per_rung": len(s["problems"]) // len(s["configs"]["haiku-low"]["by_rung"]),
                    "fast_mode_multiplier": json.load(open(os.path.join(RES, "prices.json")))["fast_mode_multiplier"],
                    "host_agents_md": HOST_AGENTS_MD, "min_pass": MIN_PASS,
                    "xor_time_bound": re.search(r"0 <= t <= ([^`]+)", xor_statement).group(1).replace("**", "^"),
                    "usd_ticks": _currency_ticks([v["usd_per_pass"] for v in {**s["configs"], **s["exploratory"]}.values() if v["usd_per_pass"] is not None])}
    s["design"] = ds["design"]
    ds["categories"] = {cat: {"n_configs": len(rr), "spend": sum(r["spend"] for r in rr)}
                        for cat in configs.CATEGORIES
                        if (rr := [r for r in catalog_rows(ds) if r["category"] == cat])}
    ds["report"] = s
    ds["facts"] = _facts(s, arms)
    ds["tables"] = _tables(s, arms)
    # The earlier 2-repeat run on p01-p06, kept whole under its own label (its tests pin the original sentences and rows).
    comparison = grok.build(ds, s, "grok_first", first=True)
    if comparison:
        ds["grok_first"] = comparison
        lane = s["grok_first"]
        paragraphs, verdict = grok.prose(comparison, lane)
        ds["facts"].update(grok_summary="\n\n".join(paragraphs), grok_verdict=verdict,
                           grok_reach_note=grok.reach_note(comparison, lane))
        ds["tables"].update(grok.tables(comparison, lane, usd))
        probs = comparison["problems"]
        last = max(int(g[1:]) for v in lane.values() for g in v["by_rung"])
        ds["facts"]["grok_scope"] = (
            f"Same-problem comparisons use {probs[0][:3]}–{probs[-1][:3]} ({len(probs)} of {len(s['problems'])} problems), "
            "main + exploratory phases only. Warmup, calibration, fastmode, escalation and hard phases are excluded. "
            "Grok has small n and was not run past " + f"L{last}, so cleared L{last} is a floor. "
            "CLI-reported cost; list price not used for Grok. Codex dollars use tokens × list price with the fast-mode multiplier.")
        ds["facts"]["grok_match_rule"] = (
            f"A lane is comparable when it clears the same rungs and first misses at the same rung on the {len(s['problems'])}-problem "
            f"main ladder. If a Grok config never missed through L{last}, every lane that clears through L{last} counts, with its later results shown.")
        counts = [n for c in lane for rung in comparison["repeat_counts"][c].values() for n in rung.values()]
        ds["facts"]["grok_first_title"] = f"First run ({min(counts)} repeats, {probs[0][:3]}–{probs[-1][:3]})"
        rungs = sorted({v["rung"] for v in s["problems"].values()})
        ds["facts"]["grok_key"] = (f"A lane is an existing config: one model at one effort. Rungs L{min(rungs)}–L{max(rungs)} get harder step by step. "
                                   "Cleared through L2 means every call passed on L1 and L2.")
    # The full spectrum (2026-10-28): every problem, 5 repeats, for low, fast-low and high; medium stays on p01-p06.
    full = grok.build(ds, s)
    if full:
        ds["grok_comparison"] = full
        ds["tables"].update(grok.full_tables(full, s["grok"], usd))
        ds["tables"]["grok_lead"], ds["tables"]["grok_better"] = grok.full_lead(full, s["grok"], usd)
        ds["facts"]["grok_full_note"] = grok.full_note(full, s["grok"], summarize.function_rows())
        short = [c for c in s["grok"] if c not in grok.full_run(full, s["grok"])]
        ds["facts"]["grok_not_run"] = (
            (f"{', '.join(short)} covers {sorted(s['grok'][short[0]]['by_problem'])[0][:3]}–{sorted(s['grok'][short[0]]['by_problem'])[-1][:3]} only, "
             "so its cells for the other problems are dashes. ") if short else "") + "A dash means no attempt, not a failure."
    _devin(ds, s)
    _equivalents(ds)
    _interesting(ds)
    method_appendix(ds)
    return ds


def _devin(ds, s):
    """The Devin free-tier lane (PLAN.md deviation 24): facts and one table. It has no token or cost data, so it never gets a $ per pass."""
    F, lane = ds["facts"], {c: v for c, v in s["exploratory"].items() if c in configs.DEVIN_CONFIGS}
    F["devin_group"] = configs.DEVIN_GROUP
    if not lane: return
    c = next(iter(lane)); v = lane[c]
    rows = [r for r in summarize.function_rows() if r["config"] == c]
    plan = open(os.path.join(ROOT, "PLAN.md")).read()
    need(configs.DEVIN_UPGRADE_ERROR in plan and f"{configs.DEVIN_STAGE2_MIN}/12" in plan and v["model"] in plan, "PLAN.md deviation 24 holds the Devin error text, the stage-2 bar and the model")
    need(v["n"] == len(s["problems"]) == len(rows) and v["usd_per_pass"] is None and v["cost_kind"] == "unmetered", "Devin ran each problem once and has no $")
    by = {}
    for r in rows: by.setdefault(r["outcome"], []).append(r["problem"])
    names = lambda oc: ", ".join(pshort(p) for p in sorted(by.get(oc, []))) or "none"
    F["devin_k"], F["devin_n"] = str(v["passes"]), str(v["n"])
    F["devin_median_s"] = f'{v["latency_s"]["median"]:.1f}'
    F["devin_model"] = v["model"]
    F["devin_error"] = configs.DEVIN_UPGRADE_ERROR
    F["devin_stage2_min"] = str(configs.DEVIN_STAGE2_MIN)
    F["devin_lead"] = (f"Devin ran each of the {v['n']} main-ladder problems once on {v['model']}. It passed {v['passes']}/{v['n']} (pass rate {pct(v['pass_at_1'])}), "
                       f"with a median {F['devin_median_s']} s per call. Timeouts: {names('timeout')}. Wrong answers: {names('wrong')}. Crashes: {names('crash')}. "
                       "It reports no tokens and no cost, so it has no $ per pass and appears on no $ chart, in no Winner pick and on no best-trade-offs line.")
    F["devin_why"] = (f"Only {v['model']} ran. The account is on the free tier, and every other Devin-native model (adaptive, swe-2-medium, swe-2-high, swe-2-max and the "
                      f"-lightning variants) returned exactly: {configs.DEVIN_UPGRADE_ERROR}")
    F["devin_bypass"] = ("The rows bypass devin-delegate, which has no model passthrough, wraps the prompt in an envelope, falls back to Codex on failure, "
                         "injects auto-context and caches results. The bench called the devin CLI directly in an empty directory, in auto permission mode, one repeat.")
    F["devin_stage2"] = (f"Stage 2 (repeats 2 to 5) needed at least {configs.DEVIN_STAGE2_MIN} of {v['n']} on stage 1. It got {v['passes']}, so it did not run.")
    F["devin_verdict"] = "Verdict: not a delegate on the free tier."
    outcome = {r["problem"]: r["outcome"] for r in rows}
    ds["tables"]["devin_reach"] = md_table(
        ["rung", "passed", "what happened"],
        [[g, f"{r['passed']}/{r['n']}", ", ".join(f"{pshort(p)} {outcome[p]}" for p in sorted(s["problems"]) if f"L{s['problems'][p]['rung']}" == g and outcome[p] != "pass") or "all passed"]
         for g, r in v["by_rung"].items()])


def view(ds):
    """Cached report-shaped projections of the canonical config/set rows."""
    return {**ds["report"], "rescue": ds["rescue"], "facts": ds["facts"]}


def read():
    return json.load(open(PATH))


def text(ds):
    return json.dumps(ds, indent=1, ensure_ascii=False) + "\n"


def main():
    summary, tables, manifest = summarize.build()
    ds = build(summary); open(PATH, "w").write(text(ds))
    json.dump(summary, open(os.path.join(RES, "summary.json"), "w"), indent=1)
    open(os.path.join(RES, "report", "tables.md"), "w").write(tables)
    json.dump(manifest, open(os.path.join(RES, "manifest.json"), "w"), indent=1)
    open(os.path.join(RES, "report", "luna_rescue.md"), "w").write(luna_rescue.table(luna_rescue.arms()) + "\n")
    print(f"dataset: {len(ds['rows'])} rows, {len(keys(ds))} configs -> results/dataset.json")


if __name__ == "__main__":
    main()
