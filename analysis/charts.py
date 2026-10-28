"""Draw the report charts as plain SVG from results/dataset.json. Standard library only; no model calls."""
import math, os, re
from analysis import configs, dataset
from analysis.labels import DISP, TESTS, plabel
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "report", "charts")
FONT = "font-family='Hanken Grotesk, -apple-system, Segoe UI, Helvetica, Arial, sans-serif'"
INK, MUTED, GRID, PLATE = "var(--fg)", "var(--muted)", "var(--line)", "var(--panel)"
HOST_AGENTS_MD = dataset.HOST_AGENTS_MD
BADC, WARNC = "var(--bad)", "var(--warn)"
FAMILY = lambda c: "var(--grok)" if c.startswith("grok") else "var(--devin)" if c.startswith("devin") else "var(--claude)" if c.startswith("haiku") else "var(--sonnet)" if c.startswith("sonnet") else "var(--codex)"


# Per-label vertical offsets so neighbouring points' labels do not collide.
LABEL_DY = {"luna-low": 18, "luna-low-bare": 18, "sol61-medium": 18, "sol56-high": 18}  # the 100% row holds three configs
LABEL_LEFT = {"haiku-low", "sonnet-medium"}  # left of the point, clear of luna-high and the 100% row
HERO_LEFT = {"sonnet-medium": 18, "haiku-medium": 4}  # README hero: left of the point, label dy; clear of the 100% row picks


def hexagon(x, y, r):
    """Flat-top hexagon points: Grok's own mark, distinct from every other series' shape."""
    return " ".join(f"{x + r * math.cos(math.radians(a)):.1f},{y + r * math.sin(math.radians(a)):.1f}" for a in range(0, 360, 60))


def grok_mark(x, y, r=10):
    return f"<polygon points='{hexagon(x, y, r)}' fill='var(--grok)' stroke='var(--panel)' stroke-width='1.5'/>"


def token_style():
    """Exact canonical bundle for standalone charts and the share-card source."""
    with open(os.path.join(ROOT, "docs", "page", "tokens.css")) as src:
        return "<style>" + src.read().strip() + "</style>"


def svg(w, h, body, x=0, y=0):
    if not x and not y:
        return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' {FONT} font-size='12'>"
                f"<rect width='{w}' height='{h}' fill='{PLATE}'/>{''.join(body)}</svg>\n")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='{x} {y} {w} {h}' width='{w}' height='{h}' {FONT} font-size='12'>"
            f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='{PLATE}'/>{''.join(body)}</svg>\n")


def text(x, y, s, size=12, anchor="start", fill=INK, weight="normal", rotate=None):
    t = f" transform='rotate({rotate} {x} {y})'" if rotate else ""
    return f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' style='fill:{fill};' font-weight='{weight}'{t}>{escape(str(s))}</text>"


def log_ticks(lo, hi):
    out = []
    for e in range(math.floor(math.log10(lo)), math.ceil(math.log10(hi)) + 1):
        for m in (1, 2, 5):
            v = m * 10 ** e
            if lo <= v <= hi: out.append(v)
    return out


