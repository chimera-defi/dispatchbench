"""Draw the report charts as plain SVG from results/summary.json. Standard library only; no model calls."""
import json, math, os, re
from analysis import dataset
from analysis.labels import DISP, TESTS, plabel
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "report", "charts")
FONT = "font-family='Hanken Grotesk, -apple-system, Segoe UI, Helvetica, Arial, sans-serif'"
INK, MUTED, GRID, PLATE = "var(--fg,#1d2321)", "var(--muted,#5d6763)", "var(--line,#dde2de)", "var(--panel,#ffffff)"
HOST_AGENTS_MD = "1.3k"  # tokens of the host's ~/.codex/AGENTS.md, measured once by hand (bytes / 4); not in the result rows
BADC, WARNC = "var(--bad,#b3261e)", "var(--warn,#a86b00)"
FAMILY = lambda c: "var(--claude,#b4572e)" if c.startswith("haiku") else "var(--sonnet,#2f8f7d)" if c.startswith("sonnet") else "var(--codex,#3a5bb8)"


# Per-label vertical offsets so neighbouring points' labels do not collide.
LABEL_DY = {"luna-low": 18, "luna-low-bare": 18, "sol61-medium": 18, "sol56-high": 18}  # the 100% row holds three configs
LABEL_LEFT = {"haiku-low", "sonnet-medium"}  # left of the point, clear of luna-high and the 100% row


def svg(w, h, body):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' {FONT} font-size='12'>"
            f"<rect width='{w}' height='{h}' fill='{PLATE}'/>{''.join(body)}</svg>\n")


def text(x, y, s, size=12, anchor="start", fill=INK, weight="normal", rotate=None):
    t = f" transform='rotate({rotate} {x} {y})'" if rotate else ""
    return f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' style='fill:{fill}' font-weight='{weight}'{t}>{escape(str(s))}</text>"


def log_ticks(lo, hi):
    out = []
    for e in range(math.floor(math.log10(lo)), math.ceil(math.log10(hi)) + 1):
        for m in (1, 2, 5):
            v = m * 10 ** e
            if lo <= v <= hi: out.append(v)
    return out


def fmt_usd(v):
    return f"${v:.4f}".rstrip("0").rstrip(".") if v < 0.01 else f"${v:.3f}".rstrip("0").rstrip(".")


def pareto_chart(s):
    cfg = {c: v for c, v in s["configs"].items() if v["usd_per_pass"]}
    extra = {c: v for c, v in (s.get("exploratory") or {}).items() if v["usd_per_pass"]}  # exploratory, not on the pre-registered frontier
    allc = {**cfg, **extra}
    W, H, L, R, T, B = 760, 480, 96, 30, 50, 80
    xs = [v["usd_per_pass"] for v in allc.values()]
    x0, x1 = min(xs) / 1.6, max(xs) * 1.6; y0 = 0.6
    X = lambda v: L + (math.log(v) - math.log(x0)) / (math.log(x1) - math.log(x0)) * (W - L - R)
    Y = lambda p: H - B - (p - y0) / (1 - y0) * (H - T - B)
    b = [text(L, 24, "Pass rate vs cost per passing solution (main ladder p01-p12, x log)", 14, weight="600")]
    for p in (0.6, 0.7, 0.8, 0.9, 1.0):
        b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(p):.1f}' y2='{Y(p):.1f}' stroke='{GRID}'/>", text(L - 8, Y(p) + 4, f"{100 * p:.0f}%", 11, "end", MUTED)]
    for v in log_ticks(x0, x1):
        b += [f"<line x1='{X(v):.1f}' x2='{X(v):.1f}' y1='{T}' y2='{H - B}' stroke='{GRID}'/>", text(X(v), H - B + 18, fmt_usd(v), 11, "middle", MUTED)]
    b += [text((L + W - R) / 2, H - B + 38, "$ per passing call", 12, "middle", MUTED),
          text(26, (T + H - B) / 2, "pass@1 (12 problems × 5 attempts)", 12, "middle", MUTED, rotate=-90)]
    front = s["pareto"]
    if len(front) > 1:
        pts = " ".join(f"{X(cfg[c]['usd_per_pass']):.1f},{Y(cfg[c]['pass_at_1']):.1f}" for c in front)
        b.append(f"<polyline points='{pts}' fill='none' stroke='{INK}' stroke-width='1.5' stroke-dasharray='5 4'/>")
    for c, v in allc.items():
        x, y = X(v["usd_per_pass"]), Y(v["pass_at_1"]); on = c in front; hollow = "-fast" in c
        lo, hi = v["ci95"]
        col = FAMILY(c)
        b.append(f"<line x1='{x:.1f}' x2='{x:.1f}' y1='{Y(max(lo, y0)):.1f}' y2='{Y(hi):.1f}' stroke='{col}' stroke-width='2' opacity='0.35'/>")
        if hollow:
            b.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='5.5' fill='{PLATE}' stroke='{col}' stroke-width='2'/>")
        else:
            b.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{7 if on else 5.5}' fill='{col}' stroke='{INK if on else PLATE}' stroke-width='1.5'/>")
        right = x > W - R - 170 or c in LABEL_LEFT
        label = f"{DISP(c)} ({100 * v['pass_at_1']:.0f}%){' *' if v['cost_kind'] == 'proxy' else ''}{', exploratory' if c in extra else ''}"
        b.append(text(x - 10 if right else x + 10, y + LABEL_DY.get(c, -8), label, 11, "end" if right else "start", MUTED if hollow else INK))
    b.append(text(L, H - 10, "Dashed: Pareto. Bars: 95% CI. Solid: normal speed; hollow: fast mode. * Codex cost is proxy.", 10, fill=MUTED))
    return svg(W, H, b)


