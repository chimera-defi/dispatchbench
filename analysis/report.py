"""Render README.md from docs/readme.tmpl.md, docs/REPORT.md from docs/report.tmpl.md and results/report/page.html from docs/page.tmpl.md. No model calls,
standard library only.

Every number in the prose is a {{fact}} computed here from results/; the templates hold no measured number (make
audit checks that). The page template is HTML; its charts, grid and short table come from analysis/page.py.

Template syntax:
  {{name}}               a fact (string) from facts()
  {{table:name}}         a markdown table from tables_md(); on the page it becomes a sortable table
  {{chart:file|caption}} README (the caption may hold facts): an image link to results/report/charts/<file>; page: the SVG inline, with the caption
  {{w_name}}             page only: a widget from analysis/page.py (scatters, grid, token bars, short table)
  lines starting "@readme " or "@page " appear only in that output
"""
import html, json, os, re, statistics

from analysis import luna_rescue, page as pagew
from analysis.charts import HOST_AGENTS_MD, MIN_PASS
from analysis.summarize import ROOT, RES, FUNC, AGENT, ci_text, cost, cost_uncached, load, pct

TEMPLATE = os.path.join(ROOT, "docs", "report.tmpl.md")
PAGE_TEMPLATE = os.path.join(ROOT, "docs", "page.tmpl.md")  # the page: HTML with facts and widgets
README = os.path.join(ROOT, "README.md")  # short front page, from docs/readme.tmpl.md
README_TEMPLATE = os.path.join(ROOT, "docs", "readme.tmpl.md")
REPORT = os.path.join(ROOT, "docs", "REPORT.md")  # the full report, from docs/report.tmpl.md
PAGE = os.path.join(RES, "report", "page.html")
CHARTS = os.path.join(RES, "report", "charts")
PAGE_DIR = os.path.join(ROOT, "docs", "page")
QUALITY = os.path.join(RES, "quality.jsonl")
NEW_CODEX = ("sol61-high", "sol56-high", "astra-medium", "luna56-high", "luna56-low")  # exploratory Codex additions, see bench/run.py
GROWTH_MARGIN = 0.3  # a fitted time exponent this far above the reference's counts as worse growth


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


def u(v, d=5):
    return f"${v:.{d}f}"


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