def pareto_chart(s, hero=False):
    """hero: README version, no intervals, labels only on the frontier and the Winner picks."""
    from analysis.dataset import WINNER_PICKS
    cfg = {c: v for c, v in s["configs"].items() if v["usd_per_pass"]}
    extra = {c: v for c, v in (s.get("exploratory") or {}).items() if v["usd_per_pass"] and c not in configs.CHART_HIDDEN}  # exploratory, not on the pre-registered frontier
    allc = {**cfg, **extra}
    # Grok is drawn on the same scale, never used to set it, and never joins the frontier. The README hero stays the full ladder.
    # grok47-medium ran p01-p06 only, so it stays off the plot.
    grok = {} if hero else {c: v for c, v in (s.get("grok") or {}).items() if v.get("usd_per_pass") and c not in configs.CHART_HIDDEN}
    W, H, L, R, T, B = 760, 480, 96, 30, 50, 80
    xs = [v["usd_per_pass"] for v in allc.values()]
    x0, x1 = min(xs) / 1.6, max(xs) * 1.6; y0 = 0.6
    X = lambda v: L + (math.log(v) - math.log(x0)) / (math.log(x1) - math.log(x0)) * (W - L - R)
    Y = lambda p: H - B - (p - y0) / (1 - y0) * (H - T - B)
    b = [text(L, 24, "Pass rate vs $ per pass, main ladder (up and left is better)" if hero else "Pass rate vs cost per passing solution (main ladder p01-p12, x log)", 14, weight="600")]
    for p in (0.6, 0.7, 0.8, 0.9, 1.0):
        b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(p):.1f}' y2='{Y(p):.1f}' stroke='{GRID}'/>", text(L - 8, Y(p) + 4, f"{100 * p:.0f}%", 11, "end", MUTED)]
    for v in log_ticks(x0, x1):
        b += [f"<line x1='{X(v):.1f}' x2='{X(v):.1f}' y1='{T}' y2='{H - B}' stroke='{GRID}'/>", text(X(v), H - B + 18, dataset.usd(v, tick=True), 11, "middle", MUTED)]
    b += [text((L + W - R) / 2, H - B + 38, "$ per passing call", 12, "middle", MUTED),
          text(26, (T + H - B) / 2, "pass rate (12 problems × 5 attempts)", 12, "middle", MUTED, rotate=-90)]
    front = s["pareto"]
    if len(front) > 1:
        pts = " ".join(f"{X(cfg[c]['usd_per_pass']):.1f},{Y(cfg[c]['pass_at_1']):.1f}" for c in front)
        b.append(f"<polyline points='{pts}' fill='none' stroke='{INK}' stroke-width='1.5' stroke-dasharray='5 4'/>")
    taken, label_boxes, pending = [], [], []
    for c, v in allc.items():
        x, y = X(v["usd_per_pass"]), Y(v["pass_at_1"]); on = c in front; hollow = "-fast" in c
        taken.append((x, y))
        lo, hi = v["ci95_plot"]
        col = FAMILY(c)
        if not hero:
            b.append(f"<line x1='{x:.1f}' x2='{x:.1f}' y1='{Y(max(lo, y0)):.1f}' y2='{Y(hi):.1f}' stroke='{col}' stroke-width='2' opacity='0.35'/>")
        if hollow:
            b.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='5.5' fill='{PLATE}' stroke='{col}' stroke-width='2'/>")
        else:
            b.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{7 if on else 5.5}' fill='{col}' stroke='{INK if on else PLATE}' stroke-width='1.5'/>")
        right = x > W - R - 170 or c in LABEL_LEFT
        label = f"{DISP(c)} ({100 * v['pass_at_1']:.0f}%){' *' if v['cost_kind'] == 'proxy' else ''}{', exploratory' if c in extra else ''}"
        if hero:
            if not (on or c in WINNER_PICKS): continue
            pick = WINNER_PICKS.get(c)
            label = f"{DISP(c)}{' ✓ ' + pick if pick else ''}"
            left = c in HERO_LEFT or (c in LABEL_LEFT and v["pass_at_1"] < 1)
            dy = HERO_LEFT.get(c, -10 if v["pass_at_1"] == 1 else 4)
            b.append(text(x - 10 if left else x + 10, y + dy, label, 12, "end" if left else "start", INK, "600" if pick else "normal"))
            continue
        pending.append((c, x, y, right, label, hollow, col, on))
    # Labels go down after every mark is known. Each takes its preferred spot, else the nearest free one (a leader joins a
    # moved label to its mark); no label box may touch another label box or a mark.
    for c, x, y, right, label, hollow, col, on in sorted(pending, key=lambda r: (not r[7], r[2], r[1])):
        tw = 6.4 * len(label)
        pref = LABEL_DY.get(c, -8)
        spot = None
        for dy in [pref] + [d for k in range(1, 26) for d in (pref - 14 * k, pref + 14 * k)]:
            for side in ((right, not right) if dy == pref else (right, not right)):
                lx, ly = (x - 10 if side else x + 10), y + dy
                left = lx - tw if side else lx
                rect = (left, ly - 12, left + tw, ly + 3)
                if rect[0] < L or rect[2] > W - 6 or rect[1] < 30 or rect[3] > H - B + 4: continue
                if any(not (rect[2] < q[0] or rect[0] > q[2] or rect[3] < q[1] or rect[1] > q[3]) for q in label_boxes): continue
                if any(math.hypot(cx - x, cy - y) > 1 and rect[0] < cx + 8 and rect[2] > cx - 8 and rect[1] < cy + 8 and rect[3] > cy - 8 for cx, cy in taken): continue
                spot = (lx, ly, "end" if side else "start", rect); break
            if spot: break
        if spot is None:
            spot = (x + 10, y + pref, "start", (x + 10, y + pref - 12, x + 10 + tw, y + pref + 3))
        lx, ly, anchor, rect = spot
        label_boxes.append(rect)
        if abs(ly - y) >= 20:
            b.append(f"<line x1='{x:.1f}' x2='{lx:.1f}' y1='{y + (6 if ly > y else -6):.1f}' y2='{ly + (-3 if ly > y else 3):.1f}' stroke='{col}' stroke-width='1' opacity='0.6'/>")
        b.append(text(lx, ly, label, 11, anchor, MUTED if hollow else INK))
    for c, v in grok.items():
        x, y = X(v["usd_per_pass"]), Y(v["pass_at_1"])
        step = 0
        while any(math.dist((x + step, y), p) < 14 for p in taken):
            step += 18  # only this mark moves; the series it collided with stays put
        x += step
        taken.append((x, y))
        lo, hi = v["ci95_plot"]
        col = FAMILY(c)
        b.append(f"<line x1='{x:.1f}' x2='{x:.1f}' y1='{Y(max(lo, y0)):.1f}' y2='{Y(hi):.1f}' stroke='{col}' stroke-width='2' opacity='0.35'/>")
        b.append(grok_mark(x, y))
        label = f"{DISP(c)} ({100 * v['pass_at_1']:.0f}%)"
        tw = 6.4 * len(label)
        spot = None
        for dx, dy, anchor in ((10, -8, "start"), (-10, -8, "end"), (10, 14, "start"), (-10, 14, "end"),
                               (10, -22, "start"), (-10, 28, "end"), (-10, 32, "end"), (10, 28, "start"),
                               (-10, 42, "end"), (-10, 56, "end"), (-10, 68, "end")):
            lx, ly = x + dx, y + dy
            left = lx - tw if anchor == "end" else lx
            rect = (left, ly - 12, left + tw, ly + 3)
            if rect[0] < L or rect[2] > W - 6 or rect[1] < 30 or rect[3] > H - B:
                continue
            if any(not (rect[2] < q[0] or rect[0] > q[2] or rect[3] < q[1] or rect[1] > q[3]) for q in label_boxes):
                continue
            if any(math.hypot(cx - x, cy - y) > 1 and rect[0] < cx + 8 and rect[2] > cx - 8 and rect[1] < cy + 8 and rect[3] > cy - 8 for cx, cy in taken):
                continue
            spot = (lx, ly, anchor, rect)
            break
        if spot is None:
            spot = (x + 10, y + 14, "start", None)
        lx, ly, anchor, rect = spot
        if rect:
            label_boxes.append(rect)
        if abs(ly - y) >= 20:  # the 100% row is already full, so a moved Grok label keeps a leader
            b.append(f"<line x1='{x:.1f}' x2='{lx:.1f}' y1='{y + (6 if ly > y else -6):.1f}' y2='{ly + (-3 if ly > y else 3):.1f}' stroke='{col}' stroke-width='1' opacity='0.6'/>")
        b.append(text(lx, ly, label, 11, anchor, INK))
    b.append(text(L, H - 10, "Dashed: best trade-offs. Hollow: fast mode. Codex $ is a token-price estimate." if hero else
                  "Dashed: best trade-offs. Bars: 95% CI. Solid: normal speed; hollow: fast mode. * Codex cost is proxy.", 10, fill=MUTED))
    note = "" if hero else (s.get("facts") or {}).get("grok_chart_note", "")
    if note:
        b.append(text(L, H + 8, note, 10, fill=MUTED))
        return svg(W, H + 22, b)
    return svg(W, H, b)


MIN_PASS = dataset.MIN_PASS
PURPLE = "var(--frontier)"


