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


def scatter(pts, fr, X, Y, xt, yt, xlab, ylab, corner, labels, W=560, H=380, L=84, R=16, T=14, B=322, extra=""):
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
    g.append(f'<path d="{fr}" fill="none" stroke="var(--frontier)" stroke-width="4" stroke-dasharray="9 6" stroke-linejoin="round"/>' + extra)
    for p in pts:
        px, py, col = X(p["x"]), Y(p["y"]), p.get("col") or FAM(p["c"])
        if p["w"]:
            ax, lo, hi = p["w"]
            if ax == "x": g.append(f'<line x1="{X(lo):.1f}" x2="{X(hi):.1f}" y1="{py:.1f}" y2="{py:.1f}" stroke="{col}" stroke-width="2.5" stroke-opacity=".4"/>')
            else: g.append(f'<line x1="{px:.1f}" x2="{px:.1f}" y1="{Y(lo):.1f}" y2="{Y(hi):.1f}" stroke="{col}" stroke-width="2" stroke-opacity=".3"/>')
        if p["on"]: g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="12" fill="none" stroke="var(--frontier)" stroke-width="3"/>')
        fill = "var(--panel)" if p["hollow"] else col
        g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6.5" fill="{fill}" stroke="{col}" stroke-width="2.5"{' stroke-dasharray="3 2"' if p.get("dash") else ""}><title>{esc(p["tip"])}</title></circle>')
        dx, dy, a = labels.get(p["c"], (14, 4, "start"))
        g.append(f'<text x="{px + dx:.1f}" y="{py + dy:.1f}" text-anchor="{a}" class="lbl{" on" if p["on"] else ""}">{esc(p.get("name", p["c"]))}</text>')
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
    xt = [(v, f"${v:g}") for v in (1e-3, 2e-3, 5e-3, 1e-2, 2e-2)]
    yt = [(v / 100, f"{v}%") for v in (60, 70, 80, 90, 100)]
    lab = {"luna-low": (12, 16, "start"), "luna-medium": (12, -8, "start"), "luna-high": (12, 14, "start"), "haiku-low": (-14, 16, "end"),
           "haiku-medium": (14, 22, "start"), "sonnet-medium": (-16, 4, "end"), "sol61-medium": (0, 26, "middle")}
    return scatter(pts, d, X, Y, xt, yt, "$ per passing answer (log scale)", "pass rate", "↖ better", lab), [p["c"] for p in fr]