def facts(s):
    F = Facts(); cfg, ex, ag, hard = s["configs"], s["exploratory"], s["agentic"], s["hard"]
    rows = load(FUNC); agent = load(AGENT); main_rows = [r for r in rows if r["phase"] == "main"]
    every = {**cfg, **ex}
    nprob = len(s["problems"]); ntask = len(next(iter(ag.values()))["by_task"])
    F.update(n_problems=str(nprob), n_tasks=str(ntask), n_configs=str(len(cfg)), n_l7=str(len({p for v in hard.values() for p in v["by_problem"]})),
             repeats=str(cfg["haiku-low"]["n"] // nprob), n_calls=str(cfg["haiku-low"]["n"]), n_all_problems=str(nprob + len({p for v in hard.values() for p in v["by_problem"]})),
             agent_repeats=str(next(iter(ag.values()))["n"] // ntask), n_rungs=str(len(cfg["haiku-low"]["by_rung"])), per_rung=str(nprob // len(cfg["haiku-low"]["by_rung"])))
    need(all(v["n"] == cfg["haiku-low"]["n"] for v in every.values()), "every function-track config has the same number of calls")
    F["host_agents_md"] = HOST_AGENTS_MD; F["min_pass"] = pct(MIN_PASS)
    F["rung_attempts"] = str(cfg["haiku-low"]["by_rung"]["L1"]["n"])
    sp = s["spend"]
    F["claude_usd"] = f"${sp['claude_measured_usd']:.2f}"; F["codex_usd"] = f"${sp['codex_proxy_usd']:.2f}"
    for c, v in every.items():
        k = c.replace("-", "_")
        F[f"{k}_pass"] = pct(v["pass_at_1"]); F[f"{k}_k"] = f"{v['passes']}/{v['n']}"; F[f"{k}_upp"] = u(v["usd_per_pass"])
        F[f"{k}_med"] = f"{v['latency_s']['median']:.1f}"; F[f"{k}_rsn"] = n(v["tokens_mean"]["reasoning_tok"]); F[f"{k}_rsn10"] = about(v["tokens_mean"]["reasoning_tok"])
        F[f"{k}_in"] = n(v["tokens_mean"]["in_tok"]); F[f"{k}_total"] = f"${v['usd_total']:.3f}"
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
    F["esc_k"] = f"{e['passes']}/{e['n']}"; F["esc_base"] = f"{e['base_passes']}/{e['base_n']}"; F["esc_vs"] = e["vs"]
    d = vs(s, "luna-high", "luna-medium"); F["lh_vs_lm"] = p1(d["diff"]); F["lh_vs_lm_ci"] = ci_pts(d["ci95"])
    # finding 3 and the token callout: stripped harness
    lb = ex["luna-low-bare"]
    F["in_cut"] = pct(1 - lb["tokens_mean"]["in_tok"] / ll["tokens_mean"]["in_tok"])
    need(1 - lb["tokens_mean"]["in_tok"] / ll["tokens_mean"]["in_tok"] > 0.5, "stripping the harness cuts input by more than half")
    d = vs(s, "luna-low-bare", "haiku-low"); F["lb_vs_hl"] = p1(d["diff"]); F["lb_vs_hl_ci"] = ci_pts(d["ci95"]); need(d["ci95"][1] == 0, "CI upper end touches zero")
    d = vs(s, "luna-low-bare", "luna-low"); F["lb_vs_ll"] = p1(d["diff"]); F["lb_vs_ll_ci"] = ci_pts(d["ci95"]); need(d["ci95"][0] < 0 < d["ci95"][1], "stripping changes nothing")
    need(lb["usd_per_pass"] < hl["usd_per_pass"] < lb["usd_per_pass_uncached"], "stripped luna cheaper than haiku only with the cache")
    F["lb_upp_nocache"] = u(lb["usd_per_pass_uncached"]); F["lb_nocache_above"] = pct(lb["usd_per_pass_uncached"] / hl["usd_per_pass"] - 1)
    tr = s["trim"]["floor"]
    F["floor_stock"] = n(tr["luna/base"]["in_tok"]); F["floor_min"] = n(tr["luna/noshell"]["in_tok"])
    # finding 4: agentic
    need(all(v["hidden_pass"] == v["n"] for v in ag.values()), "every agentic run passed")
    F["ag_k"] = f"{ag['luna-low']['hidden_pass']}/{ag['luna-low']['n']}"; F["ag_runs"] = str(sum(v["n"] for v in ag.values()))
    for c, v in ag.items():
        k = c.replace("-", "_"); F[f"ag_{k}_usd"] = f"${v['usd_per_run']:.4f}" if v["usd_per_run"] < 0.01 else f"${v['usd_per_run']:.3f}"
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
    F["terra_call"] = u(pr["terra/noshell"]["usd_per_call"], 4); F["terra_x"] = f"{pr['terra/noshell']['usd_per_call'] / pr['haiku']['usd_per_call']:.0f}×"
    # L7
    probs = sorted({p for v in hard.values() for p in v["by_problem"]}); F["l7_bound"] = pct(0.05 ** (1 / len(probs)))
    hh = hard["haiku-low"]; need(hh["outcomes"] == {"pass": hh["passes"], "timeout": hh["n"] - hh["passes"]}, "haiku-low L7 misses are all timeouts")
    hrows = [r for r in rows if r["phase"] == "hard" and r["config"] == "haiku-low" and not r["passed"]]
    need(len({r["problem"] for r in hrows}) == 1 and len({r["grade_detail"] for r in hrows}) == 1, "same p15 case")
    F["l7_hl_fail"] = str(len(hrows)); F["l7_hl_pass_p15"] = str(hh["by_problem"]["p15_paint_erase"])
    for c in ("luna-high", "sol61-medium", "sonnet-medium", "haiku-low"):
        F[f"l7_{c.replace('-', '_')}_upp"] = u(hard[c]["usd_per_pass"], 4); F[f"l7_{c.replace('-', '_')}_med"] = f"{hard[c]['latency_s']['median']:.0f}"
    lo, hi = sorted([hard["sol61-medium"]["usd_per_pass"], hard["sonnet-medium"]["usd_per_pass"]]); F["l7_dear"] = f"${lo:.3f}–{hi:.3f}"
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
    a = luna_rescue.arms(); F["rescue_n"] = str(a["luna-low"]["n"])
    for c, v in a.items():
        k = re.sub(r"\W", "_", c); F[f"r_{k}_k"] = f"{v['passes']}/{v['n']}"; F[f"r_{k}_upp"] = u(v["usd_per_pass"]); F[f"r_{k}_s"] = f"{v['median_s']:.0f}s"
    b0, b1, b2, sc, ee = a["luna-low"], a["luna-low-noshell-B1"], a["luna-low-noshell-B2"], a["luna-low-selftest"], a["luna-low+haiku-low-repair"]
    F["r_b1_gain"] = str(b1["passes"] - b0["passes"]); F["r_b2_loss"] = str(b1["passes"] - b2["passes"])
    F["r_c_cost_x"] = x(sc["usd_per_pass"], b0["usd_per_pass"]); F["r_c_time_x"] = x(sc["median_s"], b0["median_s"])
    need(sc["usd_per_pass"] > a["haiku-low"]["usd_per_pass"] and sc["passes"] < a["haiku-low"]["passes"], "self-test costs more than haiku for fewer passes")
    F["r_e_luna"] = f"{sum(r['luna_passed'] for r in ee['rows'])}/{ee['n']}"; F["r_e_changed"] = str(sum(r["haiku_changed"] for r in ee["rows"]))
    F["r_e_haiku_share"] = pct(sum(r["haiku_cost_usd"] for r in ee["rows"]) / ee["usd_total"])
    F["r_e_vs_hl_x"] = x(ee["usd_per_pass"], a["haiku-low"]["usd_per_pass"]); F["r_e_more"] = str(ee["passes"] - a["haiku-low"]["passes"])
    F["orchestrator"] = "Claude Opus 5.5"  # the model that designed, ran and checked this benchmark; not a measured config
    hr, lr, hv, sm = a["luna-high-bare+haiku-on-fail"], a["luna-low+haiku-on-fail"], a["luna-high-bare+haiku-review-all"], a["sonnet-medium"]
    need(hv["passes"] == hv["n"] == sm["passes"], "luna-high + Haiku review and sonnet-medium never failed on the hard set")
    hm = a["haiku-medium"]; need(hm["passes"] == hm["n"] and hm["usd_per_pass"] < hv["usd_per_pass"], "haiku-medium alone: no miss, cheaper than the pipeline")
    F["hm_vs_pipe_x"] = x(hv["usd_per_pass"], hm["usd_per_pass"]); F["r_pids"] = str(len(luna_rescue.PIDS))
    F["sm_vs_hm_x"] = f"{cfg['sonnet-medium']['usd_per_pass'] / cfg['haiku-medium']['usd_per_pass']:.0f}×"
    need("haiku-medium" not in hard, "haiku-medium did not run the L7 rung")
    F["g_vs_sm_x"] = x(sm["usd_per_pass"], hv["usd_per_pass"]); F["g_hi_fixed"] = str(sum(r["repaired"] for r in hr["rows"]))
    F["g_hi_missed"] = str(hr["n"] - hr["passes"]); F["g_lo_fixed"] = str(sum(r["repaired"] for r in lr["rows"]))
    # appendix: the pilot (results/2026-10-22-pilot.jsonl) and the trim probe's pair step on three of its problems
    pl = s["pilot"]; prow = load(os.path.join(RES, "2026-10-22-pilot.jsonl"))
    need(all(v["passes"] == v["n"] for v in pl.values()), "every pilot run passed")
    F["pilot_configs"] = str(len(pl)); F["pilot_runs"] = str(sum(v["n"] for v in pl.values())); F["pilot_problems"] = str(len({r["problem"] for r in prow}))
    pf = s["pilot_fast"]; F["fast_mult"] = f'{json.load(open(os.path.join(RES, "prices.json")))["fast_mode_multiplier"]:g}'
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
    F["pilot_luna_call"] = u(pr["luna/noshell"]["usd_per_call"]); F["pilot_haiku_call"] = u(pr["haiku"]["usd_per_call"])
    F["pilot_luna_k"] = f"{pr['luna/noshell']['passes']}/{pr['luna/noshell']['n']}"; F["pilot_haiku_k"] = f"{pr['haiku']['passes']}/{pr['haiku']['n']}"
    q = [r for r in quality_rows() if r["outcome"] == "pass" and r["phase"] in ("main", "exploratory", "escalation") and r.get("time_ratio") is not None]
    if q:
        w = max(q, key=lambda r: r["time_ratio"])
        F["q_worst_x"] = f"{w['time_ratio']:.0f}×"; F["q_worst_problem"] = w["problem"].split("_")[0]
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
    F["growth_margin"] = str(GROWTH_MARGIN)
    F["n_solutions"] = str(sum(1 for _, _, fs in os.walk(os.path.join(RES, "solutions")) for f in fs if f.endswith(".py")))
    # Codex additions (exploratory, run after the report at the operator's request)
    nr = [r for r in rows if r["config"] in NEW_CODEX and r["phase"] != "fastmode"]; F["new_date"] = min(r["ts"] for r in nr)[:10]; F["n_new_codex"] = str(len(NEW_CODEX))
    nu = sum(map(cost, nr + [r for r in agent if r["config"] in NEW_CODEX]))  # function and repo-task runs alike
    F["codex_new_usd"] = f"${nu:.2f}"; F["codex_old_usd"] = f"${sp['codex_proxy_usd'] - nu - sp['codex_fastmode_usd']:.2f}"; F["fm_usd"] = f"${sp['codex_fastmode_usd']:.2f}"
    for c in NEW_CODEX:
        k = "x_" + c.replace("-", "_"); e, h = ex[c], hard[c]
        F[k + "_k"] = f"{e['passes']}/{e['n']}"; F[k + "_upp"] = u(e["usd_per_pass"], 4); F[k + "_med"] = f"{e['latency_s']['median']:.1f}"
        F[k + "_hk"] = f"{h['passes']}/{h['n']}"; F[k + "_hupp"] = u(h["usd_per_pass"], 4)
    for c in ("luna-high", "sol61-medium"):
        F["x_base_" + c.replace("-", "_") + "_hk"] = f"{hard[c]['passes']}/{hard[c]['n']}" if c in hard else "–"
    need(all(ex[c]["passes"] == ex[c]["n"] for c in ("sol56-high", "astra-medium")), "sol56-high and astra-medium never failed L1-L6")
    need(hard["luna-high"]["passes"] > hard["luna56-high"]["passes"] and ex["luna56-high"]["usd_per_pass"] > ex["luna-high"]["usd_per_pass"], "gpt-6 luna-high beats 5.6 luna-high on L7 and costs less")
    need(hard["astra-medium"]["passes"] == hard["astra-medium"]["n"] > hard["sol56-high"]["passes"], "astra perfect on L7, sol56-high not")
    F["x_sol56_vs_hm"] = f"{ex['sol56-high']['usd_per_pass'] / cfg['haiku-medium']['usd_per_pass']:.0f}×"
    F["x_astra_vs_hm"] = f"{ex['astra-medium']['usd_per_pass'] / cfg['haiku-medium']['usd_per_pass']:.0f}×"
    sm_all = cfg["sonnet-medium"]["usd_per_pass"]; perfect = [c for c in list(cfg) + list(ex) if (cfg.get(c) or ex[c])["passes"] == (cfg.get(c) or ex[c])["n"] and c in hard and hard[c]["passes"] == hard[c]["n"]]
    need(sorted(perfect) == ["astra-medium", "sol61-high", "sonnet-medium"] and min(ex[c]["usd_per_pass"] for c in ("astra-medium", "sol61-high")) > sm_all,
         "sonnet-medium is the cheapest config with no miss anywhere; astra-medium and sol61-high the only others")
    need(all(ag[c]["hidden_pass"] == ag[c]["n"] for c in ("astra-medium", "sol61-high")), "both trusted Codex configs passed every repo task")
    F["x_s61h_vs_sm"] = x(ex["sol61-high"]["usd_per_pass"], sm_all)
    # trusted Codex builders: who bills what. Codex calls bill the Codex subscription, so their Claude $ is zero by construction.
    ah, sh = ex["astra-medium"], ex["sol61-high"]
    F["x_astra_vs_s61h"] = x(ah["usd_per_pass"], sh["usd_per_pass"]); F["ag_astra_vs_s61h"] = x(ag["astra-medium"]["usd_per_run"], ag["sol61-high"]["usd_per_run"])
    need(ah["latency_s"]["median"] < sh["latency_s"]["median"] and ag["astra-medium"]["latency_s"]["median"] < ag["sol61-high"]["latency_s"]["median"], "astra faster than sol61-high")
    F["ag_n"] = str(ag["sol61-high"]["n"]); F["claude_zero"] = "$0"
    F["ag_claude_med"] = f"{statistics.mean(ag[c]['latency_s']['median'] for c in ('haiku-low', 'sonnet-medium')):.0f}"
    ga = luna_rescue.arms()
    for c in ("sol61-high+haiku-on-fail", "astra-medium+haiku-on-fail"):
        g = ga[c]; need(g["passes"] == g["n"], f"{c} never failed on the hard set"); F["g_" + c.split("-")[0] + "_repairs"] = str(sum(r["repaired"] for r in g["rows"]))
        F["g_" + c.split("-")[0] + "_cupp"] = u(g["claude_usd_per_pass"])
    F["x_astra_vs_sm"] = f"{ex['astra-medium']['usd_per_pass'] / sm_all:.0f}×"
    F["x_l56_vs_lh"] = x(ex["luna56-high"]["usd_per_pass"], ex["luna-high"]["usd_per_pass"])
    return F


def md_table(head, rows, bold=None):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(map(str, r)) + " |" for r in rows])


def tables_md(s):
    T = {}; cfg, ex = s["configs"], s["exploratory"]; nprob = len(s["problems"])
    T["result"] = md_table(["config", "pass@1", "95% CI", "median s", "p90 s", "$ per pass", f"total $ ({cfg['haiku-low']['n']} calls)", "$ kind"],
                           [[c + (" (exploratory)" if c in ex else ""), f"{pct(v['pass_at_1'])} ({v['passes']}/{v['n']})", ci_text(v["passes"], v["n"], v["ci95"], nprob),
                             f"{v['latency_s']['median']:.1f}", f"{v['latency_s']['p90']:.1f}", f"{v['usd_per_pass']:.5f}", f"{v['usd_total']:.3f}", v["cost_kind"]]
                            for c, v in {**cfg, **ex}.items()])
    T["tokens"] = md_table(["config", "mean input", "of which cached", "mean output", "of which reasoning", "$ per 1k tokens"],
                           [[c + (" (exploratory)" if c in ex else ""), n(v["tokens_mean"]["in_tok"]), n(v["tokens_mean"]["cached_tok"]), n(v["tokens_mean"]["out_tok"]),
                             n(v["tokens_mean"]["reasoning_tok"]), f"{1000 * v['usd_per_call'] / (v['tokens_mean']['in_tok'] + v['tokens_mean']['out_tok']):.5f}"]
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
                        + [f"{v['latency_s']['median']:.1f}", n(v["tokens_mean"]["reasoning_tok"]), f"{v['usd_per_pass']:.4f}", v["cost_kind"]] for c, v in hard.items()])
    fail = s["failures"]; cols = list(dict.fromkeys(c for f in fail.values() for c in f["cells"]))
    ab = {"wrong": "w", "crash": "c", "timeout": "t", "no_code": "n"}

    def cell(d):
        if not d: return "–"
        f = " ".join(f"{k}{ab[o]}" for o, k in sorted(d["fails"].items()))
        k = f"**{d['passed']}**" if d["passed"] * 5 <= 2 * d["n"] else str(d["passed"])
        return k + (f" ({f})" if f else "")
    T["fail"] = md_table(["problem"] + cols, [[f"{p[:3]} L{f['rung']}"] + [cell(f["cells"].get(c)) for c in cols] for p, f in fail.items()])
    ag = s["agentic"]; at = json.load(open(os.path.join(RES, "agentic_tests.json")))
    T["agentic"] = md_table(["config", "hidden tests passed", "runs that wrote the requested test file", "test functions added", "median s", "$ per run", "$ kind"],
                            [[c, f"{v['hidden_pass']}/{v['n']}", f"{v['own_tests_written']}/{v['n']}",
                              (lambda rr: str(sum(r["test_functions_added"] for r in rr)) if all(r["test_functions_added"] is not None for r in rr)
                               else f"≥{sum(r['test_functions_lower_bound'] for r in rr)}")([r for r in at if r["config"] == c]),
                              f"{v['latency_s']['median']:.1f}", f"{v['usd_per_run']:.4f}", v["cost_kind"]] for c, v in sorted(ag.items(), key=lambda kv: kv[1]["usd_per_run"])])
    a = luna_rescue.arms()
    T["rescue"] = md_table(["config", "passed", "$ per pass", "median s"], [[v["label"], f"{v['passes']}/{v['n']}", f"{v['usd_per_pass']:.5f}", f"{v['median_s']:.1f}"] for v in a.values()])
    pr = s["trim"]["pair"]; lab = {"haiku": "haiku-low, tools off", "luna/base": "luna-low, stock harness", "luna/nofeat": "luna-low, tool features off", "luna/noshell": "luna-low, stripped"}
    T["pilot"] = md_table(["config", "passes", "median input", "median s", "$ per call", "$ kind"],
                          [[lab[c], f"{v['passes']}/{v['n']}", n(v["in_median"]), f"{v['median_s']:.1f}", f"{v['usd_per_call']:.5f}", v["cost_kind"]] for c, v in pr.items() if c in lab])
    T["quality"] = quality_table(s)
    T["fastmode"], T["blind"] = fastmode_tables(s)
    T["configs"] = md_table(["config", "CLI", "model", "effort"], [[c, {"claude": "Claude Code", "codex": "Codex CLI"}[v["cli"]], v["model"], v["effort"]] for c, v in cfg.items()])
    return T


def quality_rows():
    return [json.loads(l) for l in open(QUALITY)] if os.path.exists(QUALITY) else []


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
        out.append([c, str(len(rr)), f"{med([r['loc'] for r in rr]):.0f}", f"{med([r['cc_max'] for r in rr]):.0f}",
                    f"{sum(r['lint_warnings'] for r in rr) / len(rr):.2f}", f"{med(tr):.2f}" if tr else "–", f"{slow}", f"{med(mr):.2f}" if mr else "–"])
    return md_table(["config", "passing solutions", "median LOC", "median max complexity", "lint warnings per solution", "median time vs reference",
                     "growth worse than reference", "median peak memory vs reference"], out)


BLIND = os.path.join(ROOT, "results", "appendix", "blind_readability.json")
FM_LABEL = {"sol61-high": "sol61-high, default tier (control)", "sol61-high-fast": "sol61-high, fast mode", "sol61-xhigh": "sol61-xhigh, default tier"}


def fastmode_tables(s):
    fm = s.get("fastmode") or {}
    if not fm: return "_no fast-mode runs yet._", "_no blind read yet._"
    q = [r for r in quality_rows() if r.get("phase") == "fastmode" and r.get("outcome") == "pass"]; out = []
    for c, v in fm.items():
        rr = [r for r in q if r["config"] == c]; need(len(rr) == v["passes"], f"quality rows cover every passing fast-mode {c} solution")
        tr = [r["time_ratio"] for r in rr if r.get("time_ratio") is not None]
        out.append([FM_LABEL[c], f"{v['passes']}/{v['n']}", f"{v['median_s']:.1f}", n(v["out_median"]), f"{v['usd_per_pass']:.4f}",
                    f"{statistics.median(r['loc'] for r in rr):.0f}", f"{statistics.median(r['cc_max'] for r in rr):.0f}",
                    f"{sum(r['lint_warnings'] for r in rr) / len(rr):.2f}", f"{statistics.median(tr):.2f}" if tr else "–"])
    t1 = md_table(["config", "passed", "median s", "median output tokens", "$ per pass (proxy)", "median LOC", "median max complexity",
                   "lint warnings per solution", "median time vs reference"], out)
    b = json.load(open(BLIND)) if os.path.exists(BLIND) else None
    if not b: return t1, "_no blind read yet._"
    cs = sorted({i["config"] for i in b["items"]}, key=lambda c: -statistics.mean(i["score"] for i in b["items"] if i["config"] == c))
    t2 = md_table(["config", "solutions read", "mean score (1 to 10)", "would block"],
                  [[c, str(sum(1 for i in b["items"] if i["config"] == c)), f"{statistics.mean(i['score'] for i in b['items'] if i['config'] == c):.2f}",
                    str(sum(i["block"] for i in b["items"] if i["config"] == c))] for c in cs])
    return t1, t2

# ---------- rendering ----------

PLACE = re.compile(r"\{\{([^{}]+)\}\}")


def fill(text, F, T, mode):
    def sub(m):
        k = m.group(1)
        if k.startswith("table:"): return T[k[6:]] if mode == "readme" else to_html(T[k[6:]])
        if k.startswith("chart:"):
            f, cap = k[6:].split("|", 1)
            if mode == "readme": return f"![{cap}](results/report/charts/{f})"
            return f"<figure>{open(os.path.join(CHARTS, f)).read().strip()}<figcaption>{html.escape(cap)}</figcaption></figure>"
        return F[k]
    lines = []
    for line in text.split("\n"):
        tag = line.split(" ", 1)[0]
        if tag in ("@readme", "@page"):  # a bare tag is an empty line in that output
            if mode != tag[1:]: continue
            line = line[len(tag) + 1:]
        lines.append(line)
    plain = lambda m: m.group(0) if m.group(1).split(":")[0] in ("table", "chart") else F[m.group(1)]
    return PLACE.sub(sub, PLACE.sub(plain, "\n".join(lines)))  # facts first, so chart captions can hold them


def inline(t):
    """Markdown inline spans to HTML: code, bold, links. Relative links point into the repository, which a reader of the page may not have, so they render as code."""
    out = []; parts = re.split(r"(`[^`]+`)", t)
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append(f"<code>{html.escape(p[1:-1])}</code>"); continue
        if p.startswith("<figure>") or p.startswith("<div") or p.startswith("<h2") or p.startswith("<script") or p.startswith("<p class"):
            out.append(p); continue
        p = html.escape(p, quote=False)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', p)
        p = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: m.group(1) if m.group(1).startswith("<code>") else f"<code>{m.group(1)}</code>" if "/" in m.group(1) or "." in m.group(1) else m.group(1), p)
        out.append(p)
    return "".join(out)