MIN_PASS = 0.90
PURPLE = "var(--frontier,#7b3fe4)"


def cost_time_chart(s):
    """$ per pass against median latency, function track L1-L6. The frontier is drawn over configs at or above MIN_PASS
    pass@1: among those, the ones no other config beats on both cost and time."""
    from analysis.page import speed_dominates
    allc = {**{c: v for c, v in s["configs"].items() if v["usd_per_pass"]}, **{c: v for c, v in (s.get("exploratory") or {}).items() if v["usd_per_pass"]}}
    pts = {c: (v["usd_per_pass"], v["latency_s"]["median"]) for c, v in allc.items()}
    ok = {c: p for c, p in pts.items() if allc[c]["pass_at_1"] >= MIN_PASS}
    front = [a for a, (x, y) in ok.items() if not any(speed_dominates({"x": y2, "y": x2}, {"x": y, "y": x}) for b, (x2, y2) in ok.items() if b != a)]
    front.sort(key=lambda c: pts[c][0])
    W, H, L, R, T, B = 760, 440, 96, 30, 50, 80
    xs = [p[0] for p in pts.values()]; x0, x1 = min(xs) / 1.6, max(xs) * 1.6
    y1 = math.ceil(max(p[1] for p in pts.values()) / 5) * 5 + 5
    X = lambda v: L + (math.log(v) - math.log(x0)) / (math.log(x1) - math.log(x0)) * (W - L - R)
    Y = lambda t: H - B - t / y1 * (H - T - B)
    b = [text(L, 24, "Cost per passing solution vs median latency (main ladder p01-p12, x log)", 14, weight="600")]
    for t in range(0, int(y1) + 1, 5):
        b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(t):.1f}' y2='{Y(t):.1f}' stroke='{GRID}'/>", text(L - 8, Y(t) + 4, f"{t} s", 11, "end", MUTED)]
    for v in log_ticks(x0, x1):
        b += [f"<line x1='{X(v):.1f}' x2='{X(v):.1f}' y1='{T}' y2='{H - B}' stroke='{GRID}'/>", text(X(v), H - B + 18, fmt_usd(v), 11, "middle", MUTED)]
    b += [text((L + W - R) / 2, H - B + 38, "$ per passing call", 12, "middle", MUTED),
          text(26, (T + H - B) / 2, "median seconds per call", 12, "middle", MUTED, rotate=-90)]
    if len(front) > 1:
        b.append(f"<polyline points='{' '.join(f'{X(pts[c][0]):.1f},{Y(pts[c][1]):.1f}' for c in front)}' fill='none' stroke='{PURPLE}' stroke-width='2.5' stroke-dasharray='6 4'/>")
    lanes = {}
    for c, (x, t) in sorted(pts.items(), key=lambda item: item[1][0]):
        hollow = "-fast" in c; px, py = X(x), Y(t)
        col = FAMILY(c)
        b.append(f"<circle cx='{px:.1f}' cy='{py:.1f}' r='6' fill='{PLATE if hollow else col}' stroke='{PURPLE if c in front else col if hollow else PLATE}' stroke-width='{3 if c in front else 2 if hollow else 1.5}'/>")
        lab = f"{DISP(c)} ({100 * allc[c]['pass_at_1']:.0f}%){' *' if allc[c]['cost_kind'] == 'proxy' else ''}"; w = 6.3 * len(lab)
        xl = px - 10 - w if px + 10 + w > W - R else px + 10
        lane = next(k for k in range(30) if all(abs(ly - (py - 12 - 16 * k)) >= 15 or e < xl - 6 or s0 > xl + w + 6 for s0, e, ly in lanes.setdefault(0, [])))
        ly = py - 12 - 16 * lane
        lanes[0].append((xl, xl + w, ly))
        if lane: b.append(f"<line x1='{px:.1f}' x2='{px:.1f}' y1='{py - 7:.1f}' y2='{ly + 3:.1f}' stroke='{col}' stroke-width='1' opacity='0.6'/>")
        b.append(text(xl, ly, lab, 11, fill=MUTED if hollow else INK))
    b.append(text(L, H - 10, f"Purple ring: frontier, pass@1 ≥ {100 * MIN_PASS:.0f}%, then cost and time. Solid: normal speed; hollow: fast mode. * Codex cost is proxy.", 10, fill=MUTED))
    return svg(W, H, b)


