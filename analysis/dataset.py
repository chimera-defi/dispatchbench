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
Columns: id, source, config, display, family, category, what, set, passes, n, pass_rate, ci95, usd_per_pass, claude_usd_per_pass,
codex_usd_per_pass, usd_per_call, spend, spend_claude, spend_codex, unknown_usd, median_s, p25_s, p75_s, tokens_in_mean, tokens_out_mean,
cost_kind, groups (problems or tasks). No model calls. Run: python3 -m analysis.dataset"""
import json, os, statistics
from collections import defaultdict

from analysis import configs, stats
from analysis.luna_rescue import claude_usd
from analysis.summarize import RES, ROOT, cost, load, scale

PATH = os.path.join(RES, "dataset.json")
REPORT_PROBLEMS = 12; REPEATS = 5


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
        out.append((src, name, st, {"ok": bool(ok), "sec": sec, "group": group, "usd": usd, "claude": _claude(r, src, usd), "in": tin, "out": tout, "cli": r.get("cli", r.get("builder_kind", ""))}))
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
    p25, p75 = _quart(secs)
    spend = sum(known); sc = sum(cl)
    return {"id": e["id"], "source": src, "config": name, "display": e["display"], "family": e["family"], "category": e["category"], "what": e["what"], "set": st, "files": e["files"],
            "passes": k, "n": n, "pass_rate": round(k / n, 4), "ci95": ci, "groups": len(cells),
            "usd_per_pass": round(spend / k, 6) if k and complete else None, "claude_usd_per_pass": round(sc / k, 6) if k and complete else None,
            "codex_usd_per_pass": round((spend - sc) / k, 6) if k and complete else None, "usd_per_call": round(spend / n, 6) if complete else None,
            "spend": round(spend, 6), "spend_claude": round(sc, 6), "spend_codex": round(spend - sc, 6), "unknown_usd": n - len(known),
            "median_s": round(statistics.median(secs), 2), "p25_s": round(p25, 2), "p75_s": round(p75, 2),
            "tokens_in_mean": round(statistics.mean(x["in"] or 0 for x in rr)), "tokens_out_mean": round(statistics.mean(x["out"] or 0 for x in rr)),
            "cost_kind": "measured" if rr[0]["cli"].startswith("claude") else "proxy"}


def build():
    groups = defaultdict(list)
    for src, name, st, x in _rows(): groups[(src, name, st)].append(x)
    rows = [_row(src, name, st, rr) for (src, name, st), rr in groups.items()]
    allr = defaultdict(list)
    for (src, name, st), rr in groups.items(): allr[(src, name)] += rr
    rows += [_row(src, name, "all runs", rr) for (src, name), rr in allr.items()]
    order = {c: i for i, c in enumerate(configs.CATEGORIES)}
    rows.sort(key=lambda r: (r["set"] == "all runs", order.get(r["category"], 99), r["source"], r["set"], list(configs.REGISTRY).index((r["source"], r["config"])) if (r["source"], r["config"]) in configs.REGISTRY else 999))
    return {"generated_from": sorted({f for r in rows for f in r["files"]}), "sets": sorted({r["set"] for r in rows}), "rows": rows}


def keys(ds):
    return {(r["source"], r["config"]) for r in ds["rows"] if r["set"] == "all runs"}


def get(ds, config, set_, source="main"):
    """The one row for (config, set); KeyError if the config never ran in that set."""
    return next(r for r in ds["rows"] if r["source"] == source and r["config"] == config and r["set"] == set_)


def usd(v):
    """The one cost formatter for charts and tables built on the dataset: None is a dash, 0 is $0, then 2 decimals from $1, 4 from $0.01, 6 below
    (so $0.0009 and $0.00097 never sit side by side). The older charts keep their own formats until they migrate."""
    if v is None: return "–"
    return "$0" if v == 0 else f"${v:,.2f}" if v >= 1 else f"${v:.4f}" if v >= 0.01 else f"${v:.6f}"


def read():
    return json.load(open(PATH))


def text(ds):
    return json.dumps(ds, indent=1, ensure_ascii=False) + "\n"


def main():
    ds = build(); open(PATH, "w").write(text(ds))
    print(f"dataset: {len(ds['rows'])} rows, {len(keys(ds))} configs -> results/dataset.json")


if __name__ == "__main__":
    main()