def cost_time_chart(s):
    """$ per pass against median latency, function track L1-L6. The frontier is drawn over configs at or above MIN_PASS
    pass@1: among those, the ones no other config beats on both cost and time."""
    from analysis.dataset import speed_dominates
    allc = {**{c: v for c, v in s["configs"].items() if v["usd_per_pass"]}, **{c: v for c, v in (s.get("exploratory") or {}).items() if v["usd_per_pass"] and c not in configs.CHART_HIDDEN}}
    pts = {c: (v["usd_per_pass"], v["latency_s"]["median"]) for c, v in allc.items()}
    ok = {c: p for c, p in pts.items() if allc[c]["pass_at_1"] >= MIN_PASS}
    front = [a for a, (x, y) in ok.items() if not any(speed_dominates({"x": y2, "y": x2}, {"x": y, "y": x}) for b, (x2, y2) in ok.items() if b != a)]
    front.sort(key=lambda c: pts[c][0])
    W, H, L, R, T, B = 760, 440, 96, 30, 50, 80
    xs = [p[0] for p in pts.values()]; x0, x1 = min(xs) / 1.6, max(xs) * 1.6
    y1 = math.ceil(max(p[1] for p in pts.values()) / 5) * 5 + 5
    X = lambda v: L + (math.log(v) - math.log(x0)) / (math.log(x1) - math.log(x0)) * (W - L - R)
    Y = lambda t: H - B - t / y1 * (H - T - B)
    title = "Cost per passing solution vs median latency (main ladder p01-p12, x log)"
    b = [text(L, 24, title, 14, weight="600")]
    for t in range(0, int(y1) + 1, 5):
        b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(t):.1f}' y2='{Y(t):.1f}' stroke='{GRID}'/>", text(L - 8, Y(t) + 4, f"{t} s", 11, "end", MUTED)]
    # Grok is slower than this axis. Extra gridlines sit above it; the scale and the existing lines stay.
    grok = {c: v for c, v in (s.get("grok") or {}).items() if v.get("usd_per_pass") and c not in configs.CHART_HIDDEN}
    tops = []
    gmax = max((v["latency_s"]["median"] for v in grok.values()), default=0)
    if gmax > y1:
        for t in range(int(y1) + 5, math.ceil(gmax / 5) * 5 + 1, 5):
            b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(t):.1f}' y2='{Y(t):.1f}' stroke='{GRID}'/>", text(L - 8, Y(t) + 4, f"{t} s", 11, "end", MUTED)]
            tops.append(Y(t) - 11)
    for v in log_ticks(x0, x1):
        b += [f"<line x1='{X(v):.1f}' x2='{X(v):.1f}' y1='{T}' y2='{H - B}' stroke='{GRID}'/>", text(X(v), H - B + 18, dataset.usd(v, tick=True), 11, "middle", MUTED)]
    b += [text((L + W - R) / 2, H - B + 38, "$ per passing call", 12, "middle", MUTED),
          text(26, (T + H - B) / 2, "median seconds per call", 12, "middle", MUTED, rotate=-90)]
    if len(front) > 1:
        b.append(f"<polyline points='{' '.join(f'{X(pts[c][0]):.1f},{Y(pts[c][1]):.1f}' for c in front)}' fill='none' stroke='{PURPLE}' stroke-width='2.5' stroke-dasharray='6 4'/>")
    lanes, taken = {}, []
    for c, (x, t) in sorted(pts.items(), key=lambda item: item[1][0]):
        hollow = "-fast" in c; px, py = X(x), Y(t)
        taken.append((px, py))
        col = FAMILY(c)
        b.append(f"<circle cx='{px:.1f}' cy='{py:.1f}' r='6' fill='{PLATE if hollow else col}' stroke='{PURPLE if c in front else col if hollow else PLATE}' stroke-width='{3 if c in front else 2 if hollow else 1.5}'/>")
        lab = f"{DISP(c)} ({100 * allc[c]['pass_at_1']:.0f}%){' *' if allc[c]['cost_kind'] == 'proxy' else ''}"; w = 6.3 * len(lab)
        xl = px - 10 - w if px + 10 + w > W - R else px + 10
        lane = next(k for k in range(30) if all(abs(ly - (py - 12 - 16 * k)) >= 15 or e < xl - 6 or s0 > xl + w + 6 for s0, e, ly in lanes.setdefault(0, [])))
        ly = py - 12 - 16 * lane
        lanes[0].append((xl, xl + w, ly))
        if lane: b.append(f"<line x1='{px:.1f}' x2='{px:.1f}' y1='{py - 7:.1f}' y2='{ly + 3:.1f}' stroke='{col}' stroke-width='1' opacity='0.6'/>")
        b.append(text(xl, ly, lab, 11, fill=MUTED if hollow else INK))
    for c, v in grok.items():  # after the other labels, so their lanes stay where they were
        x, t = v["usd_per_pass"], v["latency_s"]["median"]
        px, py = X(x), Y(t)
        step = 0
        while any(math.dist((px + step, py), p) < 14 for p in taken):
            step += 18
        px += step
        taken.append((px, py))
        col = FAMILY(c)
        b.append(grok_mark(px, py))
        tops.append(py - 10)
        lab = f"{DISP(c)} ({100 * v['pass_at_1']:.0f}%)"; w = 6.3 * len(lab)
        xl = px - 10 - w if px + 10 + w > W - R else px + 10
        lane = next(k for k in range(30) if all(abs(ly - (py - 12 - 16 * k)) >= 15 or e < xl - 6 or s0 > xl + w + 6 for s0, e, ly in lanes.setdefault(0, [])))
        ly = py - 12 - 16 * lane
        lanes[0].append((xl, xl + w, ly))
        tops.append(ly - 11)
        if lane: b.append(f"<line x1='{px:.1f}' x2='{px:.1f}' y1='{py - 7:.1f}' y2='{ly + 3:.1f}' stroke='{col}' stroke-width='1' opacity='0.6'/>")
        b.append(text(xl, ly, lab, 11, fill=INK))
    b.append(text(L, H - 10, f"Purple ring: best trade-offs, pass rate ≥ {100 * MIN_PASS:.0f}%, then cost and time. Solid: normal speed; hollow: fast mode. * Codex cost is proxy.", 10, fill=MUTED))
    note = (s.get("facts") or {}).get("grok_chart_note", "")
    pad = 0
    if note:
        b.append(text(L, H + 8, note, 10, fill=MUTED))
        pad = 22
    high = [y for y in tops if y < 24]
    if high:
        title_y = min(high) - 16
        b[0] = text(L, title_y, title, 14, weight="600")
        view_y = math.floor(title_y - 18)
        if gmax > y1:
            for v in log_ticks(x0, x1):  # extend the grid into the new strip without moving the lines already drawn
                b.append(f"<line x1='{X(v):.1f}' x2='{X(v):.1f}' y1='{Y(math.ceil(gmax / 5) * 5):.1f}' y2='{T}' stroke='{GRID}'/>")
        return svg(W, (H + pad) - view_y, b, y=view_y)
    return svg(W, H + pad, b)


def rung_rows(s, ds=None):
    """The one place the rung chart reads data: ({config: {rung 'L1': (passed, n)}}, rungs L1..L6 in order). Reads the dataset's main-ladder set."""
    ds = ds or dataset.read(); ex = s.get("exploratory") or {}
    keep = list(s["configs"]) + [c for c in ("sol61-high", "sol61-high-fast", "astra-medium", "astra-medium-fast") if c in ex]  # fast mode beside its default tier
    by = {r["config"]: r["by_rung"] for r in ds["rows"] if r["source"] == "main" and r["set"] == "main ladder"}
    rows = {c: {g: tuple(v) for g, v in by[c].items()} for c in keep}
    for r in ds["rows"]:  # Devin free tier: 1 repeat, so a partial ladder; shown here for pass rates, never for $
        if r["source"] == "main" and r["set"] == "partial ladder" and r["config"] in configs.DEVIN_CONFIGS:
            rows[r["config"]] = {g: tuple(v) for g, v in r["by_rung"].items()}
    return rows, sorted({g for r in rows.values() for g in r}, key=lambda g: int(g[1:]))


