"""Widgets for the page (results/report/page.html), all drawn from results/summary.json: the two Pareto scatters, the
problem × config grid, the token-floor bars and the short result table. Inline SVG and HTML that take their colours
from the page's CSS variables, so both themes work. Standard library only."""
import html, json, math, os

from analysis import luna_rescue
from analysis.charts import FAMILY, MIN_PASS

# Plot order and family colour (a CSS variable of the page). luna-high is the exploratory full-ladder run.
ORDER = ["haiku-low", "haiku-medium", "sonnet-medium", "sol61-medium", "luna-high", "luna-medium", "luna-low"]
FAM = lambda c: "var(--claude)" if c.startswith("haiku") else "var(--sonnet)" if c.startswith("sonnet") else "var(--codex)"
NS = 'xmlns="http://www.w3.org/2000/svg"'


def every(s):
    return {**s["configs"], **s["exploratory"]}


def front(pts, better):
    """Points no other point beats on both axes. better(a, b) is True when a is at least as good as b on both."""
    return [p for p in pts if not any(q is not p and better(q, p) and (q["x"], q["y"]) != (p["x"], p["y"]) for q in pts)]


def esc(t):
    return html.escape(str(t))


def scatter(pts, fr, X, Y, xt, yt, xlab, ylab, corner, labels, W=560, H=380, L=84, R=16, T=14, B=322):
    """pts: dicts with c, x, y, w (whisker (axis, lo, hi) or None), tip, hollow. fr: frontier points in step order,
    each step already a list of (x, y) pixel vertices."""
    g = [f'<svg viewBox="0 0 {W} {H}" width="100%" {NS} role="img" aria-label="{esc(ylab)} against {esc(xlab)}, Pareto frontier in purple">']
    for v, t in xt:
        g.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{B}" stroke="var(--line)"/><text x="{X(v):.1f}" y="{B + 18}" text-anchor="middle" class="axis">{t}</text>')
    for v, t in yt:
        g.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--line)"/><text x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end" class="axis">{t}</text>')
    g.append(f'<text x="{(L + W - R) / 2}" y="{H - 14}" text-anchor="middle" class="axis">{esc(xlab)}</text>')
    g.append(f'<text x="16" y="{(T + B) / 2}" text-anchor="middle" class="axis" transform="rotate(-90 16 {(T + B) / 2})">{esc(ylab)}</text>')
    g.append(f'<text x="{L + 10}" y="{T + 18 if corner.startswith("↖") else B - 10}" class="better">{corner}</text>')
    g.append(f'<path d="{fr}" fill="none" stroke="var(--frontier)" stroke-width="4" stroke-dasharray="9 6" stroke-linejoin="round"/>')
    for p in pts:
        px, py, col = X(p["x"]), Y(p["y"]), FAM(p["c"])
        if p["w"]:
            ax, lo, hi = p["w"]
            if ax == "x": g.append(f'<line x1="{X(lo):.1f}" x2="{X(hi):.1f}" y1="{py:.1f}" y2="{py:.1f}" stroke="{col}" stroke-width="2.5" stroke-opacity=".4"/>')
            else: g.append(f'<line x1="{px:.1f}" x2="{px:.1f}" y1="{Y(lo):.1f}" y2="{Y(hi):.1f}" stroke="{col}" stroke-width="2" stroke-opacity=".3"/>')
        if p["on"]: g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="12" fill="none" stroke="var(--frontier)" stroke-width="3"/>')
        fill = "var(--panel)" if p["hollow"] else col
        g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6.5" fill="{fill}" stroke="{col}" stroke-width="2.5"><title>{esc(p["tip"])}</title></circle>')
        dx, dy, a = labels.get(p["c"], (14, 4, "start"))
        g.append(f'<text x="{px + dx:.1f}" y="{py + dy:.1f}" text-anchor="{a}" class="lbl{" on" if p["on"] else ""}">{esc(p["c"])}</text>')
    g.append("</svg>")
    return "".join(g)