def rung_rows(s, ds=None):
    """The one place the rung chart reads data: ({config: {rung 'L1': (passed, n)}}, rungs L1..L6 in order). Reads the dataset's main-ladder set."""
    ds = ds or dataset.read(); ex = s.get("exploratory") or {}
    keep = list(s["configs"]) + [c for c in ("sol61-high", "sol61-high-fast", "astra-medium", "astra-medium-fast") if c in ex]  # fast mode beside its default tier
    by = {r["config"]: r["by_rung"] for r in ds["rows"] if r["source"] == "main" and r["set"] == "main ladder"}
    rows = {c: {g: tuple(v) for g, v in by[c].items()} for c in keep}
    return rows, sorted({g for r in rows.values() for g in r}, key=lambda g: int(g[1:]))


def rung_chart(s, ds=None):
    """Heat table, one row per config (family shape + colour + name, grouped by family), one column per rung L1-L6;
    each cell is passes out of the attempts on that rung. Perfect cells stay plain, so the misses stand out."""
    from analysis.page import ORDER, SHAPE, marker  # lazy: page imports this module
    cfg, rungs = rung_rows(s, ds)
    names = sorted(cfg, key=lambda c: ORDER.index(c) if c in ORDER else len(ORDER))
    W, L, T, cw, rh = 560, 190, 96, 58, 30
    H = T + rh * len(names) + 40
    probs = {g: " ".join(q[:3] for q in sorted(s["problems"]) if f"L{s['problems'][q]['rung']}" == g) for g in rungs}
    b = [text(12, 24, "Pass rate by difficulty rung (main ladder p01-p12)", 15, weight="600"),
         text(12, 46, "Passes per rung. Tinted = a miss. L7 excluded.", 11, fill=MUTED)]
    for i, g in enumerate(rungs):
        x = L + i * cw + cw / 2
        b += [text(x, T - 22, g, 14, "middle", INK, "600"), text(x, T - 8, probs[g], 9, "middle", MUTED)]
    for r, c in enumerate(names):
        y = T + r * rh; col = FAMILY(c)
        b.append(f"<line x1='8' x2='{L + len(rungs) * cw}' y1='{y}' y2='{y}' stroke='{GRID}'/>")
        b.append(marker(SHAPE(c), 22, y + rh / 2, col, col, k=0.8))
        b.append(text(40, y + rh / 2 + 5, DISP(c), 14, fill=col, weight="600"))
        for i, g in enumerate(rungs):
            v = cfg[c].get(g); x = L + i * cw
            if not v: b.append(text(x + cw / 2, y + rh / 2 + 5, "-", 13, "middle", MUTED)); continue
            k, n = v
            tint = "" if k == n else f"<rect x='{x + 2}' y='{y + 2}' width='{cw - 4}' height='{rh - 4}' rx='3' style='fill:{BADC if k / n <= 0.4 else WARNC}' fill-opacity='0.3'/>"
            b.append(f"<g><title>{escape(DISP(c))} on {g}: {k} of {n} passed</title>{tint}"
                     + text(x + cw / 2, y + rh / 2 + 5, f"{k}/{n}", 13, "middle", INK, "normal" if k == n else "700") + "</g>")
    yb = T + rh * len(names)
    b.append(f"<line x1='8' x2='{L + len(rungs) * cw}' y1='{yb}' y2='{yb}' stroke='{GRID}'/>")
    b.append(text(12, yb + 24, "Rung L1 is easiest. Red tint: 40% or less, the breaking point.", 11, fill=MUTED))
    out = svg(W, H, b).replace(f"width='{W}' height='{H}'", "class='rung' width='100%' height='auto' style='max-width:560px'", 1)
    return re.sub(r"font-size='([\d.]+)'( text-anchor='\w+' style=')", r"\2font-size:\1px;", out)  # inline size: the page's phone CSS does not rescale this chart