def rung_chart(s, ds=None):
    """Heat table, one row per config (family shape + colour + name, grouped by family), one column per rung L1-L6;
    each cell is passes out of the attempts on that rung. Perfect cells stay plain, so the misses stand out."""
    from analysis.page import ORDER, config_marker  # lazy: page imports this module
    cfg, rungs = rung_rows(s, ds)
    names = sorted(cfg, key=lambda c: ORDER.index(c) if c in ORDER else len(ORDER))  # Devin last: it is not in ORDER
    L, T, cw, rh = 190, 270, 90, 30
    W = L + len(rungs) * cw + 12
    H = T + rh * len(names) + 40
    probs = {g: [plabel(q) for q in sorted(s["problems"]) if f"L{s['problems'][q]['rung']}" == g] for g in rungs}
    caption = (ds or dataset.read())["facts"]["rung_caption"]
    b = [text(12, 24, "Pass rate by difficulty rung (main ladder p01-p12)", 15, weight="600"),
         text(12, 46, caption, 10, fill=MUTED)]
    for i, g in enumerate(rungs):
        x = L + i * cw + cw / 2
        b.append(text(x, T - 8, g, 14, "middle", INK, "600"))
        b += [text(x + (j - .5) * 40, T - 32, label, 11, fill=MUTED, rotate=-65)
              for j, label in enumerate(probs[g])]
    for r, c in enumerate(names):
        y = T + r * rh; col = FAMILY(c)
        b.append(f"<line x1='8' x2='{L + len(rungs) * cw}' y1='{y}' y2='{y}' stroke='{GRID}'/>")
        b.append(config_marker(c, 22, y + rh / 2, col, k=0.8))
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
    b.append(text(12, yb + 24, "Rung L1 is easiest.", 11, fill=MUTED))
    out = svg(W, H, b).replace(f"width='{W}' height='{H}'", f"class='rung' width='{W}' height='{H}'", 1)
    return re.sub(r"font-size='([\d.]+)'( text-anchor='\w+' style=')", r"\2font-size:\1px;", out)  # inline size: the page's phone CSS does not rescale this chart


def heatmap(s):
    """Main-run configs first, then exploratory ones (muted headers, after a gap); a dash where a config did not run a problem."""
    ex = {c: v for c, v in (s.get("exploratory") or {}).items() if c not in configs.CHART_HIDDEN}
    dv = {c: v for c, v in (s.get("exploratory") or {}).items() if c in configs.DEVIN_CONFIGS}  # 1 repeat: cells are 0 or 1 of 1
    cols = [(c, {p: v[c] for p, v in s["problems"].items()}, False) for c in s["configs"]] + [(c, v["by_problem"], True) for c, v in ex.items()] \
        + [(c, v["by_problem"], True) for c, v in dv.items()]
    probs = sorted(s["problems"], key=lambda q: (s["problems"][q]["rung"], q)); cw, ch, L, T, gap = 50, 24, 250, 130, 14
    X = lambda j: L + j * cw + (gap if cols[j][2] else 0)
    W, H = X(len(cols) - 1) + cw + 20, T + ch * len(probs) + 40
    b = [text(12, 24, "Passes out of 5 per problem and config", 14, weight="600"),
         text(12, 42, "Main ladder, p01–p12, rungs L1–L6 (2 per rung). Left: main run. Right, muted: exploratory configs; ⚡ = fast mode. Last column: Devin, 1 try per problem (0 or 1).", 11, fill=MUTED)]
    for j, (c, _, x) in enumerate(cols):  # rotated headers so every config fits
        b.append(text(X(j) + cw / 2 + 4, T - 8, DISP(c), 11, "start", MUTED if x else INK, rotate=-55))
    for i, p in enumerate(probs):
        y = T + i * ch
        b.append(f"<g><title>{escape(TESTS.get(p, ''))}</title>" + text(L - 10, y + ch / 2 + 4, plabel(p, s["problems"][p]["rung"]), 11, "end", INK) + "</g>")
        for j, (c, bp, _) in enumerate(cols):
            k = bp.get(p)
            if k is None:
                b.append(text(X(j) + cw / 2, y + ch / 2 + 4, "–", 11, "middle", MUTED)); continue
            top = 1 if c in dv else 5  # Devin's single try is a full-strength cell
            fill, op = ("var(--bad)", 0.35) if k == 0 else ("var(--good)", 0.1 + 0.09 * k * 5 / top)
            b.append(f"<rect x='{X(j) + 1}' y='{y + 1}' width='{cw - 2}' height='{ch - 2}' fill='{fill}' opacity='{op:.2f}'/>")
            b.append(text(X(j) + cw / 2, y + ch / 2 + 4, k, 11, "middle", INK))
    return svg(W, H, b)


def floor_chart(s):
    fast = {c: v for c, v in s["exploratory"].items() if c.endswith("-fast")}
    rows = [(c, configs.set_label("main ladder", capital=True), v["input_floor"][0], v["input_floor"][1]) for c, v in {**s["configs"], **fast}.items()]
    rows += [(c, "Repo tasks: tools on", v["input_floor"][0], v["input_floor"][1]) for c, v in (s.get("agentic") or {}).items()]
    W, L, R, T, bh = 760, 200, 90, 50, 20
    H = T + len(rows) * (bh + 8) + 70
    mx = max(r[2] for r in rows) * 1.05; X = lambda v: L + v / mx * (W - L - R)
    b = [text(12, 24, "Minimum input tokens over all calls (the harness floor), cached share shaded", 14, weight="600")]
    y = T; last = None
    for c, track, tot, cached in rows:
        if track != last:
            b.append(text(12, y + 12, track, 11, fill=MUTED, weight="600")); y += 18; last = track
        b += [f"<rect x='{L}' y='{y}' width='{X(tot) - L:.1f}' height='{bh}' fill='{FAMILY(c)}' opacity='0.35'/>",
              f"<rect x='{L}' y='{y}' width='{X(cached) - L:.1f}' height='{bh}' fill='{FAMILY(c)}'/>",
              text(L - 8, y + 14, DISP(c), 11, "end"), text(X(tot) + 6, y + 14, f"{tot:,}", 11, fill=MUTED)]
        y += bh + 8
    b.append(text(12, y + 22, f"Solid: cached. Pale: uncached. Codex includes ~{HOST_AGENTS_MD} host AGENTS.md tokens.", 11, fill=MUTED))
    return svg(W, y + 40, b)