def speed_cost(s):
    """Median seconds (left is better, whisker p25–p75) against $ per pass, log (down is better). Frontier among configs
    that pass at least MIN_PASS; the rest are drawn but cannot be on it."""
    E = every(s); L, R, T, B, W = 84, 16, 14, 462, 560
    X = lambda v: L + (v - 3) / 27 * (W - R - L); Y = logscale(5e-4, 1e-1, B, T)
    pts = [{"c": c, "x": E[c]["latency_s"]["median"], "y": E[c]["usd_per_pass"], "hollow": c == "luna-high", "tip": tip(c, E[c]),
            "w": ("x", E[c]["latency_s"]["p25"], E[c]["latency_s"]["p75"]) if "p25" in E[c]["latency_s"] else None} for c in ORDER]
    ok = [p for p in pts if E[p["c"]]["pass_at_1"] >= MIN_PASS]
    fr = sorted(front(ok, lambda a, b: a["x"] <= b["x"] and a["y"] <= b["y"]), key=lambda p: p["x"])
    for p in pts: p["on"] = p in fr
    # Codex fast mode ran only in the pilot (other problems, every call passed, so $ per call = $ per pass): drawn dashed and
    # hollow, joined default → fast, never on the frontier.
    pf = s["pilot_fast"]; pil = []
    for k, v in pf.items():
        c, tier = k.split("/"); nm = f"{c} {'⚡' if tier == 'fast' else 'pilot'}"; short = "pilot" if k == "luna-low/default" else nm  # its ⚡ twin, joined by the line, names it
        pil.append({"c": k, "name": short, "x": v["median_s"], "y": v["usd_per_call"], "hollow": True, "dash": True, "on": False, "w": None, "col": "var(--codex)",
                    "tip": f"{nm}: pilot, {v['passes']}/{v['n']} passed, ${v['usd_per_call']:.5f} per call, median {v['median_s']:.1f} s"})
    ex = "".join(f'<line x1="{X(pf[c + "/default"]["median_s"]):.1f}" y1="{Y(pf[c + "/default"]["usd_per_call"]):.1f}" x2="{X(pf[c + "/fast"]["median_s"]):.1f}" '
                 f'y2="{Y(pf[c + "/fast"]["usd_per_call"]):.1f}" stroke="var(--codex)" stroke-width="2" stroke-dasharray="4 3" stroke-opacity=".6"/>' for c in dict.fromkeys(k.split("/")[0] for k in pf))
    d = f"M{X(fr[0]['x']):.1f} {Y(fr[0]['y']):.1f}" + "".join(f" H{X(p['x']):.1f} V{Y(p['y']):.1f}" for p in fr[1:]) + f" H{W - R}"
    xt = [(v, f"{v} s") for v in (5, 10, 15, 20, 25)]
    yt = [(v, f"${v:g}") for v in (1e-3, 3e-3, 1e-2, 3e-2, 1e-1)]
    lab = {"luna-low/default": (-8, 26, "start"), "luna-low/fast": (14, 5, "start"), "sol61-low/default": (14, 5, "start"), "sol61-low/fast": (14, 5, "start"),
           "luna-low": (0, -14, "middle"), "luna-medium": (14, 10, "start"), "haiku-low": (0, -20, "middle"), "luna-high": (14, -10, "start"),
           "haiku-medium": (14, -8, "start"), "sonnet-medium": (14, 4, "start"), "sol61-medium": (-14, -12, "end")}
    g = scatter(pts + pil, d, X, Y, xt, yt, "median seconds per call (bar: middle half of calls)", "$ per pass (log)", "", lab, H=520, B=B, extra=ex)
    return g.replace("</svg>", f'<text x="{W - R - 6}" y="{T + 18}" text-anchor="end" class="better">↙ better</text></svg>'), [p["c"] for p in fr]


# Display names for hard-set rows, used by every chart and table so a pipeline reads the same everywhere. luna-high on the hard
# set is the stripped harness (luna-high-bare); the name says so. Haiku in a pipeline reviews the answer and rewrites it if wrong.
NAME = {"luna-low": "luna-low", "luna-high-bare": "luna-high-bare", "haiku-low": "haiku-low", "haiku-medium": "haiku-medium",
        "sonnet-medium": "sonnet-medium", "sol61-medium": "sol61-medium",
        "luna-low+haiku-review-all": "luna-low → Haiku fixes all", "luna-low+haiku-on-fail": "luna-low → Haiku if samples fail",
        "luna-high-bare+haiku-review-all": "luna-high-bare → Haiku fixes all", "luna-high-bare+haiku-on-fail": "luna-high-bare → Haiku if samples fail",
        "luna-high-bare+retry-on-fail": "luna-high-bare → retry if samples fail",
        "haiku-low-plan+luna-low": "Haiku plan → luna-low", "haiku-low-plan+luna-high-bare": "Haiku plan → luna-high-bare"}
# Hard-set points: every row of the results table except the plan-first pipelines (in the table, not plotted).
HARD_PTS = [(c, n) for c, n in NAME.items() if not c.startswith("haiku-low-plan")]
SHORT = lambda n: n.replace("luna-", "").replace(" → Haiku if samples fail", "→H fail").replace(" → Haiku fixes all", "→H all").replace(" → retry if samples fail", "→retry")


def hard_pts():
    a = luna_rescue.arms()
    return [{"c": c, "name": SHORT(n) if "→" in n else n, "col": "var(--frontier)" if "→" in n else FAM(c), "hollow": False, "w": None, "k": a[c]["passes"] / a[c]["n"],
             "usd": a[c]["usd_per_pass"], "sec": a[c]["median_s"],
             "tip": f"{n}: {a[c]['passes']}/{a[c]['n']} passed, ${a[c]['usd_per_pass']:.5f} per pass, median {a[c]['median_s']:.1f} s"} for c, n in HARD_PTS]