def to_html(md):
    """Enough markdown for this one template: headings, paragraphs, lists, tables, fenced code, blockquotes and raw HTML blocks."""
    L = md.split("\n"); i = 0; out = []
    while i < len(L):
        line = L[i]
        if not line.strip(): i += 1; continue
        if line.startswith("<"):  # raw HTML block (figures, page-only markup) runs to the next blank line
            j = i
            while j < len(L) and L[j].strip(): j += 1
            out.append("\n".join(L[i:j])); i = j; continue
        if line.startswith("```"):
            j = i + 1
            while not L[j].startswith("```"): j += 1
            out.append("<pre><code>" + html.escape("\n".join(L[i + 1:j])) + "</code></pre>"); i = j + 1; continue
        m = re.match(r"(#{1,3}) (.*)", line)
        if m:
            lv = len(m.group(1)); txt = m.group(2); hid = re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>|`", "", txt.lower())).strip("-")
            out.append(f"<h{lv} id=\"{hid}\">{inline(txt)}</h{lv}>"); i += 1; continue
        if line.startswith("|"):
            j = i
            while j < len(L) and L[j].startswith("|"): j += 1
            cells = [[c.strip() for c in r.strip().strip("|").split(" | ")] for r in L[i:j]]
            head, body = cells[0], cells[2:]
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f"<div class=\"wrap\"><table class=\"sortable\"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>"); i = j; continue
        if line.startswith("> "):
            j = i; buf = []
            while j < len(L) and L[j].startswith(">"): buf.append(L[j][1:].strip()); j += 1
            out.append(f"<div class=\"rule\">{inline(' '.join(buf))}</div>"); i = j; continue
        if re.match(r"(- |\d+\. )", line):
            tag = "ol" if line[0].isdigit() else "ul"; items = []; j = i
            while j < len(L) and L[j].strip():
                if re.match(r"(- |\d+\. )", L[j]): items.append(re.sub(r"^(- |\d+\. )", "", L[j]))
                else: items[-1] += " " + L[j].strip()
                j += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(t)}</li>" for t in items) + f"</{tag}>"); i = j; continue
        j = i; buf = []
        while j < len(L) and L[j].strip() and not re.match(r"(#|\||- |\d+\. |```|> |<)", L[j]): buf.append(L[j]); j += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>"); i = j
    return "\n".join(out)