def agentic_chart(s):
    from analysis.page import config_marker
    ag = s.get("agentic") or {}
    if not ag: return None
    W, H, L, R, T, B = 760, 500, 80, 40, 200, 80
    xs = [v["usd_per_run"] for v in ag.values()]
    x0, x1 = min(xs) / 1.5, max(xs) * 1.5
    X = lambda v: L + (math.log(v) - math.log(x0)) / (math.log(x1) - math.log(x0)) * (W - L - R); Y = lambda p: H - B - p * (H - T - B)
    b = [text(L, 24, "Repo tasks (4 tasks x 3 runs, with tools): task complete vs $ per run", 14, weight="600")]
    for p in (0, 0.25, 0.5, 0.75, 1.0):
        b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(p):.1f}' y2='{Y(p):.1f}' stroke='{GRID}'/>", text(L - 8, Y(p) + 4, f"{100 * p:.0f}%", 11, "end", MUTED)]
    for v in log_ticks(x0, x1):
        b += [f"<line x1='{X(v):.1f}' x2='{X(v):.1f}' y1='{T}' y2='{H - B}' stroke='{GRID}'/>", text(X(v), H - B + 18, dataset.usd(v, tick=True), 11, "middle", MUTED)]
    b += [text((L + W - R) / 2, H - B + 38, "$ per run", 12, "middle", MUTED), text(20, (T + H - B) / 2, "share of runs passing", 12, "middle", MUTED, rotate=-90)]
    # Direct labels above the dots, with vertical stubs clear of the shared 100% line.
    for i, (c, v) in enumerate(sorted(ag.items(), key=lambda kv: kv[1]["usd_per_run"])):
        x, y = X(v["usd_per_run"]), Y(v["task_complete"] / v["n"]); lo, hi = v["ci95_plot"]  # headline rule: task complete
        b.append(f"<line x1='{x:.1f}' x2='{x:.1f}' y1='{Y(lo):.1f}' y2='{Y(hi):.1f}' stroke='{FAMILY(c)}' stroke-width='2' opacity='0.5'/>")
        yh = Y(v["hidden_pass_rate"])  # second mark: the hidden suite alone; a ring, so it reads as a different rule
        if yh != y: b.append(f"<line x1='{x:.1f}' x2='{x:.1f}' y1='{y:.1f}' y2='{yh:.1f}' stroke='{FAMILY(c)}' stroke-width='1' stroke-dasharray='3 3'/>")
        b.append(f"<circle class='complete-mark' cx='{x:.1f}' cy='{yh:.1f}' r='9' fill='none' stroke='{FAMILY(c)}' stroke-width='1.5'/>")
        b.append(config_marker(c, x, y, FAMILY(c)))
        lab = f"{DISP(c)} {v['task_complete']}/{v['n']} complete ({v['hidden_pass']}/{v['n']} hidden){' *' if v['cost_kind'] == 'proxy' else ''}"
        ly = T - 24 - i * 22
        anchor = "end" if x + len(lab) * 6.6 > W - 10 else "start"
        b.append(f"<line class='leader' x1='{x:.1f}' x2='{x:.1f}' y1='{y - 8:.1f}' y2='{ly + 5:.1f}' stroke='{FAMILY(c)}' stroke-width='1' opacity='0.6'/>")
        b.append(text(x, ly, s=lab, size=11, anchor=anchor))
    b.append(text(L, H - 26, "Filled mark: task complete (hidden and the run's own visible suite both green). Ring: hidden suite only.", 11, fill=MUTED))
    b.append(text(L, H - 10, "Bars: 95% interval for task complete; a perfect score shows its lower bound. * Estimated from tokens.", 11, fill=MUTED))
    return svg(W, H, b)


def bars(title, rows, fmt, note, W=360, L=None, R=8, low_start=None, values=None, cached=None,
         responsive=False):
    """Compact horizontal desktop rows; phones stack values below their bars."""
    import textwrap
    if responsive:
        phone = bars(title, rows, fmt, note, low_start=low_start, values=values, cached=cached)
        phone = phone.replace("<svg ", "<svg class='bar-phone' ", 1)
        mx = max(r[1] for r in rows) or 1
        value_text = values if values is not None else [fmt(r[1]) for r in rows]
        value_width = max(len(str(v)) for v in value_text)
        wide = [f'<div class="bar-wide" style="--bar-value-width:{value_width}ch"><b class="bar-title">{escape(title)}</b>']
        for i, (label, v, col, hollow) in enumerate(rows):
            if i == low_start:
                wide.append('<b class="bar-divider">Low context</b>')
            value = value_text[i]
            style = f"--bar-color:{col};--bar-width:{100 * v / mx:.3f}%"
            cls = "bar-fill" + (" bar-hollow" if hollow else "") + (" bar-uncached" if cached is not None else "")
            fill = f'<span class="{cls}" style="{style}">'
            if cached is not None:
                fill += f'<span class="bar-cached" style="width:{100 * cached[i]:.3f}%"></span>'
            wide.append(f'<div class="bar-row"><span class="bar-name">{escape(label)}</span>'
                        f'<span class="bar-track">{fill}</span></span>'
                        f'<span class="bar-value">{escape(str(value))}</span></div>')
        if note: wide.append(f'<p class="bar-note">{escape(note)}</p>')
        return phone + "".join(wide) + '</div>'
    label_lines = [textwrap.wrap(r[0], 20, break_long_words=True, break_on_hyphens=False) for r in rows]
    L = min(140, max(90, max(len(line) for lines in label_lines for line in lines) * 6.2 + 12))
    title_lines = textwrap.wrap(title, 45)
    note_lines = textwrap.wrap(note, 55)
    T, step, bh = 22 + 18 * len(title_lines), 62, 22
    H = T + len(rows) * step + 18 * len(note_lines) + 12 + (24 if low_start is not None else 0)
    mx = max(r[1] for r in rows) or 1
    b = [text(8, 20 + i * 18, line, 13, weight="600") for i, line in enumerate(title_lines)]
    for i, (lab, v, col, hollow) in enumerate(rows):
        if i == low_start:
            b.append(text(8, T + i * step + 12, "Low context", 11, fill=MUTED, weight="600"))
        y = T + i * step + (24 if low_start is not None and i >= low_start else 0)
        for j, line in enumerate(label_lines[i]):
            b.append(text(8, y + 15 + j * 14, line, 11, fill=INK))
        width = max(1, v / mx * (W - L - R))
        opacity = " fill-opacity='.35'" if cached is not None else ""
        b.append(f"<rect x='{L}' y='{y}' width='{width:.1f}' height='{bh}' fill='{PLATE if hollow else col}' stroke='{col}' stroke-width='{2 if hollow else 0}'{opacity}/>")
        if cached is not None:
            b.append(f"<rect x='{L}' y='{y}' width='{width * cached[i]:.1f}' height='{bh}' fill='{col}'/>")
        b.append(text(L, y + 42, values[i] if values else fmt(v), 11, fill=INK))
    start = H - 12 - (len(note_lines) - 1) * 16
    b.extend(text(8, start + i * 16, line, 10, fill=MUTED) for i, line in enumerate(note_lines))
    return svg(W, H, b)