def hard_pass_cost():
    """Hard set: pass rate against $ per pass (log), single models and the Haiku pipelines; no intervals (n is small and post hoc)."""
    L, R, T, B, W = 84, 16, 14, 382, 560
    X = logscale(5e-4, 3e-2, L, W - R); Y = lambda v: B - (v - 0.84) / 0.18 * (B - T)
    pts = [dict(p, x=p["usd"], y=p["k"]) for p in hard_pts() if p["k"] >= 0.84]; off = [p for p in hard_pts() if p["k"] < 0.84]
    fr = sorted(front(pts, lambda a, b: a["x"] <= b["x"] and a["y"] >= b["y"]), key=lambda p: p["x"])
    for p in pts: p["on"] = p in fr
    d = f"M{X(fr[0]['x']):.1f} {B} V{Y(fr[0]['y']):.1f}" + "".join(f" H{X(p['x']):.1f} V{Y(p['y']):.1f}" for p in fr[1:]) + f" H{W - R}"
    xt = [(v, f"${v:g}") for v in (1e-3, 2e-3, 5e-3, 1e-2, 2e-2)]
    yt = [(v / 100, f"{v}%") for v in (85, 90, 95, 100)]
    lab = {"luna-high-bare": (14, 20, "start"), "haiku-low": (14, 5, "start"), "haiku-medium": (0, -16, "middle"),
           "sonnet-medium": (0, -14, "middle"), "sol61-medium": (0, 24, "middle"), "luna-high-bare+retry-on-fail": (-14, 5, "end"),
           "luna-high-bare+haiku-on-fail": (0, 24, "middle"), "luna-low+haiku-on-fail": (-14, 5, "end"),
           "luna-low+haiku-review-all": (14, 5, "start"), "luna-high-bare+haiku-review-all": (0, 22, "middle")}
    g = scatter(pts, d, X, Y, xt, yt, "$ per passing answer (log scale)", "pass rate", "↖ better", lab, H=440, B=B)
    note = "".join(f'<text x="{W - R}" y="{B - 10}" text-anchor="end" class="axis">below the chart: {esc(p["name"])} {100 * p["k"]:.0f}%</text>' for p in off)
    return g.replace("</svg>", note + "</svg>"), [p["c"] for p in fr]


