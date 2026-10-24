"""Draw the report charts as plain SVG from results/summary.json. Standard library only; no model calls."""
import json, math, os
from analysis import dataset
from analysis.labels import DISP, TESTS, plabel
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "report", "charts")
FONT = "font-family='Hanken Grotesk, -apple-system, Segoe UI, Helvetica, Arial, sans-serif'"
INK, MUTED, GRID, PLATE = "var(--fg,#1d2321)", "var(--muted,#5d6763)", "var(--line,#dde2de)", "var(--panel,#ffffff)"
HOST_AGENTS_MD = "1.3k"  # tokens of the host's ~/.codex/AGENTS.md, measured once by hand (bytes / 4); not in the result rows
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


def rung_chart(s):
    from analysis.page import config_marker, place
    ex = s.get("exploratory") or {}
    cfg = {**s["configs"], **{c: ex[c] for c in ("sol61-high", "sol61-high-fast", "astra-medium", "astra-medium-fast") if c in ex}}
    rungs = sorted({g for v in cfg.values() for g in v["by_rung"]}, key=lambda g: int(g[1:]))
    W, H, L, R, T, B = 760, 650, 72, 220, 200, 72
    X = lambda i: L + i / max(1, len(rungs) - 1) * (W - L - R)
    Y = lambda p: H - B - p * (H - T - B)
    b = [text(L, 24, "Pass rate by difficulty rung (main ladder p01-p12)", 14, weight="600"),
         text(L, 46, "L7 excluded. Solid = normal speed; hollow = fast mode. Hover a point for per-problem passes.", 11, fill=MUTED)]
    patterns = ("none", "8 3", "2 3", "8 3 2 3", "12 4", "4 2 1 2", "12 3 2 3", "2 2 2 5", "10 2 4 2", "1 4")
    dashes = {c: patterns[k] if k < len(patterns) else f"{k + 3} 2 1 4" for k, c in enumerate(cfg)}
    # The key precedes the plot; each entry repeats the series dash and model marker.
    for k, c in enumerate(cfg):
        x, y = L + (k % 3) * 220, 72 + (k // 3) * 25
        b.append(f"<line class='rung-key' x1='{x}' x2='{x + 24}' y1='{y}' y2='{y}' stroke='{FAMILY(c)}' stroke-width='2' stroke-dasharray='{dashes[c]}'/>")
        b.append(config_marker(c, x + 12, y, FAMILY(c), .55))
        b.append(text(x + 31, y + 4, DISP(c), 11, fill=FAMILY(c)))
    for rate in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(rate):.1f}' y2='{Y(rate):.1f}' stroke='{GRID}'/>",
              text(L - 8, Y(rate) + 4, f"{100 * rate:.0f}%", 11, "end", MUTED)]
    b.append(f"<line x1='{L}' x2='{W - R}' y1='{Y(0.4):.1f}' y2='{Y(0.4):.1f}' stroke='var(--bad,#b3261e)' stroke-dasharray='4 3'/>")
    b.append(text(L + 6, Y(0.4) - 6, "breaking point (≤ 40%)", 11, fill="var(--bad,#b3261e)"))
    for i, g in enumerate(rungs):
        b.append(text(X(i), H - B + 18, g, 11, "middle", MUTED))
        b.append(text(X(i), H - B + 34, " ".join(q[:3] for q in sorted(s["problems"]) if f"L{s['problems'][q]['rung']}" == g), 11, "middle", MUTED))
    b.append(text((L + W - R) / 2, H - 8, "rung (L1 easiest; problems listed underneath)", 12, "middle", MUTED))
    dots = []
    walls = [(L, Y(.4) - 3, W - R, Y(.4) + 3),
             (L + 6, Y(.4) - 20, L + 180, Y(.4) - 3)]
    for k, (c, v) in enumerate(cfg.items()):
        off = (k - (len(cfg) - 1) / 2) * 2.5
        pts = []
        for i, g in enumerate(rungs):
            if g not in v["by_rung"]: continue
            z = v["by_rung"][g]; rate = z["passed"] / z["n"]
            px, py = X(i) + off, Y(rate); pts.append((px, py))
            probs = [q for q in sorted(s["problems"]) if f"L{s['problems'][q]['rung']}" == g]
            detail = ", ".join(f"{q[:3]}: {(v.get('by_problem') or {}).get(q, s['problems'][q].get(c))}/{v['n'] // len(s['problems'])}" for q in probs)
            title = f"{DISP(c)}, {g}: {z['passed']}/{z['n']} passed; {detail}"
            mark = config_marker(c, px, py, FAMILY(c), .6).replace(" ", ' class="rung-marker" ', 1)
            b.append(f"<g><title>{escape(title)}</title>{mark}</g>")
            dots.append(dict(c=f"{c}/{g}", name=f"{DISP(c)} {z['passed']}/{z['n']}", x=px, y=py, on=False, dip=rate < 1))
        # Thin boxes follow each segment instead of blocking its entire diagonal bounds.
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            steps = max(1, math.ceil(math.hypot(bx - ax, by - ay) / 6))
            for j in range(steps):
                x0, y0 = ax + (bx - ax) * j / steps, ay + (by - ay) * j / steps
                x1, y1 = ax + (bx - ax) * (j + 1) / steps, ay + (by - ay) * (j + 1) / steps
                walls.append((min(x0, x1) - 2, min(y0, y1) - 2, max(x0, x1) + 2, max(y0, y1) + 2))
        # Lines behind markers, without hiding each point's hover title.
        b.insert(0, f"<polyline points='{' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)}' fill='none' stroke='{FAMILY(c)}' stroke-width='2' stroke-dasharray='{dashes[c]}'/>")
    for p, (x, y, anchor) in place([p for p in dots if p["dip"]], lambda v: v, lambda v: v,
                                   {p["c"]: (14, -14, "start") for p in dots if p["c"].endswith("/L6")},
                                   (L - 20, W - 10, T - 28, H - B - 4), walls=walls, also=dots, char_width=6.6, label_height=15):
        if p["lead"]:
            a, b0, c, d = p["lead"]
            b.append(f"<line x1='{a:.1f}' y1='{b0:.1f}' x2='{c:.1f}' y2='{d:.1f}' stroke='{MUTED}'/>")
        b.append(text(x, y, p["name"], 11, anchor).replace("<text ", "<text class='dip-label' ", 1))
    return svg(W, H, b)


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
    charts = {"pareto.svg": pareto_chart(s), "cost_time.svg": cost_time_chart(s), "pass_by_rung.svg": rung_chart(s), "heatmap.svg": heatmap(s),
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