def all_configs(s):
    return [(c, v, "-fast" in c) for c, v in {**s["configs"], **{c: v for c, v in (s.get("exploratory") or {}).items() if c not in configs.CHART_HIDDEN}}.items()]


def ladder(ds, s, set_="main ladder"):
    """[(config, dataset row, hollow)] for one set: the 12-problem x 5-repeat configs. Hollow = fast mode."""
    order = [c for c, _, _ in all_configs(s)]  # page order, until the registry owns it
    rows = [(r["config"], r, "-fast" in r["config"]) for r in ds["rows"] if r["source"] == "main" and r["set"] == set_]
    return sorted(rows, key=lambda x: (configs.low_context(x[0]), order.index(x[0])))


def cost_tokens_chart(s, ds=None):
    """Total $ for the 60 function-track calls, and $ per 1,000 tokens processed (input plus output), per config. Reads the dataset."""
    rows = ladder(ds or dataset.read(), s)
    low_start = next((i for i, (c, _, _) in enumerate(rows) if configs.low_context(c)), None)
    tot = [(r["display"] + (" *" if r["cost_kind"] == "proxy" else ""), r["spend"], FAMILY(c), x) for c, r, x in rows]
    per = [(r["display"] + (" *" if r["cost_kind"] == "proxy" else ""), r["usd_per_1k_tokens"], FAMILY(c), x) for c, r, x in rows]
    a = bars(f'Total $: {configs.set_label("main ladder")}', tot, dataset.usd,
             "Solid: normal speed. Hollow: fast mode. * Codex cost is estimated. Claude cost is measured.", low_start=low_start)
    b = bars("$ per 1,000 tokens processed (input + output, mean per call)", per, dataset.usd,
                "Cached input costs less per token. * Codex cost is estimated.", low_start=low_start)
    return a, b


TOKEN_IN = ["luna-low", "luna-low-bare", "haiku-low", "sonnet-medium"]


def token_in_chart(s, ds=None):
    allc = {c: r for c, r, _ in ladder(ds or dataset.read(), s)}
    lab = {"luna-low": "luna-low, Codex's normal prompt", "luna-low-bare": "luna-low, trimmed prompt", "haiku-low": "haiku-low", "sonnet-medium": "sonnet-medium"}
    order = sorted([c for c in TOKEN_IN if c in allc], key=configs.low_context)
    rows = [(lab[c], allc[c]["tokens_in_mean"], FAMILY(c), "-fast" in c) for c in order]
    low_start = next((i for i, c in enumerate(order) if configs.low_context(c)), None)
    return bars(f'Mean input per call: {configs.set_label("main ladder")}', rows, lambda v: f"{v:,.0f}",
                f"Includes cached input. Tools were off. Codex includes ~{HOST_AGENTS_MD} host AGENTS.md tokens.", low_start=low_start)


def check_design(s):
    """Chart titles and notes state the design (12 problems x 5 attempts = 60 calls per config, 10 per rung, 5 per cell). Fail if the data differ."""
    bad = [c for c, v, _ in all_configs(s) if v["n"] != 60 or any(r["n"] != 10 for r in v["by_rung"].values())]
    if bad or len(s["problems"]) != 12:
        raise SystemExit(f"chart text assumes 12 problems, 60 calls per config and 10 per rung; check {bad or 'the problem count'}")


def harness_chart(s):
    """Slope chart: the same two configs on Claude's one-shot bench and on Codex's bench (vendor agent CLIs)."""
    f = s.get("facts") or {}
    if "hb_claude_luna_low" not in f: return None
    W, H, L, R, T, B = 350, 280, 44, 112, 50, 50
    cols = [(L + 42, "Claude's bench"), (W - R - 20, "Codex's bench")]
    cells = {c: [tuple(map(int, f[f"hb_{h}_{c.replace('-', '_')}"].split("/"))) for h in ("claude", "codex")] for c in ("haiku-low", "luna-low")}
    Y = lambda p: H - B - (p - 0.5) / 0.5 * (H - T - B)
    b = [text(8, 24, f"Same models, two benches: passes out of {cells['luna-low'][0][1]}", 14, weight="600")]
    for p in (0.5, 0.75, 1.0):
        b += [f"<line x1='{L}' x2='{W - R + 10}' y1='{Y(p):.1f}' y2='{Y(p):.1f}' stroke='{GRID}'/>", text(L - 8, Y(p) + 4, f"{100 * p:.0f}%", 11, "end", MUTED)]
    for x, lab in cols:
        b.append(text(x, H - B + 22, lab, 12, "middle", MUTED))
    for c, pts in cells.items():
        xy = [(x, Y(k / n)) for (x, _), (k, n) in zip(cols, pts)]
        b.append(f"<line x1='{xy[0][0]:.1f}' y1='{xy[0][1]:.1f}' x2='{xy[1][0]:.1f}' y2='{xy[1][1]:.1f}' stroke='{FAMILY(c)}' stroke-width='3'/>")
        for (x, y), (k, n), side in zip(xy, pts, ("end", "start")):
            b += [f"<circle cx='{x:.1f}' cy='{y:.1f}' r='6' fill='{FAMILY(c)}'/>", text(x + (-12 if side == "end" else 12), y + 4, str(k), 12, side, weight="600")]
        gain = pts[1][0] - pts[0][0]
        b.append(text(xy[1][0] + 32, xy[1][1] + 4, f"{DISP(c)} (+{gain})", 12, fill=FAMILY(c), weight="600"))
    return svg(W, H, b)