def heatmap(s):
    """Main-run configs first, then exploratory ones (muted headers, after a gap); a dash where a config did not run a problem."""
    ex = s.get("exploratory") or {}
    cols = [(c, {p: v[c] for p, v in s["problems"].items()}, False) for c in s["configs"]] + [(c, v["by_problem"], True) for c, v in ex.items()]
    probs = sorted(s["problems"], key=lambda q: (s["problems"][q]["rung"], q)); cw, ch, L, T, gap = 50, 24, 250, 130, 14
    X = lambda j: L + j * cw + (gap if cols[j][2] else 0)
    W, H = X(len(cols) - 1) + cw + 20, T + ch * len(probs) + 40
    b = [text(12, 24, "Passes out of 5 per problem and config", 14, weight="600"),
         text(12, 42, "Main ladder, p01–p12, rungs L1–L6 (2 per rung). Left: main run. Right, muted: exploratory configs; ⚡ = fast mode.", 11, fill=MUTED)]
    for j, (c, _, x) in enumerate(cols):  # rotated headers so every config fits
        b.append(text(X(j) + cw / 2 + 4, T - 8, DISP(c), 11, "start", MUTED if x else INK, rotate=-55))
    for i, p in enumerate(probs):
        y = T + i * ch
        b.append(f"<g><title>{escape(TESTS.get(p, ''))}</title>" + text(L - 10, y + ch / 2 + 4, plabel(p, s["problems"][p]["rung"]), 11, "end", INK) + "</g>")
        for j, (c, bp, _) in enumerate(cols):
            k = bp.get(p)
            if k is None:
                b.append(text(X(j) + cw / 2, y + ch / 2 + 4, "–", 11, "middle", MUTED)); continue
            fill, op = ("var(--bad,#b3261e)", 0.35) if k == 0 else ("var(--good,#1c7c3c)", 0.1 + 0.09 * k)
            b.append(f"<rect x='{X(j) + 1}' y='{y + 1}' width='{cw - 2}' height='{ch - 2}' fill='{fill}' opacity='{op:.2f}'/>")
            b.append(text(X(j) + cw / 2, y + ch / 2 + 4, k, 11, "middle", INK))
    return svg(W, H, b)


def floor_chart(s):
    rows = [(c, "main ladder p01-p12", v["input_floor"][0], v["input_floor"][1]) for c, v in s["configs"].items()]
    rows += [(c, "Repo tasks (4 tasks x 3 runs, with tools)", v["input_floor"][0], v["input_floor"][1]) for c, v in (s.get("agentic") or {}).items()]
    W, L, R, T, bh = 760, 190, 90, 50, 20
    H = T + len(rows) * (bh + 8) + 70
    mx = max(r[2] for r in rows) * 1.05; X = lambda v: L + v / mx * (W - L - R)
    b = [text(12, 24, "Minimum input tokens over all calls (the harness floor), cached share shaded", 14, weight="600")]
    y = T; last = None
    for c, track, tot, cached in rows:
        if track != last:
            b.append(text(12, y + 12, track, 11, fill=MUTED, weight="600")); y += 18; last = track
        b += [f"<rect x='{L}' y='{y}' width='{X(tot) - L:.1f}' height='{bh}' fill='{FAMILY(c)}' opacity='0.35'/>",
              f"<rect x='{L}' y='{y}' width='{X(cached) - L:.1f}' height='{bh}' fill='{FAMILY(c)}'/>",
              text(L - 8, y + 14, c, 11, "end"), text(X(tot) + 6, y + 14, f"{tot:,}", 11, fill=MUTED)]
        y += bh + 8
    b.append(text(12, y + 22, f"Solid: cached. Pale: uncached. Codex includes ~{HOST_AGENTS_MD} host AGENTS.md tokens.", 11, fill=MUTED))
    return svg(W, y + 40, b)