def hard_speed_cost():
    """Hard set: median seconds against $ per pass (log); frontier among rows passing at least MIN_PASS."""
    L, R, T, B, W = 84, 16, 14, 462, 560
    X = lambda v: L + (v - 6) / 22 * (W - R - L); Y = logscale(8e-4, 2.5e-2, B, T)
    pts = [dict(p, x=p["sec"], y=p["usd"]) for p in hard_pts()]
    ok = [p for p in pts if p["k"] >= MIN_PASS]
    fr = sorted(front(ok, lambda a, b: a["x"] <= b["x"] and a["y"] <= b["y"]), key=lambda p: p["x"])
    for p in pts: p["on"] = p in fr
    d = f"M{X(fr[0]['x']):.1f} {Y(fr[0]['y']):.1f}" + "".join(f" H{X(p['x']):.1f} V{Y(p['y']):.1f}" for p in fr[1:]) + f" H{W - R}"
    xt = [(v, f"{v} s") for v in (10, 15, 20, 25)]
    yt = [(v, f"${v:g}") for v in (1e-3, 2e-3, 5e-3, 1e-2, 2e-2)]
    lab = {"luna-low": (-12, 5, "end"), "luna-high-bare": (14, 5, "start"), "haiku-low": (14, 1, "start"), "haiku-medium": (14, 5, "start"),
           "sonnet-medium": (14, 5, "start"), "sol61-medium": (-14, 4, "end"), "luna-high-bare+retry-on-fail": (-20, 28, "middle"),
           "luna-high-bare+haiku-on-fail": (12, 6, "start"), "luna-low+haiku-on-fail": (0, -16, "middle"),
           "luna-low+haiku-review-all": (0, -14, "middle"), "luna-high-bare+haiku-review-all": (-14, 5, "end")}
    g = scatter(pts, d, X, Y, xt, yt, "median seconds per call", "$ per pass (log)", "", lab, H=520, B=B)  # corner label goes top right: the bottom left is crowded
    return g.replace("</svg>", f'<text x="{W - R - 6}" y="{T + 18}" text-anchor="end" class="better">↙ better</text></svg>'), [p["c"] for p in fr]


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
    """Hard set: single models next to the Haiku review and repair pipelines (plan-first rows are in the results table)."""
    a = luna_rescue.arms()
    bars = [(c, SHORT(NAME[c]) if "→" in NAME[c] else NAME[c], "var(--frontier)" if "→" in NAME[c] else FAM(c))
            for c in ("luna-low", "luna-high-bare", "haiku-low", "luna-low+haiku-on-fail", "luna-high-bare+haiku-on-fail",
                      "luna-low+haiku-review-all", "luna-high-bare+haiku-review-all", "haiku-medium", "sonnet-medium")]
    W, BL, BR, H = 560, 150, 360, 16 + 40 * len(bars)
    g = [f'<svg viewBox="0 0 {W} {H}" width="100%" {NS} role="img" aria-label="Passes on the hard set: single models and the Haiku review and repair pipelines">']
    for i, (c, name, col) in enumerate(bars):
        v = a[c]; y = 8 + i * 40; w = v["passes"] / v["n"] * (BR - BL)
        g.append(f'<text x="{BL - 10}" y="{y + 19}" text-anchor="end" class="lbl">{esc(name)}</text>')
        g.append(f'<rect x="{BL}" y="{y}" width="{BR - BL}" height="28" rx="3" fill="var(--line)"/>')
        g.append(f'<rect x="{BL}" y="{y}" width="{w:.1f}" height="28" rx="3" fill="{col}"/>')
        g.append(f'<text x="{BR + 8}" y="{y + 19}" class="lbl">{v["passes"]}/{v["n"]} · ${v["usd_per_pass"]:.4f} · {v["median_s"]:.0f}s</text>')
    g.append("</svg>")
    return "".join(g)


def fast(s):
    """Codex fast mode against the default tier on the pilot problems: median seconds per call, $ per call."""
    f = s["pilot_fast"]; mx = max(v["median_s"] for v in f.values())
    W, BL, BR, H = 560, 190, 370, 16 + 40 * len(f)
    g = [f'<svg viewBox="0 0 {W} {H}" width="100%" {NS} role="img" aria-label="Median seconds per call, Codex default tier against fast mode">']
    for i, (k, v) in enumerate(f.items()):
        c, tier = k.split("/"); y = 8 + i * 40; w = v["median_s"] / mx * (BR - BL)
        g.append(f'<text x="{BL - 10}" y="{y + 19}" text-anchor="end" class="lbl">{esc(c)} {"⚡ fast" if tier == "fast" else "default"}</text>')
        g.append(f'<rect x="{BL}" y="{y}" width="{BR - BL}" height="28" rx="3" fill="var(--line)"/>')
        g.append(f'<rect x="{BL}" y="{y}" width="{w:.1f}" height="28" rx="3" fill="{"var(--frontier)" if tier == "fast" else "var(--codex)"}"/>')
        g.append(f'<text x="{BR + 8}" y="{y + 19}" class="lbl">{v["median_s"]:.1f}s · ${v["usd_per_call"]:.4f}</text>')
    g.append("</svg>")
    return "".join(g)


def explorer(s):
    """The pick-your-axes scatter (docs/page/explorer.html) with every config's numbers injected."""
    data = [{"c": c, "exp": e, "col": FAMILY(c), "kind": v["cost_kind"], "pass": v["pass_at_1"], "usd": v["usd_per_pass"],
             "med": v["latency_s"]["median"], "inp": v["tokens_mean"]["in_tok"], "rsn": v["tokens_mean"]["reasoning_tok"]}
            for e, group in ((False, s["configs"]), (True, s["exploratory"])) for c, v in group.items()]
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "page", "explorer.html")
    return open(src).read().replace("__DATA__", json.dumps(data, separators=(",", ":")))