def logscale(lo, hi, a, b):
    return lambda v: a + (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (b - a)


def tip(c, v):
    k = " (exploratory)" if c == "luna-high" else ""
    return (f"{c}{k}: {v['passes']}/{v['n']} passed, ${v['usd_per_pass']:.5f} per pass ({v['cost_kind']}), "
            f"median {v['latency_s']['median']:.1f} s")


def pass_cost(s):
    """Pass rate (up is better) against $ per pass, log (left is better). Whiskers: 95% CI of the pass rate."""
    E = every(s); L, R, T, B, W = 84, 16, 14, 322, 560
    X = logscale(5e-4, 3e-2, L, W - R); Y = lambda v: B - (v - 0.6) / 0.4 * (B - T)
    pts = [{"c": c, "x": E[c]["usd_per_pass"], "y": E[c]["pass_at_1"], "hollow": c == "luna-high", "tip": tip(c, E[c]),
            "w": ("y", max(0.6, E[c]["ci95"][0]), E[c]["ci95"][1])} for c in ORDER]
    fr = sorted(front(pts, lambda a, b: a["x"] <= b["x"] and a["y"] >= b["y"]), key=lambda p: p["x"])
    for p in pts: p["on"] = p in fr
    d = f"M{X(fr[0]['x']):.1f} {B} V{Y(fr[0]['y']):.1f}" + "".join(f" H{X(p['x']):.1f} V{Y(p['y']):.1f}" for p in fr[1:]) + f" H{W - R}"
    xt = [(v, f"${v:g}") for v in (5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2)]
    yt = [(v / 100, f"{v}%") for v in (60, 70, 80, 90, 100)]
    lab = {"luna-low": (12, 16, "start"), "luna-medium": (12, -8, "start"), "luna-high": (12, 14, "start"), "haiku-low": (-14, -6, "end"),
           "haiku-medium": (14, 4, "start"), "sonnet-medium": (-16, 4, "end"), "sol61-medium": (-16, 4, "end")}
    return scatter(pts, d, X, Y, xt, yt, "$ per passing answer (log scale)", "pass rate", "↖ better", lab), [p["c"] for p in fr]


def speed_cost(s):
    """Median seconds (left is better, whisker p25–p75) against $ per pass, log (down is better). Frontier among configs
    that pass at least MIN_PASS; the rest are drawn but cannot be on it."""
    E = every(s); L, R, T, B, W = 84, 16, 14, 322, 560
    X = lambda v: L + (v - 4) / 26 * (W - R - L); Y = logscale(2.5e-4, 3e-2, B, T)
    pts = [{"c": c, "x": E[c]["latency_s"]["median"], "y": E[c]["usd_per_pass"], "hollow": c == "luna-high", "tip": tip(c, E[c]),
            "w": ("x", E[c]["latency_s"]["p25"], E[c]["latency_s"]["p75"]) if "p25" in E[c]["latency_s"] else None} for c in ORDER]
    ok = [p for p in pts if E[p["c"]]["pass_at_1"] >= MIN_PASS]
    fr = sorted(front(ok, lambda a, b: a["x"] <= b["x"] and a["y"] <= b["y"]), key=lambda p: p["x"])
    for p in pts: p["on"] = p in fr
    d = f"M{X(fr[0]['x']):.1f} {Y(fr[0]['y']):.1f}" + "".join(f" H{X(p['x']):.1f} V{Y(p['y']):.1f}" for p in fr[1:]) + f" H{W - R}"
    xt = [(v, f"{v} s") for v in (5, 10, 15, 20, 25, 30)]
    yt = [(v, f"${v:g}") for v in (5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2)]
    lab = {"luna-low": (-10, 20, "end"), "luna-medium": (8, 22, "start"), "haiku-low": (-14, -10, "end"), "luna-high": (6, 24, "start"),
           "haiku-medium": (14, -8, "start"), "sonnet-medium": (14, 4, "start"), "sol61-medium": (-14, -12, "end")}
    return scatter(pts, d, X, Y, xt, yt, "median seconds per call (bar: middle half of calls)", "$ per pass (log)", "↙ better", lab), [p["c"] for p in fr]


def grid(s):
    """Problems (rows, by rung) × configs (columns); each cell is passes out of the attempts at that problem."""
    E = every(s); probs = sorted(s["problems"], key=lambda p: (s["problems"][p]["rung"], p))
    def cell(p, c):
        if c in s["problems"][p]: return s["problems"][p][c], E[c]["n"] // len(probs)
        f = s["failures"].get(p, {}).get("cells", {}).get(c)
        return (f["passed"], f["n"]) if f else (E[c]["n"] // len(probs),) * 2  # absent from failures: every attempt passed
    out = [f'<div class="grid" style="grid-template-columns:minmax(84px,auto) repeat({len(ORDER)},minmax(40px,1fr))">', '<div class="h m">problem</div>']
    out += [f'<div class="h">{esc(c)}</div>' for c in ORDER]
    for p in probs:
        out.append(f'<div class="m">{p[:3]} <span class="rung">L{s["problems"][p]["rung"]}</span>'
                   f'<span class="lc {LC[p].lower()}" title="LeetCode level, my estimate">{LC[p][0]}</span></div>')
        for c in ORDER:
            k, n = cell(p, c); cls = "pass" if k == n else "part" if k * 2 > n else "fail"
            out.append(f'<div class="{cls}" title="{esc(c)} on {p}: {k} of {n} passed">{k}/{n}</div>')
    out.append("</div>")
    return "".join(out)


def floor(s):
    """Mean input tokens per call; the darker part was served from the prompt cache."""
    E = every(s)
    bars = [("haiku-low", "haiku-low, tools off"), ("sonnet-medium", "sonnet-medium, tools off"),
            ("luna-low", "luna-low, stock Codex"), ("luna-low-bare", "luna-low, stripped"), ("sol61-medium", "sol61-medium, stock")]
    W, BL, BR, H = 560, 210, 496, 30 + 40 * len(bars); top = max(E[c]["tokens_mean"]["in_tok"] for c, _ in bars)
    g = [f'<svg viewBox="0 0 {W} {H}" width="100%" {NS} role="img" aria-label="Mean input tokens per call by config">']
    for i, (c, name) in enumerate(bars):
        t = E[c]["tokens_mean"]; y = 8 + i * 40; w = t["in_tok"] / top * (BR - BL); cw = t["cached_tok"] / top * (BR - BL)
        g.append(f'<text x="{BL - 10}" y="{y + 19}" text-anchor="end" class="lbl">{esc(name)}</text>')
        g.append(f'<rect x="{BL}" y="{y}" width="{w:.1f}" height="28" rx="3" fill="{FAM(c)}" fill-opacity=".35"/>')
        g.append(f'<rect x="{BL}" y="{y}" width="{cw:.1f}" height="28" rx="3" fill="{FAM(c)}" fill-opacity=".9"/>')
        g.append(f'<text x="{BL + w + 8:.1f}" y="{y + 19}" class="lbl">{t["in_tok"] / 1000:.1f}k</text>')
    g.append(f'<text x="{BL}" y="{H - 4}" class="axis">solid = served from cache · faded = uncached</text></svg>')
    return "".join(g)


def pipes():
    """Hard set, 35 attempts each: single models next to the luna-low → haiku-low repair pipeline."""
    a = luna_rescue.arms()
    bars = [("luna-low", "luna-low alone", "var(--codex)"), ("luna-high-bare", "luna-high alone", "var(--codex)"),
            ("haiku-low", "haiku-low alone", "var(--claude)"),
            ("haiku-low-plan+luna-low", "Haiku plan → luna-low", "var(--frontier)"), ("haiku-low-plan+luna-high-bare", "Haiku plan → luna-high", "var(--frontier)"),
            ("luna-low+haiku-low-repair", "luna-low → Haiku repair", "var(--frontier)"),
            ("sonnet-medium", "sonnet-medium alone", "var(--sonnet)")]
    W, BL, BR, H = 560, 190, 370, 16 + 40 * len(bars)
    g = [f'<svg viewBox="0 0 {W} {H}" width="100%" {NS} role="img" aria-label="Passes on the hard set: single models, Haiku-plan pipelines and the Haiku-repair pipeline">']
    for i, (c, name, col) in enumerate(bars):
        v = a[c]; y = 8 + i * 40; w = v["passes"] / v["n"] * (BR - BL)
        g.append(f'<text x="{BL - 10}" y="{y + 19}" text-anchor="end" class="lbl">{esc(name)}</text>')
        g.append(f'<rect x="{BL}" y="{y}" width="{BR - BL}" height="28" rx="3" fill="var(--line)"/>')
        g.append(f'<rect x="{BL}" y="{y}" width="{w:.1f}" height="28" rx="3" fill="{col}"/>')
        g.append(f'<text x="{BR + 8}" y="{y + 19}" class="lbl">{v["passes"]}/{v["n"]} · ${v["usd_per_pass"]:.4f} · {v["median_s"]:.0f}s</text>')
    g.append("</svg>")
    return "".join(g)


def explorer(s):
    """The pick-your-axes scatter (docs/page/explorer.html) with every config's numbers injected."""
    data = [{"c": c, "exp": e, "col": FAMILY(c), "kind": v["cost_kind"], "pass": v["pass_at_1"], "usd": v["usd_per_pass"],
             "med": v["latency_s"]["median"], "inp": v["tokens_mean"]["in_tok"], "rsn": v["tokens_mean"]["reasoning_tok"]}
            for e, group in ((False, s["configs"]), (True, s["exploratory"])) for c, v in group.items()]
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "page", "explorer.html")
    return open(src).read().replace("__DATA__", json.dumps(data, separators=(",", ":")))


def verdict(c, v, need):
    """One word per config; each is checked against the data so the table cannot drift from it."""
    if c == "haiku-low": need(v["pass_at_1"] >= MIN_PASS, "haiku-low clears the pass bar"); return "default · repair"
    if c == "luna-high": need(v["pass_at_1"] >= MIN_PASS, "luna-high clears the pass bar"); return "build"
    if v["passes"] == v["n"]: return "never failed"
    if v["pass_at_1"] < MIN_PASS: return "avoid"
    return "no gain"


def short_table(s, need):
    """Config, passed (pill coloured by rate), $ per pass, median seconds, verdict. Sortable by the page script."""
    E = every(s)
    rows = []
    for c in ORDER:
        v = E[c]; r = v["pass_at_1"]; cls = "good" if r >= 0.95 else "warn" if r >= MIN_PASS else "bad"
        rows.append(f'<tr><td><span class="dot" style="background:{FAM(c)}"></span>{esc(c)}</td><td><span class="pill {cls}">{v["passes"]}/{v["n"]}</span></td>'
                    f'<td>{"~" if v["cost_kind"] == "proxy" else ""}${v["usd_per_pass"]:.5f}</td><td>{v["latency_s"]["median"]:.1f}</td><td>{verdict(c, v, need)}</td></tr>')
    return ('<div class="tablewrap"><table class="sortable"><thead><tr><th>config</th><th>passed</th><th>$ per pass</th>'
            '<th>median seconds</th><th>verdict</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")


# What each problem tests, one line each, for the visible method list. Links go to the problem file in the repo.
REPO = "https://github.com/chimera-defi/model-routing-bench/blob/main/bench/problems/"
TESTS = {
    "p01_overlap_minutes": "minutes with at least k meetings at once; half-open intervals, sweep line",
    "p02_squash": "run-length encoding with escaped digits and backslashes",
    "p03_ledger": "bank operations with validation rules, frozen accounts and transfers",
    "p04_taller_within": "count taller people among the k in front; sliding window",
    "p05_pass_route": "cheapest route when zone passes can be bought on the way; state-space shortest path",
    "p06_calc": "integer expression parser: precedence, right-assoc power, unary minus, errors",
    "p07_weighted_distance_sums": "weighted distance sums from every tree node; rerooting",
    "p08_recur": "calendar recurrence rules (daily, weekly, monthly) expanded to dates",
    "p09_k_machine_schedule": "best total pay for jobs on k printers; weighted interval scheduling",
    "p10_avoid_count": "count strings avoiding banned substrings; automaton DP, modulo",
    "p11_best_average": "largest average of a subarray of length at least k, as an exact fraction",
    "p12_sheet": "spreadsheet evaluator with references, ranges, division and cycle errors",
    "p13_xor_ring": "XOR cellular automaton on a ring for huge t; doubling",
    "p14_bounce_board": "expected turns on a bouncing board game with jumps, as an exact fraction",
    "p15_paint_erase": "paint and erase ranges where higher colours win; segment tree",
}


# Closest LeetCode difficulty for each new problem: my estimate from the nearest LeetCode analogue, not a measurement.
LC = {"p01_overlap_minutes": "Medium", "p02_squash": "Easy", "p03_ledger": "Medium", "p04_taller_within": "Medium",
      "p05_pass_route": "Medium", "p06_calc": "Hard", "p07_weighted_distance_sums": "Hard", "p08_recur": "Medium",
      "p09_k_machine_schedule": "Hard", "p10_avoid_count": "Hard", "p11_best_average": "Hard", "p12_sheet": "Hard",
      "p13_xor_ring": "Hard", "p14_bounce_board": "Hard", "p15_paint_erase": "Hard"}
# The pilot's well-known LeetCode problems, in the order the pilot ran them (round 1, then the harder round 2).
PILOT = [("Fizz Buzz", "fizz-buzz", "Easy"), ("Course Schedule II", "course-schedule-ii", "Medium"), ("Candy", "candy", "Hard"),
         ("Reconstruct Itinerary", "reconstruct-itinerary", "Hard"), ("Minimum Window Substring", "minimum-window-substring", "Hard"),
         ("Wildcard Matching", "wildcard-matching", "Hard")]


def method(s):
    from bench.run import CLAUDE_FLAGS, CODEX_FLAGS
    lvl = lambda d: f'<span class="lc {d.lower()}">{d}</span>'
    item = lambda p, r: f'<li>{lvl(LC[p])} L{r} <a href="{REPO}{p}.py"><code>{p.split("_", 1)[1]}</code></a>: {esc(TESTS[p])}</li>'
    main = sorted(s["problems"], key=lambda p: (s["problems"][p]["rung"], p))
    hard = sorted({p for v in s["hard"].values() for p in v["by_problem"]})
    hcfg = ", ".join(c for c in ORDER if c in s["hard"])
    li = [f'<li class="round"><b>Pilot</b>: well-known LeetCode problems. Every config passed, so it ranked nothing and is not scored.<ul>'
          + "".join(f'<li>{lvl(d)} <a href="https://leetcode.com/problems/{slug}/">{esc(n)}</a></li>' for n, slug, d in PILOT) + "</ul></li>",
          f'<li class="round"><b>Round 1</b>: {len(main)} new problems on rungs L1–L6, every config.<ul>'
          + "".join(item(p, s["problems"][p]["rung"]) for p in main) + "</ul></li>",
          f'<li class="round"><b>Round 2</b>: {len(hard)} harder problems on rung L7, run later on {hcfg}.<ul>'
          + "".join(item(p, 7) for p in hard) + "</ul></li>"]
    flag = lambda fl: esc(" ".join(f if f else '""' for f in fl))
    group = {}
    for c, v in list(s["configs"].items()) + list(s["hard"].items()):
        if c in ORDER: group.setdefault((v["cli"], v["model"]), set()).add(v["effort"])
    eff = lambda e: "|".join(x for x in ["low", "medium", "high"] if x in e)
    cmds = [f'<li><code>claude -p --model {m} --effort {eff(e)} {flag(CLAUDE_FLAGS)}</code></li>' if cli == "claude" else
            f'<li><code>codex exec -m {m} -c model_reasoning_effort={eff(e)} {flag(CODEX_FLAGS)}</code></li>'
            for (cli, m), e in group.items()]
    return "".join(li), "".join(cmds)


def widgets(s, need):
    a, fa = pass_cost(s); b, fb = speed_cost(s)
    return {"pass_cost": a, "speed_cost": b, "grid": grid(s), "floor": floor(s), "pipes": pipes(), "explorer": explorer(s), "short_table": short_table(s, need),
            "front_pass": ", ".join(fa), "front_speed": ", ".join(fb),
            "problems": method(s)[0], "flags": method(s)[1]}