def agentic_chart(s):
    ag = s.get("agentic") or {}
    if not ag: return None
    W, H, L, R, T, B = 760, 500, 80, 40, 200, 80
    xs = [v["usd_per_run"] for v in ag.values()]
    x0, x1 = min(xs) / 1.5, max(xs) * 1.5
    X = lambda v: L + (math.log(v) - math.log(x0)) / (math.log(x1) - math.log(x0)) * (W - L - R); Y = lambda p: H - B - p * (H - T - B)
    b = [text(L, 24, "Repo tasks (4 tasks x 3 runs, with tools): pass rate vs $ per run", 14, weight="600")]
    for p in (0, 0.25, 0.5, 0.75, 1.0):
        b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(p):.1f}' y2='{Y(p):.1f}' stroke='{GRID}'/>", text(L - 8, Y(p) + 4, f"{100 * p:.0f}%", 11, "end", MUTED)]
    for v in log_ticks(x0, x1):
        b += [f"<line x1='{X(v):.1f}' x2='{X(v):.1f}' y1='{T}' y2='{H - B}' stroke='{GRID}'/>", text(X(v), H - B + 18, fmt_usd(v), 11, "middle", MUTED)]
    b += [text((L + W - R) / 2, H - B + 38, "$ per run", 12, "middle", MUTED), text(20, (T + H - B) / 2, "runs passing all hidden tests", 12, "middle", MUTED, rotate=-90)]
    # Direct labels above the dots, with vertical stubs clear of the shared 100% line.
    for i, (c, v) in enumerate(sorted(ag.items(), key=lambda kv: kv[1]["usd_per_run"])):
        x, y = X(v["usd_per_run"]), Y(v["hidden_pass_rate"]); lo, hi = v["ci95"]
        if v["hidden_pass"] == v["n"]: lo = 0.05 ** (1 / len(v["by_task"]))  # bootstrap collapses at 100%; one-sided bound over tasks, as in the tables
        b.append(f"<line x1='{x:.1f}' x2='{x:.1f}' y1='{Y(lo):.1f}' y2='{Y(hi):.1f}' stroke='{FAMILY(c)}' stroke-width='2' opacity='0.5'/>")
        b.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='6' fill='{FAMILY(c)}'/>")
        lab = f"{DISP(c)} {v['hidden_pass']}/{v['n']}{' *' if v['cost_kind'] == 'proxy' else ''}"
        ly = T - 24 - i * 22
        anchor = "end" if x + len(lab) * 6.6 > W - 10 else "start"
        b.append(f"<line class='leader' x1='{x:.1f}' x2='{x:.1f}' y1='{y - 8:.1f}' y2='{ly + 5:.1f}' stroke='{FAMILY(c)}' stroke-width='1' opacity='0.6'/>")
        b.append(text(x, ly, s=lab, size=11, anchor=anchor))
    b.append(text(L, H - 10, "All configs: 12/12. Bars: lower 95% bound. * Estimated from tokens.", 11, fill=MUTED))
    return svg(W, H, b)


def bars(title, rows, fmt, note, W=760, L=190, R=110):
    """Horizontal bars. rows: (label, value, colour, hollow). Labels sit left of the bars, values right of them."""
    T, bh = 50, 20; H = T + len(rows) * (bh + 8) + 46
    mx = max(r[1] for r in rows) * 1.02; X = lambda v: L + v / mx * (W - L - R)
    b = [text(12, 24, title, 14, weight="600")]
    for i, (lab, v, col, hollow) in enumerate(rows):
        y = T + i * (bh + 8)
        b += [f"<rect x='{L}' y='{y}' width='{max(1, X(v) - L):.1f}' height='{bh}' fill='{PLATE if hollow else col}' stroke='{col}' stroke-width='{2 if hollow else 0}'/>",
              text(L - 8, y + 14, lab, 11, "end", MUTED if hollow else INK), text(X(v) + 6, y + 14, fmt(v), 11, fill=MUTED)]
    b.append(text(12, H - 14, note, 10, fill=MUTED))
    return svg(W, H, b)