def verdict(c, v, need, E):
    """One word per config; each is checked against the data so the table cannot drift from it."""
    if c == "haiku-medium":
        need(v["passes"] == v["n"] - 1 and luna_rescue.arms()[c]["passes"] == luna_rescue.arms()[c]["n"], "haiku-medium: one miss, none on the hard set")
        return "★ pick"
    if c == "haiku-low":
        need(v["usd_per_pass"] == min(E[d]["usd_per_pass"] for d in ORDER if E[d]["pass_at_1"] >= 0.95), "haiku-low is the cheapest at 95%+")
        return "budget pick"
    if v["passes"] == v["n"]: return "0 misses"
    if v["pass_at_1"] < MIN_PASS: return "avoid"
    dominated = any(d != c and E[d]["usd_per_pass"] <= v["usd_per_pass"] and E[d]["pass_at_1"] >= v["pass_at_1"] for d in ORDER)
    return "beaten" if dominated else "pricier, passes more"


# Hard-set rows for the results table: single models, then pipelines (arrow = a second model or call after the first).
HARD = list(NAME.items())


def row(name, col, k, n, usd, sec, verdict, proxy=False):
    r = k / n; cls = "good" if r >= 0.95 else "warn" if r >= MIN_PASS else "bad"
    return (f'<tr><td><span class="dot" style="background:{col}"></span>{esc(name)}</td><td><span class="pill {cls}">{100 * r:.0f}% ({k}/{n})</span></td>'
            f'<td>{"~" if proxy else ""}${usd:.5f}</td><td>{sec:.1f}</td><td>{verdict}</td></tr>')


def short_table(s, need):
    """One table, two groups that sort separately: every config on all problems, then single models and pipelines on the hard
    set. Passed reads "95% (57/60)" so it sorts by rate. Hard-set verdicts come from the numbers: never failed, the cheapest of
    those, or how many attempts missed."""
    E = every(s); a = luna_rescue.arms()
    top = [row(c, FAM(c), E[c]["passes"], E[c]["n"], E[c]["usd_per_pass"], E[c]["latency_s"]["median"], verdict(c, E[c], need, E),
               E[c]["cost_kind"] == "proxy") for c in ORDER]
    clean = [c for c, _ in HARD if a[c]["passes"] == a[c]["n"]]; need(clean, "some hard-set row never failed")
    best = min(clean, key=lambda c: a[c]["usd_per_pass"])
    need(best == "haiku-medium", "haiku-medium is the cheapest hard-set row with no miss")
    hv = lambda c: "0 misses, cheapest" if c == best else "0 misses" if c in clean else f"missed {a[c]['n'] - a[c]['passes']}"
    hard = [row(name, "var(--frontier)" if "→" in name else FAM(c), a[c]["passes"], a[c]["n"], a[c]["usd_per_pass"], a[c]["median_s"], hv(c),
                "luna" in c or "sol61" in c) for c, name in HARD]
    grp = lambda t: f'<tr class="grp"><th colspan="5">{t}</th></tr>'
    return ('<div class="tablewrap"><table class="sortable"><thead><tr><th>config</th><th>passed</th><th>$ per pass</th>'
            '<th>median s</th><th>verdict</th></tr></thead>'
            f'<tbody>{grp("All problems")}{"".join(top)}</tbody>'
            f'<tbody>{grp(f"Hard set: {a[HARD[0][0]]["n"]} attempts on {len(luna_rescue.PIDS)} problems chosen after round 1")}{"".join(hard)}</tbody></table></div>')


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
    a, fa = pass_cost(s); b, fb = speed_cost(s); ha, hfa = hard_pass_cost(); hb, hfb = hard_speed_cost(); nm = dict(HARD_PTS)
    return {"pass_cost": a, "speed_cost": b, "hard_pass_cost": ha, "hard_speed_cost": hb,
            "hard_front_pass": ", ".join(nm[c] for c in hfa), "hard_front_speed": ", ".join(nm[c] for c in hfb), "grid": grid(s), "floor": floor(s), "pipes": pipes(), "fast": fast(s), "explorer": explorer(s), "short_table": short_table(s, need),
            "front_pass": ", ".join(fa), "front_speed": ", ".join(fb),
            "problems": method(s)[0], "flags": method(s)[1]}