def build(ds=None, names=None):
    """{file name: SVG text or None}, using only the dataset."""
    ds = ds or dataset.read(); s = dataset.view(ds)
    check_design(s)
    renderers = {"pareto.svg": lambda: pareto_chart(s), "hero.svg": lambda: explorer_svg(ds["explorer"], standalone=True),
                 "cost_time.svg": lambda: cost_time_chart(s), "pass_by_rung.svg": lambda: rung_chart(s, ds),
                 "heatmap.svg": lambda: heatmap(s), "token_floor.svg": lambda: floor_chart(s),
                 "agentic.svg": lambda: agentic_chart(s), "token_in.svg": lambda: token_in_chart(s, ds),
                 "harness_bias.svg": lambda: harness_chart(s)}
    charts = {name: draw() for name, draw in renderers.items() if names is None or name in names}
    if names is None or names & {"cost_total.svg", "cost_per_1k.svg"}:
        total, per = cost_tokens_chart(s, ds)
        charts.update({k: v for k, v in (("cost_total.svg", total), ("cost_per_1k.svg", per))
                       if names is None or k in names})
    # Inline report charts inherit the page bundle; standalone files carry it.
    return {name: body.replace(">", ">" + token_style(), 1)
            if body and name != "hero.svg" else body for name, body in charts.items()}


def main():
    os.makedirs(OUT, exist_ok=True)
    charts = build()
    for name, body in charts.items():
        if body: open(os.path.join(OUT, name), "w").write(body)
    print("charts ->", os.path.relpath(OUT, ROOT), ", ".join(n for n, b in charts.items() if b))




def explorer_cost_label(r):
    return {"measured": "measured", "proxy": "token-estimate", "unmetered": "unmetered"}[r["cost_kind"]]


def explorer_colour(r, facet="vendor"):
    key = (r["model_short"] if facet == "model" else r["effort"] if facet == "effort" else r["mode"] if facet == "mode" else
           "codex-old" if r["family"] == "Codex" and r["generation"] == "5.6" else r["family"].lower())
    if facet == "effort": key = "effort-" + key
    return f"var(--data-{key})"


def explorer_marker(r, x, y, radius=6):
    """Vendor shape, effort size, mode fill. All paint comes from tokens."""
    col = explorer_colour(r)
    attrs = f'fill="{PLATE if r["mode"] in ("fast", "bare") else col}" stroke="{col}" stroke-width="2"'
    if r["mode"] == "bare": attrs += ' stroke-dasharray="3 2"'
    if r["mode"] == "pipeline": return f'<rect x="{x-radius:.2f}" y="{y-radius:.2f}" width="{2*radius}" height="{2*radius}" {attrs}/>'
    if r["family"] == "Codex": return f'<path d="M{x:.2f} {y-radius:.2f}l{radius} {radius}l{-radius} {radius}l{-radius} {-radius}Z" {attrs}/>'
    if r["family"] == "Grok": return f'<path d="M{x:.2f} {y-radius:.2f}l{radius} {2*radius}h{-2*radius}Z" {attrs}/>'
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" {attrs}/>'


def explorer_label_position(q, label, placed, points, left, right, top, bottom):
    """Nudge vertically in a stable order; avoid labels and every point."""
    width = len(label) * 7
    x = max(left, min(right-width, q[0]+14))
    base = max(top+14, min(bottom-4, q[1]-14))
    candidates = [base]
    for n in range(1, math.ceil((bottom-top)/18)+1):
        candidates.extend((base+n*18, base-n*18))
    best, best_score = (x, base, width), math.inf
    for y in candidates:
        if not top+14 <= y <= bottom-4: continue
        overlaps = sum(x < px+pw+6 and px < x+width+6 and abs(py-y) < 18 for px,py,pw in placed)
        hits = sum(x-9 <= px <= x+width+9 and y-22 <= py <= y+10 for px,py in points)
        score = overlaps + hits
        if score < best_score:
            best, best_score = (x,y,width), score
            if not score: break
    return best


def explorer_svg(exp, standalone=False):
    """The default view, pre-rendered for no-JS readers and the OG source."""
    st = next(s for s in exp["sets"] if s["id"] == exp["default_set"])
    rows = [r for r in exp["rows"] if r["key"] in st["rows"] and r["cost_kind"] != "unmetered" and r["usd_per_pass"] is not None]
    ext = st["views"]["list"]["extents"]; membership = st["views"]["list"]["front"]["membership"]
    W,H,L,R,T,B = 760,480,90,30,36,410
    lo,hi = ext["cost"]; p0,p1 = ext["pass_rate"]
    X = lambda v: L + math.log(v/lo)/math.log(hi/lo)*(W-L-R)
    Y = lambda v: B - (v-p0)/(p1-p0)*(B-T)
    b = ['<title>Cost, pass rate and speed: default cost versus pass view</title>',
         '<desc>Ringed configs are strict Pareto trade-offs. All measurements and intervals come from the embedded dataset.</desc>']
    for v in log_ticks(lo,hi):
        b += [f'<path class="ex-grid" d="M{X(v):.2f} {T}V{B}"/>',text(X(v),B+26,dataset.usd(v,tick=True),12,"middle",MUTED)]
    for i in range(math.ceil(p0*10),11):
        v=i/10
        b += [f'<path class="ex-grid" d="M{L} {Y(v):.2f}H{W-R}"/>',text(L-10,Y(v)+4,f'{100*v:.0f}%',12,"end",MUTED)]
    frontier = sorted([r for r in rows if membership[r['key']]['on_frontier']],key=lambda r:r['usd_per_pass'])
    if frontier:
        d='M'+f'{X(frontier[0]["usd_per_pass"]):.2f} {B}'
        for r in frontier: d+=f'H{X(r["usd_per_pass"]):.2f}V{Y(r["pass_rate"]):.2f}'
        d+=f'H{W-R}'
        b += [f'<path class="ex-shade" d="{d}V{B}Z"/>',f'<path class="ex-front" d="{d}"/>']
    positions={r['config']:(X(r['usd_per_pass']),Y(r['pass_rate'])) for r in rows}
    for r in rows:
        x,y=positions[r['config']]; col=explorer_colour(r)
        if r['fast_twin'] in positions:
            tx,ty=positions[r['fast_twin']]
            b.append(f'<path class="ex-trail" stroke="{col}" stroke-dasharray="3 3" d="M{tx:.2f} {ty:.2f}L{x:.2f} {y:.2f}"/>')
        ci=r['ci95_plot']
        b.append(f'<path class="ex-ci" stroke="{col}" d="M{x:.2f} {Y(ci[0]):.2f}V{Y(ci[1]):.2f}"/>')
        title=f'{r["display"]}: {r["passes"]}/{r["n"]}, {dataset.usd(r["usd_per_pass"])} per pass ({explorer_cost_label(r)}), {r["median_s"]:g} s; {r["coverage_note"]}'
        b.append(f'<g class="ex-point" data-key="{escape(r["key"])}" tabindex="0" role="button" aria-label="{escape(title)}"><title>{escape(title)}</title>')
        if membership[r['key']]['on_frontier']: b.append(f'<circle class="ex-ring" cx="{x:.2f}" cy="{y:.2f}" r="11"/>')
        b += [explorer_marker(r,x,y),'</g>']
    # Match the interactive label pass, including winner picks and point clearance.
    labels, placed = [], []
    for r in rows:
        if not (membership[r['key']]['on_frontier'] or r['winner_pick']): continue
        q = positions[r['config']]
        same = next((l for l in labels if math.hypot(l[0][0]-q[0], l[0][1]-q[1]) < 1), None)
        if same: same[1].append(r['display'])
        else: labels.append((q, [r['display']]))
    for q,names in labels:
        label = f'{len(names)} tied at this point' if len(names)>1 else names[0]
        x,y,w = explorer_label_position(q,label,placed,positions.values(),L,W-R,T,B)
        placed.append((x,y,w))
        b += [f'<path class="ex-leader" d="M{q[0]:.2f} {q[1]:.2f}L{x:.2f} {y-4:.2f}"/>',
              text(x,y,label,12).replace('<text ', '<text class="ex-label" ', 1)]
    b += [text((L+W-R)/2,H-18,'$ per pass (log) · left is cheaper',12,'middle',MUTED),text(22,(T+B)/2,'Pass rate · up is better',12,'middle',MUTED,rotate=-90)]
    if standalone:
        tokens = token_style()
        paint = ".ex-grid{fill:none;stroke:var(--data-grid)}.ex-front{fill:none;stroke:var(--frontier);stroke-dasharray:5 4}.ex-shade{fill:var(--data-beaten)}.ex-ci{fill:none;stroke-width:1.5;opacity:.35}.ex-ring{fill:none;stroke:var(--frontier);stroke-width:2}.ex-trail{fill:none;opacity:.5}.ex-leader{fill:none;stroke:var(--muted);stroke-width:1}.ex-svg{background:var(--panel)}"
        b.insert(0,tokens+"<style>"+paint+"</style>")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" class="ex-svg">'+''.join(b)+'</svg>')