def all_configs(s):
    return [(c, v, "-fast" in c) for c, v in {**s["configs"], **(s.get("exploratory") or {})}.items()]


def ladder(ds, s, set_="main ladder"):
    """[(config, dataset row, hollow)] for one set: the 12-problem x 5-repeat configs. Hollow = fast mode."""
    order = [c for c, _, _ in all_configs(s)]  # page order, until the registry owns it
    rows = [(r["config"], r, "-fast" in r["config"]) for r in ds["rows"] if r["source"] == "main" and r["set"] == set_]
    return sorted(rows, key=lambda x: order.index(x[0]))


def cost_tokens_chart(s, ds=None):
    """Total $ for the 60 function-track calls, and $ per 1,000 tokens processed (input plus output), per config. Reads the dataset."""
    rows = ladder(ds or dataset.read(), s)
    tot = [(r["display"] + (" *" if r["cost_kind"] == "proxy" else ""), r["spend"], FAMILY(c), x) for c, r, x in rows]
    per = [(r["display"] + (" *" if r["cost_kind"] == "proxy" else ""), 1000 * r["usd_per_call"] / (r["tokens_in_mean"] + r["tokens_out_mean"]), FAMILY(c), x) for c, r, x in rows]
    a = bars("Total $ for the main ladder p01-p12", tot, lambda v: f"${v:.3f}", "Solid: normal speed; hollow: fast mode. * Codex cost is proxy; Claude is measured.")
    b = bars("$ per 1,000 tokens processed (input + output, mean per call)", per, lambda v: f"${v:.5f}",
                "Cached input costs less per token. * Codex cost is proxy.")
    return a, b


TOKEN_IN = ["luna-low", "luna-low-bare", "haiku-low", "sonnet-medium"]


def token_in_chart(s, ds=None):
    allc = {c: r for c, r, _ in ladder(ds or dataset.read(), s)}
    lab = {"luna-low": "luna-low, stock Codex", "luna-low-bare": "luna-low, stripped Codex", "haiku-low": "haiku-low, tools off", "sonnet-medium": "sonnet-medium, tools off"}
    rows = [(lab[c], allc[c]["tokens_in_mean"], FAMILY(c), "-fast" in c) for c in TOKEN_IN if c in allc]
    return bars("Mean input tokens per call (main ladder p01-p12)", rows, lambda v: f"{v:,}",
                f"Includes cached input. Codex includes ~{HOST_AGENTS_MD} host AGENTS.md tokens.", L=200, R=80)


def check_design(s):
    """Chart titles and notes state the design (12 problems x 5 attempts = 60 calls per config, 10 per rung, 5 per cell). Fail if the data differ."""
    bad = [c for c, v, _ in all_configs(s) if v["n"] != 60 or any(r["n"] != 10 for r in v["by_rung"].values())]
    if bad or len(s["problems"]) != 12:
        raise SystemExit(f"chart text assumes 12 problems, 60 calls per config and 10 per rung; check {bad or 'the problem count'}")


def build(s, ds=None):
    """{file name: SVG text or None} for every chart."""
    check_design(s); ds = ds or dataset.read()
    charts = {"pareto.svg": pareto_chart(s), "cost_time.svg": cost_time_chart(s), "pass_by_rung.svg": rung_chart(s, ds), "heatmap.svg": heatmap(s),
              "token_floor.svg": floor_chart(s), "agentic.svg": agentic_chart(s), "token_in.svg": token_in_chart(s, ds)}
    charts["cost_total.svg"], charts["cost_per_1k.svg"] = cost_tokens_chart(s, ds)
    return charts


def main():
    s = json.load(open(os.path.join(ROOT, "results", "summary.json")))
    os.makedirs(OUT, exist_ok=True)
    charts = build(s)
    for name, body in charts.items():
        if body: open(os.path.join(OUT, name), "w").write(body)
    print("charts ->", os.path.relpath(OUT, ROOT), ", ".join(n for n, b in charts.items() if b))


if __name__ == "__main__":
    main()