def render():
    """(README text, full report text, page HTML), all computed from results/ and the templates."""
    s = json.load(open(os.path.join(RES, "summary.json")))
    F = facts(s); T = tables_md(s)
    readme = fill(open(README_TEMPLATE).read(), F, T, "readme").strip() + "\n"
    up = lambda m: m.group(0) if re.match(r"https?:|#|mailto:", m.group(2)) else f"{m.group(1)}(../{m.group(2)})"
    report = re.sub(r"(\]|!\[[^\]]*\])\(([^)\s]+)\)", up, fill(open(TEMPLATE).read(), F, T, "readme").strip() + "\n")  # it lives in docs/
    W = pagew.widgets(s, need)
    body = fill(open(PAGE_TEMPLATE).read(), Facts({**F, **{"w_" + k: v for k, v in W.items()}}), T, "page")
    shell = open(os.path.join(PAGE_DIR, "shell.html")).read()
    page = shell.replace("__CSS__", open(os.path.join(PAGE_DIR, "style.css")).read().strip()).replace("__BODY__", body).replace("__JS__", open(os.path.join(PAGE_DIR, "sort.js")).read().strip())
    return readme, report, page


def main():
    readme, report, page = render()
    open(README, "w").write(readme); open(REPORT, "w").write(report)
    os.makedirs(os.path.dirname(PAGE), exist_ok=True); open(PAGE, "w").write(page)
    print(f"report -> README.md ({len(readme):,} chars), docs/REPORT.md ({len(report):,} chars), {os.path.relpath(PAGE, ROOT)} ({len(page):,} chars)")


if __name__ == "__main__":
    main()