def explorer_panels(exp):
    """Static by-model panels; JS follows the selected set and filters."""
    st = next(s for s in exp["sets"] if s["id"] == exp["default_set"])
    rows = [r for r in exp["rows"] if r["key"] in st["rows"] and r["cost_kind"] != "unmetered" and r["usd_per_pass"] is not None]
    view = st["views"]["list"]["front"]; out=[]
    for panel,stat in view["panels"].items():
        group = [r for r in rows if r["panel"] == panel]
        if not group: continue
        ext=stat["extents"]; lo,hi=ext["cost"]; p0,p1=ext["pass_rate"]
        X=lambda v: 25+math.log(v/lo)/math.log(hi/lo)*190
        Y=lambda v: 140-(v-p0)/(p1-p0)*115
        fr=sorted([r for r in rows if view["membership"][r["key"]]["on_frontier"]],key=lambda r:r["usd_per_pass"])
        d=""
        for i,r in enumerate(fr): d+=("H" if i else "M")+f'{X(r["usd_per_pass"]):.2f}'+("V" if i else " ")+f'{Y(r["pass_rate"]):.2f}'
        if d: d+='H240'
        b=[f'<path class="ex-shade" d="{d}V160H{X(fr[0]["usd_per_pass"]):.2f}Z"/><path class="ex-front" d="{d}"/>'] if d else []
        for r in rows:
            if r not in group: b.append(f'<circle class="ex-ghost" cx="{X(r["usd_per_pass"]):.2f}" cy="{Y(r["pass_rate"]):.2f}" r="2"/>')
        normal=sorted([r for r in group if r['mode']=='normal'],key=lambda r: {'low':0,'medium':1,'high':2,'xhigh':3}.get(r['effort'],4))
        if len(normal)>1: b.append('<polyline class="ex-trail" fill="none" stroke="'+explorer_colour(normal[0])+'" points="'+' '.join(f'{X(r["usd_per_pass"]):.2f},{Y(r["pass_rate"]):.2f}' for r in normal)+'"/>')
        for r in group:
            x,y=X(r['usd_per_pass']),Y(r['pass_rate'])
            b += [f'<g data-key="{escape(r["key"])}"><title>{escape(r["display"])} · {explorer_cost_label(r)}</title>',explorer_marker(r,x,y),text(min(220,x+10),max(14,y-10),{'low':'L','medium':'M','high':'H','xhigh':'XH'}.get(r['effort'],'D'),12),'</g>']
        out.append(f'<div class="card"><h4>{escape(panel)}</h4><p class="ex-meta">{stat["on_frontier"]} of {stat["total"]} on frontier · {stat["beaten"]} beaten</p><svg viewBox="0 0 240 160" role="img"><title>{escape(panel)} detail</title>{"".join(b)}</svg></div>')
    return ''.join(out)


def explorer_radars(exp):
    st=next(s for s in exp['sets'] if s['id']==exp['default_set']); ext=st['views']['list']['extents']
    rows=[r for r in exp['rows'] if r['key'] in st['rows']]; lo,hi=ext['cost']; p0,p1=ext['pass_rate']; tmax=ext['median_s'][1]; out=[]
    def point(i,v):
        a=-math.pi/2+i*2*math.pi/3
        return f'{100+math.cos(a)*60*v:.2f},{85+math.sin(a)*60*v:.2f}'
    for r in rows:
        b=[]
        for v in (.33,.66,1): b.append(f'<polygon class="ex-grid" fill="none" points="{" ".join(point(i,v) for i in range(3))}"/>')
        for i,label in enumerate(('pass','cheap','fast')):
            x,y=map(float,point(i,1.3).split(',')); b.append(text(x,y+4,label,12,'middle'))
        if r['cost_kind']!='unmetered' and r['usd_per_pass'] is not None:
            values=[(r['pass_rate']-p0)/(p1-p0),1-math.log(r['usd_per_pass']/lo)/math.log(hi/lo),1-r['median_s']/tmax]
            b.append(f'<polygon fill="{explorer_colour(r)}" fill-opacity=".16" stroke="{explorer_colour(r)}" points="{" ".join(point(i,max(.02,min(1,v))) for i,v in enumerate(values))}"/>')
        else: b.append(text(100,88,'cost unavailable',12,'middle'))
        out.append(f'<div class="card ex-radar" data-key="{escape(r["key"])}"><h4>{escape(r["display"])}</h4><svg viewBox="0 0 200 180" role="img"><title>{escape(r["display"])} normalised radar</title>{"".join(b)}</svg><p class="ex-meta">{r["passes"]}/{r["n"]} · {dataset.usd(r["usd_per_pass"])} ({explorer_cost_label(r)}) · {r["median_s"]:g} s</p></div>')
    return ''.join(out)


if __name__ == "__main__":
    main()
