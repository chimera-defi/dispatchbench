"""Widgets for the page (results/report/page.html), all drawn from results/dataset.json: the two Pareto scatters, the
problem × config grid, the token-floor bars and the short result table. Inline SVG and HTML that take their colours
from the page's CSS variables, so both themes work. Standard library only."""
import html, json, math, os, re

from analysis import configs, dataset
from html.parser import HTMLParser
from analysis.charts import FAMILY, MIN_PASS
from analysis.labels import TESTS, DISP, pshort, plabel, plabel_html

# Plot order and family colour (a CSS variable of the page). luna-high is the exploratory full-ladder run.
ORDER = ["haiku-low", "haiku-medium", "haiku-high", "sonnet-medium", "sol61-medium", "luna-high", "luna-medium", "luna-low", "luna-low-bare",
         "astra-medium", "astra-medium-fast", "sol61-high", "sol61-high-fast", "sol56-high", "luna56-high", "luna56-low"]
FAM = lambda c: "var(--claude)" if c.startswith("haiku") else "var(--sonnet)" if c.startswith("sonnet") else "var(--codex56)" if c.startswith(("sol56", "luna56")) else "var(--codex)"
NS = 'xmlns="http://www.w3.org/2000/svg"'


def every(s):
    return {**s["configs"], **s["exploratory"]}


def front(pts, better):
    """Points no other point beats on both axes. better(a, b) is True when a is at least as good as b on both."""
    return [p for p in pts if not any(q is not p and better(q, p) and (q["x"], q["y"]) != (p["x"], p["y"]) for q in pts)]


def speed_dominates(a, b):
    """Cost must not rise; speed changes below both 0.5 s and 5% count as ties."""
    tolerance = min(0.5, b["x"] * 0.05)
    return (a["y"] < b["y"] and a["x"] <= b["x"] + tolerance or
            a["y"] == b["y"] and a["x"] <= b["x"] - tolerance)


def esc(t):
    return html.escape(str(t))


# Marker shape by model (colour stays the vendor): read the chart without a label on every point.
def SHAPE(c):
    if "luna" in c:
        return "triangle-down" if "high" in c else "triangle-right" if "medium" in c else "triangle"
    return "circle" if c.startswith("haiku") else "square" if c.startswith("sonnet") else "star" if c.startswith("astra") else "diamond"


def config_marker(c, x, y, col=None, k=1.0):
    """Across plots, hollow means fast mode, dashed means a stripped prompt."""
    col = col or FAM(c)
    return marker(SHAPE(c), x, y, "var(--panel)" if "-fast" in c else col, col, "bare" in c, k)


def point_category(c):
    if "+" in c: return "pipelines"
    if c.endswith("-fast"): return "fast"
    return "exploratory" if c == "luna-high" or c not in ORDER else "main"


def marker(kind, x, y, fill, stroke, dash=False, k=1.0):
    a = f' fill="{fill}" stroke="{stroke}" stroke-width="2.5"' + (' stroke-dasharray="3 2"' if dash else "")
    if kind == "circle": return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{6.5 * k:.1f}"{a}/>'
    if kind == "square": return f'<rect x="{x - 6 * k:.1f}" y="{y - 6 * k:.1f}" width="{12 * k:.1f}" height="{12 * k:.1f}"{a}/>'
    if kind == "triangle": v = [(0, -8.5), (7.5, 5.5), (-7.5, 5.5)]
    elif kind == "triangle-down": v = [(0, 8.5), (7.5, -5.5), (-7.5, -5.5)]
    elif kind == "triangle-right": v = [(8.5, 0), (-5.5, 7.5), (-5.5, -7.5)]
    elif kind == "diamond": v = [(0, -8.5), (8.5, 0), (0, 8.5), (-8.5, 0)]
    else: v = [(r * math.sin(math.radians(36 * i)), -r * math.cos(math.radians(36 * i))) for i, r in enumerate([9.5, 4] * 5)]
    return f'<polygon points="{" ".join(f"{x + dx * k:.1f},{y + dy * k:.1f}" for dx, dy in v)}"{a}/>'


def scatter(pts, fr, X, Y, xt, yt, xlab, ylab, corner, labels, W=560, H=380, L=84, R=16, T=14, B=322, extra="", stat=None, variant=None, free_pts=()):
    """pts: dicts with c, x, y, w (whisker (axis, lo, hi) or None), tip, hollow. fr: the frontier path. Only frontier points
    get a text label; every point is in the key beside the chart, and hovering (or tapping) a point or a key row shows its tip."""
    g = [f'<svg viewBox="0 0 {W} {H}" width="100%" {NS} role="img" aria-label="{esc(ylab)} against {esc(xlab)}, Pareto frontier in purple; the key lists every point">']
    for i, (v, t) in enumerate(xt):
        # Thin labels from the right on mobile, retaining the inset final label.
        skip = " tick-skip" if (len(xt) - 1 - i) % 2 else ""
        anchor = "end" if i == len(xt) - 1 else "middle"
        g.append(f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{B}" stroke="var(--line)"/><text x="{X(v):.1f}" y="{B + 18}" text-anchor="{anchor}" class="axis x-tick{skip}">{t}</text>')
    for v, t in yt:
        g.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="var(--line)"/><text x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end" class="axis">{t}</text>')
    g.append(f'<text x="{(L + W - R) / 2}" y="{H - 14}" text-anchor="middle" class="axis">{esc(xlab)}</text>')
    g.append(f'<text x="16" y="{(T + B) / 2}" text-anchor="middle" class="axis" transform="rotate(-90 16 {(T + B) / 2})">{esc(ylab)}</text>')
    g.append(f'<text x="{L + 10}" y="{T + 18 if corner.startswith("↖") else B - 10}" class="better">{corner}</text>')
    g.append(f'<path d="{fr}" fill="none" stroke="var(--frontier)" stroke-width="4" stroke-dasharray="9 6" stroke-linejoin="round"/>' + extra)
    for p in sorted(pts, key=lambda p: p["on"]):  # frontier points drawn last, on top
        px, py, col = X(p["x"]), Y(p["y"]), p.get("col") or FAM(p["c"])
        g.append(f'<g class="pt" {point_attrs(p)}>')
        if p["w"]:
            ax, lo, hi = p["w"]
            if ax == "x": g.append(f'<line x1="{X(lo):.1f}" x2="{X(hi):.1f}" y1="{py:.1f}" y2="{py:.1f}" stroke="{col}" stroke-width="2.5" stroke-opacity=".4"/>')
            else: g.append(f'<line x1="{px:.1f}" x2="{px:.1f}" y1="{Y(lo):.1f}" y2="{Y(hi):.1f}" stroke="{col}" stroke-width="2" stroke-opacity=".3"/>')
        if p["on"]: g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="13" fill="none" stroke="var(--frontier)" stroke-width="3"/>')
        g.append(marker(p.get("shape", SHAPE(p["c"])), px, py, "var(--panel)" if p["hollow"] else col, col, p.get("dash")))
        g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="14" fill="transparent"/></g>')  # hover target
    cx, cy = L + 10, T + 18 if corner.startswith("↖") else B - 10
    walls = path_boxes(fr) + [(cx, cy - LH + 3, cx + CW * len(corner), cy + 3)]
    for p, (x, y, a) in place([p for p in pts if p["on"]], X, Y, labels, (L, W - 2, T - 6, B - 2), walls, also=pts):
        if p["lead"]: g.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="var(--muted)" stroke-width="1"/>' % p["lead"])
        g.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{a}" class="lbl on" data-cat="{point_category(p["c"])}" data-set="{p.get("set", "main")}">{esc(p.get("name", p["c"]))}</text>')
    g.append("</svg>")
    if variant:
        return f'<div class="cvariant v-{variant}"><div class="cplot">{"".join(g)}{free_strip(free_pts, stat)}</div>{key(pts + list(free_pts), stat)}</div>'
    return f'<div class="cwrap"><div class="cplot">{"".join(g)}</div>{key(pts, stat)}<div class="ctip" hidden></div></div>'


def point_attrs(p):
    return (f'data-c="{esc(p["c"])}" data-cat="{point_category(p["c"])}" '
            f'data-set="{p.get("set", "main")}" data-tip="{esc(p["tip"])}"')


def point_icon(p):
    col = p.get("col") or FAM(p["c"])
    return (f'<svg viewBox="-10 -10 20 20" {NS} aria-hidden="true">'
            + marker(p.get("shape", SHAPE(p["c"])), 0, 0, "var(--panel)" if p["hollow"] else col, col, p.get("dash"), .8) + '</svg>')


def point_values(p, stat):
    metric = f'{p["x"]:.1f} s' if stat == "speed" else f'{100 * p["y"]:.0f}%'
    usd = p["y"] if stat == "speed" else p["x"]
    value = f'{metric} · {dataset.usd(usd)}'
    if p.get("free_mode") and p["normal_usd"] != p["free_usd"]:
        value += f' · saved {dataset.usd(p["saved_usd"])}'
    return value


def free_strip(pts, stat):
    """Zero-cost configs ranked by the chart's other metric, outside its log plot."""
    if not pts: return ""
    ranked = sorted(pts, key=lambda p: (p["x"] if stat == "speed" else -p["y"], p["c"]))
    rows = [f'<li tabindex="0" {point_attrs(p)}>{point_icon(p)}<span class="n">{esc(p["name"])}</span>'
            f'<span class="v">{point_values(p, stat)}</span></li>' for p in ranked]
    metric = "fastest first" if stat == "speed" else "highest pass rate first"
    return f'<div class="free-quota"><p><b>Free with Codex quota:</b> {metric}</p><ol class="free-strip">{"".join(rows)}</ol></div>'


def key(pts, stat):
    """Every point grouped by the filter categories; only main starts expanded."""
    groups = []
    for cat in ("main", "fast", "pipelines", "exploratory"):
        rows = []
        for p in sorted((p for p in pts if point_category(p["c"]) == cat),
                        key=lambda p: (p["x"] if stat == "speed" else p["y"] * -1, p["y"] if stat == "speed" else p["x"])):
            nm = p.get("lname") or p.get("name", p["c"])
            rows.append(f'<li tabindex="0" {point_attrs(p)}{" class=on" if p["on"] else ""}>'
                        f'{point_icon(p)}<span class="n">{esc(nm)}</span><span class="v">{point_values(p, stat) if stat else ""}</span></li>')
        if rows:
            groups.append(f'<details class="key-group" data-cat="{cat}"{" open" if cat == "main" else ""}>'
                          f'<summary>{cat} ({len(rows)})</summary><ul class="ckey">{"".join(rows)}</ul></details>')
    return f'<div class="ckeys">{"".join(groups)}</div>'


CW, LH = 11, 21  # reserve room for the mobile 16px labels and their outlines
SPOTS = [(14, 5, "start"), (-14, 5, "end"), (0, -14, "middle"), (0, 26, "middle"), (14, -10, "start"), (14, 20, "start"),
         (-14, -10, "end"), (-14, 20, "end")]
# Far spots, joined to their dot by a thin leader line: rings at 45 and 75 units, every 30 degrees.
FAR = [(round(r * math.cos(a)), round(r * math.sin(a)) + 5, "start" if math.cos(a) > .3 else "end" if math.cos(a) < -.3 else "middle")
       for r in (45, 75, 110, 150) for a in (math.radians(d) for d in range(0, 360, 30))]


def path_boxes(d):
    """The frontier path (M x y, then H x / V y steps) as thin boxes, so labels keep off the line."""
    out, x, y = [], 0.0, 0.0
    for op, a, b in re.findall(r"([MHV])\s*([\d.]+)(?:\s+([\d.]+))?", d):
        if op == "M": x, y = float(a), float(b); continue
        nx, ny = (float(a), y) if op == "H" else (x, float(a))
        out.append((min(x, nx) - 3, min(y, ny) - 3, max(x, nx) + 3, max(y, ny) + 3)); x, y = nx, ny
    return out


def place(pts, X, Y, labels, box, walls=(), also=(), char_width=CW, label_height=LH):
    """Greedy label placement: frontier points first, each takes the first spot (its hand-set offset, then SPOTS) whose text
    box stays inside the plot and clears every dot and every label already placed; if none is clear, the least-overlapping."""
    x0, x1, y0, y1 = box
    dots = [(X(p["x"]) - (15 if p["on"] else 10), Y(p["y"]) - (15 if p["on"] else 10),
             X(p["x"]) + (15 if p["on"] else 10), Y(p["y"]) + (15 if p["on"] else 10)) for p in list(also) or pts]
    taken, out = list(walls), {}
    def rect(px, py, dx, dy, a, n):
        w = char_width * len(n); l = px + dx - (w if a == "end" else w / 2 if a == "middle" else 0)
        return (l, py + dy - label_height + 4, l + w, py + dy + 4)
    centres = [(X(p["x"]), Y(p["y"])) for p in list(also) or pts]
    def gap(r, x, y): return math.hypot(max(r[0] - x, 0, x - r[2]), max(r[1] - y, 0, y - r[3]))
    def hit(r, q): return max(0, min(r[2], q[2]) - max(r[0], q[0])) * max(0, min(r[3], q[3]) - max(r[1], q[1]))
    # A pipeline whose gate never fired sits on its single model's dot: label the dot once (the chart note says so).
    nm = {id(p): p.get("name", p["c"]) for p in pts}; skip = set()
    for i, p in enumerate(pts):
        for q in pts[i + 1:]:
            if abs(X(p["x"]) - X(q["x"])) < 4 and abs(Y(p["y"]) - Y(q["y"])) < 4 and nm[id(q)].startswith(nm[id(p)]):
                skip.add(id(q))
    def best(p, others):
        px, py, n = X(p["x"]), Y(p["y"]), nm[id(p)]; top = None
        for s in ([labels[p["c"]]] if p["c"] in labels else []) + SPOTS + FAR:
            r = rect(px, py, *s, n); led = s in FAR or p.get("label", False)
            out_of = (max(0, x0 - r[0]) + max(0, r[2] - x1) + max(0, y0 - r[1]) + max(0, r[3] - y1)) * 1000
            # text on text or on a dot is bad; an unled label closer to another dot than its own misnames it
            mine = gap(r, px, py); near = any(gap(r, *c) < mine - 2 for c in centres if c != (px, py))
            cost = out_of + 4 * sum(hit(r, q) for q in dots + others) + 400 * near + mine + 80 * led
            if top is None or cost < top[0]: top = (cost, s, r)
        return top
    order = [p for p in sorted(pts, key=lambda p: not p["on"]) if id(p) not in skip]; got = {}
    for p in order:
        got[id(p)] = best(p, taken + [g[2] for g in got.values()])
    for _ in range(6):  # repair pass: any label that now overlaps something (even one placed clear earlier) is re-seated
        for p in order:
            others = taken + [g[2] for k, g in got.items() if k != id(p)]
            if sum(hit(got[id(p)][2], q) for q in others) > 0 or sum(hit(got[id(p)][2], q) for q in dots) > 0:
                got[id(p)] = best(p, others)
    for p in order:
        _, s, r = got[id(p)]; dx, dy, a = s; px, py = X(p["x"]), Y(p["y"])
        lead = None
        if s in FAR or p.get("label"):  # line from the dot's edge to the nearest point of the label box
            qx, qy = min(max(px, r[0]), r[2]), min(max(py, r[1]), r[3]); d = math.hypot(qx - px, qy - py) or 1
            lead = (px + (qx - px) * 8 / d, py + (qy - py) * 8 / d, qx, qy)
        out[id(p)] = (dict(p, name=nm[id(p)], lead=lead), (px + dx, py + dy, a))
    return list(out.values())


def logscale(lo, hi, a, b):
    return lambda v: a + (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (b - a)


def tip(c, v):
    k = " (exploratory)" if c == "luna-high" else ""
    return (f"{DISP(c)}{k} [main ladder]: {v['passes']}/{v['n']} passed, {dataset.usd(v['usd_per_pass'])} per pass ({'estimated from tokens' if v['cost_kind'] == 'proxy' else 'measured bill'}), "
            f"median {v['latency_s']['median']:.1f} s")


FAST_PAIRS = [("sol61-high", "sol61-high-fast"), ("astra-medium", "astra-medium-fast")]


def fast_pairs(pts, X, Y):
    """A thin line from each default-tier config to its fast-mode twin (same model and effort, priority tier), so the cost of speed reads off the chart."""
    by = {p["c"]: p for p in pts}
    return "".join(f'<line x1="{X(by[a]["x"]):.1f}" y1="{Y(by[a]["y"]):.1f}" x2="{X(by[b]["x"]):.1f}" y2="{Y(by[b]["y"]):.1f}" '
                   f'data-cat="fast" data-from-cat="main" stroke="var(--codex)" stroke-width="1.5" stroke-opacity=".6"/>' for a, b in FAST_PAIRS if a in by and b in by)


def frontier_caption(s):
    """Explain the cost/pass-rate dominance using the eligible full-ladder frontier."""
    E = every(s); c = "luna-low"; v = E[c]
    pts = [{"c": c, "x": E[c]["usd_per_pass"], "y": E[c]["pass_at_1"]} for c in ORDER if point_category(c) != "exploratory"]
    fr = front(pts, lambda a, b: a["x"] <= b["x"] and a["y"] >= b["y"])
    dominators = [p for p in fr if p["x"] <= v["usd_per_pass"] and p["y"] > v["pass_at_1"]]
    if dominators:
        d = min(dominators, key=lambda p: (p["y"], p["x"]))["c"]; q = E[d]
        relation = "costs about the same" if math.isclose(q["usd_per_pass"], v["usd_per_pass"], rel_tol=.05) else "costs less"
        reason = (f'{DISP(c)} is off the frontier: {DISP(d)} {relation} '
                  f'({dataset.usd(q["usd_per_pass"], sig=3)} vs {dataset.usd(v["usd_per_pass"], sig=3)}) and passes more '
                  f'({q["passes"]}/{q["n"]} vs {v["passes"]}/{v["n"]}).')
    else:
        reason = f'{DISP(c)} has no cost/pass-rate dominator on the eligible frontier'
    return f'<p class="frontier-note">{esc(reason)} Hollow and exploratory points are left off the frontier.</p>'


def ladder_toggle(render, s):
    normal, fr = render(s, free=False)
    free, _ = render(s, free=True)
    rescue_normal, _ = render(s, free=False, problem_set="rescue")
    rescue_free, _ = render(s, free=True, problem_set="rescue")
    note = ('<p class="repair-note">Hollow = pipeline, using the builder’s shape; filled = single model. '
            'Savings per pass appear in the key and tooltip. The log plot shows paid configs; free configs are ranked below it.</p>')
    main_categories = {point_category(c) for c in ORDER}
    filters = '<div class="category-filter" role="group" aria-label="Point categories">' + "".join(
        ('<label>' if cat in main_categories else f'<label class="disabled" title="only on the {configs.set_label("rescue set")}">')
        + f'<input type="checkbox" data-cat="{cat}" checked' + ('' if cat in main_categories else ' disabled')
        + f'> {cat}</label>' for cat in ("main", "fast", "pipelines", "exploratory")) + '</div>'
    set_name = render.__name__ + "-set"
    sets = (f'<div class="set-filter" role="group" aria-label="Problem set">'
            f'<label><input type="radio" name="{set_name}" value="main" checked> Main ladder</label>'
            f'<label><input type="radio" name="{set_name}" value="rescue"> {configs.set_label("rescue set", capital=True)}</label></div>')
    rescue_n = next(iter(rescue_arms(s).values()))["n"]
    return ('<div class="cwrap"><label class="cost-toggle"><input type="checkbox"> Codex is free (subscription quota)</label>'
            + sets + filters + note + '<div class="cset s-main">' + normal + free + frontier_caption(s) + '</div>'
            + f'<div class="cset s-rescue"><p class="set-note">{configs.set_label("rescue set", capital=True)}: '
            + f'{rescue_n} attempts, shown apart from the main ladder.</p>'
            + rescue_normal + rescue_free + '</div><div class="ctip" hidden></div></div>'), fr


def quota_tip(normal, free, saving):
    return (f'Normal: {dataset.usd(normal)} per pass; Codex free: {dataset.usd(free)} per pass '
            f'(saving {dataset.usd(saving)} per pass).')


def ladder_repairs(free, stat, arms=None):
    """All rescue configs, including baselines measured on this same subset."""
    pts = []
    for c, v in (arms if arms is not None else rescue_arms()).items():
        name = NAME.get(c) or " → ".join(DISP(part) for part in c.split("+"))
        pipeline = "+" in c
        builder = c.split("+", 1)[-1] if c.startswith("haiku-low-plan+") else c.split("+", 1)[0]
        usd = v["claude_usd_per_pass"] if free else v["usd_per_pass"]
        pts.append({"c": c, "name": name, "set": "rescue", "x": v["median_s"] if stat == "speed" else usd,
                    "y": usd if stat == "speed" else v["pass_rate"], "rate": v["pass_rate"], "hollow": pipeline,
                    "shape": SHAPE(builder), "w": None, "on": False, "free_mode": free,
                    "saved_usd": v["usd_saved_per_pass"], "normal_usd": v["usd_per_pass"], "free_usd": v["claude_usd_per_pass"],
                    "tip": f"{name}: {v['passes']}/{v['n']} passed. {dataset.usd(usd)} per pass. Median {v['median_s']:.1f} s. {configs.set_label('rescue set', capital=True)} only. "
                    + quota_tip(v["usd_per_pass"], v["claude_usd_per_pass"], v["usd_saved_per_pass"])
                    + (" (" + v["derived_note"] + ")" if "derived_note" in v else "")})
    return pts


def ladder_points(s, free, stat, problem_set):
    if problem_set == "rescue": return ladder_repairs(free, stat, rescue_arms(s))
    pts = []
    for c in ORDER:
        v = every(s)[c]; normal = v["usd_per_pass"]
        quota = v["claude_usd_per_pass"]
        usd = quota if free else normal
        w = (("x", v["latency_s"]["p25"], v["latency_s"]["p75"]) if "p25" in v["latency_s"] else None) if stat == "speed" else ("y", v["ci95"][0], v["ci95"][1])
        pts.append({"c": c, "name": DISP(c), "set": "main", "x": v["latency_s"]["median"] if stat == "speed" else usd,
                    "y": usd if stat == "speed" else v["pass_at_1"], "rate": v["pass_at_1"], "hollow": False, "w": w,
                    "saved_usd": v["usd_saved_per_pass"], "normal_usd": normal, "free_usd": quota, "free_mode": free,
                    "tip": tip(c, dict(v, usd_per_pass=usd)) + ". " + quota_tip(normal, quota, v["usd_saved_per_pass"])})
    return pts


def paid_points(pts, stat):
    axis = "y" if stat == "speed" else "x"
    return [p for p in pts if p[axis] > 0], [dict(p, on=False) for p in pts if p[axis] == 0]


def pass_cost(s, free=None, problem_set="main"):
    """Pass rate (up is better) against paid $ per pass, log (left is better)."""
    if free is None: return ladder_toggle(pass_cost, s)
    L, R, T, B, W = 84, 16, 14, 322, 560
    all_pts = ladder_points(s, free, "pass", problem_set)
    ymin = min(.6, math.floor(min(p["y"] for p in all_pts) * 10) / 10)
    pts, free_pts = paid_points(all_pts, "pass")
    cost_min = min(p["x"] for p in pts)
    lo = 5e-4 if cost_min >= 5e-4 else 10 ** math.floor(math.log10(cost_min))
    X = logscale(lo, 3e-1, L, W - R)
    Y = lambda v: B - (v - ymin) / (1.1 - ymin) * (B - T)
    eligible = [p for p in pts if not p["hollow"] and point_category(p["c"]) != "exploratory"]
    fr = sorted(front(eligible, lambda a, b: a["x"] <= b["x"] and a["y"] >= b["y"]), key=lambda p: p["x"])
    for p in pts:
        p["on"] = p in fr
        if p["w"]: p["w"] = ("y", max(ymin, p["w"][1]), p["w"][2])
    d = (f"M{X(fr[0]['x']):.1f} {B} V{Y(fr[0]['y']):.1f}" + "".join(f" H{X(p['x']):.1f} V{Y(p['y']):.1f}" for p in fr[1:]) + f" H{W - R}") if fr else ""
    xt = [(v, dataset.usd(v)) for v in (3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1) if v >= lo]
    yt = [(v / 100, f"{v}%") for v in range(round(ymin * 100), 101, 10)]
    lab = {"luna-low": (12, 16, "start"), "luna-medium": (12, -8, "start"), "luna-high": (12, 14, "start"), "haiku-low": (-14, 16, "end"),
           "haiku-medium": (14, 22, "start"), "sonnet-medium": (-14, -10, "end"), "sol61-medium": (0, 26, "middle"),
           "haiku-high": (14, 20, "start"), "luna56-high": (14, 5, "start")}
    return scatter(pts, d, X, Y, xt, yt, "$ per passing answer (log scale)", "pass rate", "↖ better", lab,
                   extra=fast_pairs(pts, X, Y), stat="pass", variant="free" if free else "normal", free_pts=free_pts), [p["c"] for p in fr]


def speed_cost(s, free=None, problem_set="main"):
    """Median seconds against paid $ per pass, log; frontier requires MIN_PASS."""
    if free is None: return ladder_toggle(speed_cost, s)
    L, R, T, B, W = 84, 16, 14, 462, 560
    all_pts = ladder_points(s, free, "speed", problem_set)
    xmax = math.ceil(max(p["w"][2] if p["w"] else p["x"] for p in all_pts) / 5) * 5
    X = lambda v: L + v / xmax * (W - R - L)
    pts, free_pts = paid_points(all_pts, "speed")
    cost_min = min(p["y"] for p in pts)
    lo = 5e-4 if cost_min >= 5e-4 else 10 ** math.floor(math.log10(cost_min))
    Y = logscale(lo, 3e-1, B, T)
    ok = [p for p in pts if p.get("rate", 0) >= MIN_PASS and not p["hollow"] and point_category(p["c"]) != "exploratory"]
    fr = sorted(front(ok, speed_dominates), key=lambda p: p["x"])
    for p in pts: p["on"] = p in fr
    d = (f"M{X(fr[0]['x']):.1f} {Y(fr[0]['y']):.1f}" + "".join(f" H{X(p['x']):.1f} V{Y(p['y']):.1f}" for p in fr[1:]) + f" H{W - R}") if fr else ""
    xt = [(v, f"{v} s") for v in range(5, xmax + 1, 5)]
    yt = [(v, dataset.usd(v)) for v in (3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1) if v >= lo]
    lab = {"luna-low": (0, -14, "middle"), "luna-medium": (14, 10, "start"), "haiku-low": (0, -20, "middle"), "luna-high": (14, -10, "start"),
           "haiku-medium": (14, 5, "start"), "sonnet-medium": (14, 4, "start"), "sol61-medium": (-14, -12, "end"),
           "luna56-high": (-14, 5, "end"), "luna56-low": (0, 26, "middle"), "haiku-high": (0, -14, "middle")}
    g = scatter(pts, d, X, Y, xt, yt, "median seconds per call (bar: middle half of calls)", "$ per pass (log)", "", lab,
                H=520, B=B, extra=fast_pairs(pts, X, Y), stat="speed", variant="free" if free else "normal", free_pts=free_pts)
    return g.replace("</svg>", f'<text x="{W - R - 6}" y="{T + 18}" text-anchor="end" class="better">↙ better</text></svg>', 1), [p["c"] for p in fr]


# Display names for rescue-set rows, used by every chart and table so a pipeline reads the same everywhere. luna-high on the hard
# set is the stripped harness (luna-high-bare); the name says so. Haiku in a pipeline reviews the answer and rewrites it if wrong.
from analysis.configs import RESCUE_NAMES as NAME
HARD_PTS = list(NAME.items())
SHORT = lambda n: n.replace("Haiku plan → ", "plan→").replace(" → Haiku if samples fail", "→H fail").replace(" → Haiku fixes all", "→H all").replace(" → retry if samples fail", "→retry")


def rescue_arms(ds=None):
    """Cached measured and derived arms, including their validated provenance."""
    return (ds or dataset.read())["rescue"]


def hard_pts(arms=None):
    a = arms if arms is not None else rescue_arms()
    return [{"c": c, "name": SHORT(n) if "→" in n else n, "set": "rescue", "col": "var(--frontier)" if "→" in n else FAM(c), "hollow": False, "w": None, "k": a[c]["pass_rate"],
             "usd": a[c]["usd_per_pass"], "sec": a[c]["median_s"],
             "tip": f"{n} [{configs.set_label('rescue set')}]: {a[c]['passes']}/{a[c]['n']} passed. {dataset.usd(a[c]['usd_per_pass'])} per pass. Median {a[c]['median_s']:.1f} s" + (" (" + a[c]["derived_note"] + ")" if "derived_note" in a[c] else "")} for c, n in HARD_PTS]


def hard_pass_cost(arms=None):
    """Rescue set: pass rate against $ per pass (log), single models and the Haiku pipelines; no intervals (n is small and post hoc)."""
    L, R, T, B, W = 84, 16, 14, 382, 560
    X = logscale(5e-4, 4e-1, L, W - R); Y = lambda v: B - (v - 0.55) / 0.5 * (B - T)
    pts = [dict(p, x=p["usd"], y=p["k"]) for p in hard_pts(arms)]
    fr = sorted(front(pts, lambda a, b: a["x"] <= b["x"] and a["y"] >= b["y"]), key=lambda p: p["x"])
    for p in pts: p["on"] = p in fr
    d = f"M{X(fr[0]['x']):.1f} {B} V{Y(fr[0]['y']):.1f}" + "".join(f" H{X(p['x']):.1f} V{Y(p['y']):.1f}" for p in fr[1:]) + f" H{W - R}"
    xt = [(v, dataset.usd(v)) for v in (1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1)]
    yt = [(v / 100, f"{v}%") for v in (55, 65, 75, 85, 95, 100)]
    lab = {"luna-high-bare": (14, 20, "start"), "haiku-low": (14, 5, "start"), "haiku-medium": (0, -16, "middle"),
           "sonnet-medium": (0, -14, "middle"), "sol61-medium": (0, 24, "middle"), "luna-high-bare+retry-on-fail": (-14, 28, "end"),
           "luna-high-bare+haiku-on-fail": (0, 24, "middle"), "luna-low+haiku-on-fail": (-14, 5, "end"),
           "luna-low+haiku-review-all": (14, 5, "start"), "luna-high-bare+haiku-review-all": (0, 22, "middle")}
    g = scatter(pts, d, X, Y, xt, yt, "$ per passing answer (log scale)", "pass rate", "↖ better", lab, H=440, B=B, stat="pass", extra=fast_pairs(pts, X, Y))
    return g, [p["c"] for p in fr]


def hard_speed_cost(arms=None):
    """Rescue set: median seconds against $ per pass (log); frontier among rows passing at least MIN_PASS."""
    L, R, T, B, W = 84, 16, 14, 462, 560
    X = lambda v: L + (v - 6) / 30 * (W - R - L); Y = logscale(8e-4, 4e-1, B, T)
    pts = [dict(p, x=p["sec"], y=p["usd"]) for p in hard_pts(arms)]
    ok = [p for p in pts if p["k"] >= MIN_PASS]
    fr = sorted(front(ok, speed_dominates), key=lambda p: p["x"])
    for p in pts: p["on"] = p in fr
    d = f"M{X(fr[0]['x']):.1f} {Y(fr[0]['y']):.1f}" + "".join(f" H{X(p['x']):.1f} V{Y(p['y']):.1f}" for p in fr[1:]) + f" H{W - R}"
    xt = [(v, f"{v} s") for v in (10, 15, 20, 25, 30, 35)]
    yt = [(v, dataset.usd(v)) for v in (1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1)]
    lab = {"luna-low": (-12, 5, "end"), "luna-high-bare": (14, 5, "start"), "haiku-low": (14, 1, "start"), "haiku-medium": (14, 5, "start"),
           "sonnet-medium": (14, 5, "start"), "sol61-medium": (-14, 4, "end"), "luna-high-bare+retry-on-fail": (-20, 28, "middle"),
           "luna-high-bare+haiku-on-fail": (12, 6, "start"), "luna-low+haiku-on-fail": (0, -16, "middle"),
           "luna-low+haiku-review-all": (0, -14, "middle"), "luna-high-bare+haiku-review-all": (-14, 5, "end")}
    g = scatter(pts, d, X, Y, xt, yt, "median seconds per call", "$ per pass (log)", "", lab, H=520, B=B, stat="speed", extra=fast_pairs(pts, X, Y))  # corner label goes top right: the bottom left is crowded
    return g.replace("</svg>", f'<text x="{W - R - 6}" y="{T + 18}" text-anchor="end" class="better">↙ better</text></svg>', 1), [p["c"] for p in fr]


def grid(s):
    """Problems (rows, by rung) × configs (columns); each cell is passes out of the attempts at that problem."""
    E = every(s); probs = sorted(s["problems"], key=lambda p: (s["problems"][p]["rung"], p))
    main = set(probs)
    hard = sorted({p for v in s["hard"].values() for p in v["by_problem"]})
    def cell(p, c):
        v = E.get(c) if p in main else s["hard"].get(c)
        cell = v["by_group"].get(p) if v else None
        return (cell["passes"], cell["n"]) if cell else (None, None)
    out = [f'<div class="grid" style="--n:{len(ORDER)};grid-template-columns:minmax(150px,auto) repeat({len(ORDER)},minmax(40px,1fr))">', '<div class="h m">problem</div>']
    out += [f'<div class="h{" fast" if c.endswith("-fast") else ""}">{esc(DISP(c))}</div>' for c in ORDER]
    for p in probs + hard:
        if p == hard[0]: out.append(f'<div class="set-separator" style="grid-column:1 / -1">L7 set</div>')
        rung = s["problems"][p]["rung"] if p in main else 7
        out.append(f'<div class="m">{plabel_html(p, rung)}'
                   f'<span class="lc {LC[p].lower()}" title="LeetCode level, my estimate">{LC[p][0]}</span></div>')
        for c in ORDER:
            k, n = cell(p, c)
            if k is None:
                out.append('<div class="muted">–</div>'); continue
            cls = "pass" if k == n else "part" if k * 2 > n else "fail"
            out.append(f'<div class="{cls}" title="{esc(DISP(c))} on {esc(plabel(p, rung))}: {k} of {n} passed">{k}/{n}</div>')
    out.append("</div>")
    return "".join(out)


def scroll_chart(body, width):
    return (f'<div class="svgscroll" style="--natural-width:{width}px" tabindex="0" role="region" aria-label="Scrollable chart">{body}</div>'
            '<p class="scroll-hint">Scroll sideways on narrow screens.</p>')


def floor(s):
    """Compact stacked labels and bars fit a phone; darker input was cached."""
    E = every(s)
    bars = [("haiku-low", "haiku-low"), ("sonnet-medium", "sonnet-medium"),
            ("luna-low", "luna-low, stock prompt"), ("sol61-medium", "sol61-medium"), ("luna-low-bare", "luna-low, trimmed prompt")]
    bars.sort(key=lambda row: configs.low_context(row[0]))
    W, BL, BR, H = 760, 200, 600, 40 + 40 * len(bars); top = max(E[c]["tokens_mean"]["in_tok"] for c, _ in bars)
    g = [f'<svg viewBox="0 0 {W} {H}" width="100%" {NS} role="img" aria-label="Mean input tokens per call by config">']
    offset = 0
    for i, (c, name) in enumerate(bars):
        if configs.low_context(c) and not offset:
            g.append(f'<text x="12" y="{20 + i * 40}" class="lbl">Low context</text>'); offset = 24
        t = E[c]["tokens_mean"]; y = 8 + i * 40 + offset; w = t["in_tok"] / top * (BR - BL); cw = t["cached_tok"] / top * (BR - BL)
        g.append(f'<text x="{BL - 10}" y="{y + 19}" text-anchor="end" class="lbl">{esc(name)}</text>')
        g.append(f'<rect x="{BL}" y="{y}" width="{w:.1f}" height="28" rx="3" fill="{FAM(c)}" fill-opacity=".35"/>')
        g.append(f'<rect x="{BL}" y="{y}" width="{cw:.1f}" height="28" rx="3" fill="{FAM(c)}" fill-opacity=".9"/>')
        g.append(f'<text x="{BL + w + 8:.1f}" y="{y + 19}" class="lbl">{t["in_tok"]:,.0f}</text>')
    g.append("</svg>")
    return scroll_chart("".join(g), W)


def pipes(arms=None):
    """Rescue set: the single models, then every pipeline (plan first, check then fix, fix everything)."""
    a = arms if arms is not None else rescue_arms()
    low = lambda c: configs.low_context(c, "rescue")
    bars = sorted([(c, SHORT(n), "var(--frontier)" if "→" in n else FAM(c)) for c, n in HARD_PTS], key=lambda row: low(row[0]))
    W, BL, BR, H = 760, 200, 580, 40 + 40 * len(bars)
    g = [f'<svg viewBox="0 0 {W} {H}" width="100%" {NS} role="img" aria-label="Passes on the {configs.set_label("rescue set")}: single models and Haiku pipelines">']
    offset = 0
    for i, (c, name, col) in enumerate(bars):
        if low(c) and not offset:
            g.append(f'<text x="12" y="{20 + i * 40}" class="lbl">Low context</text>'); offset = 24
        v = a[c]; y = 8 + i * 40 + offset; w = v["pass_rate"] * (BR - BL)
        g.append(f'<g><title>{esc(NAME[c])}{" (" + v["derived_note"] + ")" if "derived_note" in v else ""}</title>')
        g.append(f'<text x="{BL - 10}" y="{y + 19}" text-anchor="end" class="lbl">{esc(name)}</text>')
        g.append(f'<rect x="{BL}" y="{y}" width="{BR - BL}" height="28" rx="3" fill="var(--line)"/>')
        g.append(f'<rect x="{BL}" y="{y}" width="{w:.1f}" height="28" rx="3" fill="{col}"/>')
        g.append(f'<text x="{BR + 8}" y="{y + 19}" class="lbl">{v["passes"]}/{v["n"]} · {dataset.usd(v["usd_per_pass"])} · {v["median_s"]:.0f}s</text>')
        g.append("</g>")
    g.append("</svg>")
    return scroll_chart("".join(g), W)


def fast(s):
    """Default → fast twins on the main ladder and L7, never the pilot."""
    rows = [(label, c, group[c]) for label, group in ((configs.set_label("main ladder"), every(s)), (configs.set_label("L7 set"), s["hard"]))
            for pair in FAST_PAIRS for c in pair]
    mx = max(v["latency_s"]["median"] for _, _, v in rows)
    W, BL, BR, H = 760, 200, 600, 16 + 40 * len(rows)
    g = [f'<svg viewBox="0 0 {W} {H}" width="100%" {NS} role="img" aria-label="Default to fast mode pairs on the main ladder and L7 set">']
    for i, (label, c, v) in enumerate(rows):
        y = 8 + i * 40; w = v["latency_s"]["median"] / mx * (BR - BL)
        short_set = "L7" if label == configs.set_label("L7 set") else "ladder"
        g.append(f'<text x="{BL - 10}" y="{y + 19}" text-anchor="end" class="lbl">{short_set} · {esc(DISP(c))}</text>')
        g.append(f'<rect x="{BL}" y="{y}" width="{BR - BL}" height="28" rx="3" fill="var(--line)"/>')
        g.append(f'<rect x="{BL}" y="{y}" width="{w:.1f}" height="28" rx="3" fill="var(--frontier)"/>')
        g.append(f'<text x="{BR + 8}" y="{y + 19}" class="lbl">{v["latency_s"]["median"]:.1f}s · {dataset.usd(v["usd_per_pass"])}</text>')
    g.append("</svg>")
    return scroll_chart("".join(g), W)


def explorer(s):
    """Render interactive geometry around cached measurements and dollar labels."""
    data = [{"c": c, "d": DISP(c), "exp": e, "col": FAM(c), "fast": "-fast" in c,
             "mark": config_marker(c, 0, 0), "kind": v["cost_kind"], "pass": v["pass_at_1"], "usd": v["usd_per_pass"], "usd_text": v["usd_text"],
             "med": v["latency_s"]["median"], "inp": v["tokens_mean"]["in_tok"], "rsn": v["tokens_mean"]["reasoning_tok"]}
            for e, group in ((False, s["configs"]), (True, s["exploratory"])) for c, v in group.items()]
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "page", "explorer.html")
    body = open(src).read().replace("__DATA__", json.dumps(data, separators=(",", ":"))).replace("__USD_TICKS__", json.dumps(s["design"]["usd_ticks"], separators=(",", ":")))
    body = body.replace("Hollow = exploratory config. Codex $ is a proxy.",
                        "Solid = normal speed; hollow = fast mode; dashed edge = bare prompt; lighter blue = 5.6 generation. Shapes match the charts above. Labels connect to their own points. Codex $ is a proxy.")
    # Match the static speed chart: differences below both 0.5 s and 5% are ties.
    body = body.replace('return M[k].up?a>=b:a<=b', 'return k=="med"?a<=b+Math.min(.5,.05*b):M[k].up?a>=b:a<=b')
    body = body.replace('return M[k].up?a>b:a<b', 'return k=="med"?a<=b-Math.min(.5,.05*b):M[k].up?a>b:a<b')
    body = body.replace('sx.t.forEach(function(v){', 'var tickEnd=-Infinity; sx.t.forEach(function(v){')
    body = body.replace('if(x<L-1||x>W-R+1)return;',
                        'if(x<L-1||x>W-R+1)return;var tw=tf(st.x,v).length*(small?6:7);if(x-tw/2<tickEnd+10)return;tickEnd=x+tw/2;')
    start, end = body.index(' var placed=[];'), body.index(" box.innerHTML='<svg")
    body = body[:start] + r"""
 var placed=[],dots=pts.map(function(p){return [sx.f(p[st.x]),sy.f(p[st.y])]}),fontSize=small?11:12;
 var measure=document.createElement('canvas').getContext('2d');measure.font=fontSize+'px -apple-system,Segoe UI,Helvetica,Arial,sans-serif';
 pts.forEach(function(p){var x=sx.f(p[st.x]),y=sy.f(p[st.y]),onf=fr.indexOf(p)>=0;
  g.push('<g class="explorer-point" data-i="'+D.indexOf(p)+'" data-x="'+x+'" data-y="'+y+'" transform="translate('+x+' '+y+')" style="cursor:pointer">'+
   '<title>'+esc(p.d)+'</title>'+(onf?'<circle r="12" fill="none" stroke="var(--frontier)" stroke-width="3"/>':'')+p.mark+'<circle r="14" fill="transparent"/></g>')});
 function overlap(a,b){return Math.max(0,Math.min(a[2],b[2])-Math.max(a[0],b[0]))*Math.max(0,Math.min(a[3],b[3])-Math.max(a[1],b[1]))}
 pts.filter(function(p){return !small||fr.indexOf(p)>=0}).sort(function(a,b){return (fr.indexOf(b)>=0)-(fr.indexOf(a)>=0)||sy.f(a[st.y])-sy.f(b[st.y])}).forEach(function(p){
  var x=sx.f(p[st.x]),y=sy.f(p[st.y]),w=measure.measureText(p.d).width+6,h=fontSize+5,candidates=[];
  [20,45,75,110,150].forEach(function(r){for(var angle=0;angle<360;angle+=30){var a=angle*Math.PI/180,dx=Math.cos(a)*r,dy=Math.sin(a)*r;
    candidates.push([x+dx-(dx<0?w:0),y+dy])}});
  for(var yy=T+h;yy<H-B;yy+=h+3)for(var xx=L;xx+w<W-R;xx+=24)candidates.push([xx,yy]);
  var best=null;
  candidates.forEach(function(c){var lx=c[0],ly=c[1],r=[lx,ly-h,lx+w,ly+3];
   var outside=Math.max(0,L-r[0])+Math.max(0,r[2]-(W-R))+Math.max(0,T-r[1])+Math.max(0,r[3]-(H-B));
   var collision=placed.reduce(function(s,q){return s+overlap(r,q)},0)+dots.reduce(function(s,q){return s+overlap(r,[q[0]-15,q[1]-15,q[0]+15,q[1]+15])},0);
   var score=outside*10000+collision*1000+Math.hypot(lx+w/2-x,ly-h/2-y);
   if(!best||score<best.score)best={score:score,r:r,lx:lx,ly:ly};
  });
  var r=best.r,qx=Math.max(r[0],Math.min(x,r[2])),qy=Math.max(r[1],Math.min(y,r[3])),dist=Math.hypot(qx-x,qy-y)||1;
  placed.push(r);g.push('<line class="explorer-leader" x1="'+(x+(qx-x)*14/dist)+'" y1="'+(y+(qy-y)*14/dist)+'" x2="'+qx+'" y2="'+qy+'" stroke="var(--muted)" stroke-width="1"/>');
  g.push('<text class="explorer-label" x="'+(best.lx+3)+'" y="'+best.ly+'" style="fill:var(--fg)" pointer-events="none">'+esc(p.d)+'</text>');
 });
""" + body[end:]
    body = body.replace('box.querySelectorAll("circle")', 'box.querySelectorAll(".explorer-point")')
    body = body.replace('c.getAttribute("cx")', 'c.getAttribute("data-x")').replace('c.getAttribute("cy")', 'c.getAttribute("data-y")')
    return body


def verdict(c, v, need, E, arms=None):
    """One word per config; each is checked against the data so the table cannot drift from it."""
    if c == "haiku-medium":
        need(v["passes"] == v["n"] - 1 and (arms if arms is not None else rescue_arms())[c]["passes"] == (arms if arms is not None else rescue_arms())[c]["n"], "haiku-medium: one miss, none on the rescue set")
        return f"missed {v['n'] - v['passes']}"
    if c == "haiku-high":
        need(v["passes"] == v["n"] and v["usd_per_pass"] == min(E[d]["usd_per_pass"] for d in ORDER if E[d]["passes"] == E[d]["n"]), "haiku-high is the cheapest with 0 misses")
        return "★ pick"
    if c == "sol61-high":
        need(v["passes"] == v["n"] == 60, "Winner sol61-high passed every main-ladder answer")
        return "★ pick"
    if c == "haiku-low":
        need(v["usd_per_pass"] == min(E[d]["usd_per_pass"] for d in ORDER if E[d]["pass_at_1"] >= 0.95), "haiku-low is the cheapest at 95%+")
        return "budget pick"
    if c == "luna-high":
        need(v["usd_per_pass"] > E["luna-low"]["usd_per_pass"] and v["passes"] > E["luna-low"]["passes"], "luna-high trades cost for more passes")
        return "trade-off"
    if v["passes"] == v["n"]: return "0 misses"
    if v["pass_at_1"] < MIN_PASS: return "avoid"
    dominated = any(d != c and E[d]["usd_per_pass"] <= v["usd_per_pass"] and E[d]["pass_at_1"] >= v["pass_at_1"] for d in ORDER)
    return "beaten" if dominated else "trade-off"


# Hard-set rows for the results table: single models, then pipelines (arrow = a second model or call after the first).
HARD = list(NAME.items())


def row(name, col, k, n, usd, cusd, sec, verdict, proxy=False, derived="", *, rate, claude_only=False):
    r = rate; cls = "good" if r >= 0.95 else "warn" if r >= MIN_PASS else "bad"
    attr = f' title="{esc(derived)}"' if derived else ""
    return (f'<tr{attr}><td><span class="dot" style="background:{col}"></span>{esc(name)}</td><td><span class="pill {cls}">{100 * r:.0f}% ({k}/{n})</span></td>'
            f'<td>{"~" if proxy else ""}{dataset.usd(usd)}</td><td>{"all" if claude_only else dataset.usd(cusd)}</td><td>{sec:.1f}</td><td class="verdict-cell" style="white-space:nowrap">{verdict}</td></tr>')


CODEX = lambda c: any(x in c for x in ("luna", "sol", "astra"))


def short_table(s, need):
    """One table, two groups that sort separately: every config on all problems, then single models and pipelines on the hard
    set. Passed reads "95% (57/60)" so it sorts by rate. Hard-set verdicts come from the numbers: never failed, the cheapest of
    those, or how many attempts missed."""
    E = every(s); a = rescue_arms(s)
    top = [(c, row(DISP(c), FAM(c), E[c]["passes"], E[c]["n"], E[c]["usd_per_pass"], None,
               E[c]["latency_s"]["median"], verdict(c, E[c], need, E, a),
               E[c]["cost_kind"] == "proxy", rate=E[c]["pass_at_1"], claude_only=not CODEX(c))) for c in ORDER]
    clean = [c for c, _ in HARD if a[c]["passes"] == a[c]["n"]]; need(clean, "some rescue-set row never failed")
    best = min(clean, key=lambda c: a[c]["usd_per_pass"])
    need(best == "haiku-medium", "haiku-medium is the cheapest rescue-set row with no miss")
    hv = lambda c: "0 misses ★" if c == best else "★ pick" if c == "sol61-high" else "0 misses" if c in clean else f"missed {a[c]['misses']}"
    duplicates = {c + "+haiku-on-fail" for pair in FAST_PAIRS for c in pair}
    hard = [(c, row(SHORT(name), "var(--frontier)" if "→" in name else FAM(c), a[c]["passes"], a[c]["n"], a[c]["usd_per_pass"], None if CODEX(c) and "+" not in c else a[c]["claude_usd_per_pass"],
                a[c]["median_s"], hv(c), CODEX(c), a[c].get("derived_note", ""), rate=a[c]["pass_rate"], claude_only=not CODEX(c))) for c, name in HARD if c not in duplicates]
    problems = sorted(s["problems"]); rungs = [v["rung"] for v in s["problems"].values()]
    def group(label, rows, source):
        regular = "".join(body for c, body in rows if not configs.low_context(c, source))
        low = "".join(body for c, body in rows if configs.low_context(c, source))
        return (f'<tbody><tr class="grp"><th colspan="6">{esc(label)}</th></tr>{regular}</tbody>'
                + (f'<tbody class="low-context"><tr class="grp"><th colspan="6">Low context: trimmed prompt</th></tr>{low}</tbody>' if low else ""))
    repeats = E[ORDER[0]]["n"] // len(problems)
    ladder_label = f'{configs.set_label("main ladder", capital=True)}: {len(problems)} problems × {repeats} tries = {E[ORDER[0]]["n"]} calls'
    subset_label = f'{configs.set_label("rescue set", capital=True)}: {len(s["design"]["rescue_problems"])} problems × {repeats} tries = {a[HARD[0][0]]["n"]} attempts'
    return ('<div class="tablewrap"><table class="sortable"><thead><tr><th>config</th><th>passed</th><th>$ per pass</th>'
            '<th>Claude $</th><th>median s</th><th>verdict</th></tr></thead>'
            + group(ladder_label, top, "main") + group(subset_label, hard, "rescue") + '</table></div>'
            '<ul class="tight small">'
            f'<li>Ladder problems: {problems[0][:3]}–{problems[-1][:3]}.</li><li>Rungs: L{min(rungs)}–L{max(rungs)}.</li>'
            f'<li>{configs.set_label("rescue set", capital=True)}: problems luna failed most, selected after the main run.</li>'
            '<li>Subset problems:<ul>' + "".join(f'<li>{esc(plabel(q))}.</li>' for q in s["design"]["rescue_problems"]) + '</ul></li>'
            '<li>Low-context rows use trimmed prompts. Other variants: Notes → Everything we tried.</li></ul>')


def full_table(ds):
    """Retain every interval, tail latency and total in a compact grouped table."""
    spec = ds["tables"]["result_detail"]
    label = configs.set_label("main ladder", capital=True)
    low_names = {configs.display(c) + " †" for source, c in configs.REGISTRY if source == "main" and configs.low_context(c)}
    def rows(low):
        return "".join('<tr>' + "".join(f'<td>{esc(cell)}</td>' for cell in r) + '</tr>'
                       for r in spec["rows"] if (r[0] in low_names) == low)
    return ('<div class="tablewrap"><table class="sortable"><thead><tr>'
            + "".join(f'<th>{esc(h)}</th>' for h in spec["head"]) + '</tr></thead>'
            f'<tbody><tr class="grp"><th colspan="4">{esc(label)}</th></tr>{rows(False)}</tbody>'
            f'<tbody class="low-context"><tr class="grp"><th colspan="4">Low context: trimmed prompt</th></tr>{rows(True)}</tbody>'
            '</table></div>')




REPO = "https://github.com/chimera-defi/model-routing-bench/blob/main/bench/problems/"


# Closest LeetCode difficulty for each new problem: my estimate from the nearest LeetCode analogue, not a measurement.
from analysis.configs import LC
# Closest LeetCode analogue per problem, chosen by hand by core technique and shape. It is NOT the source (the problems
# were written for this bench) and is not a measurement. None = nothing on LeetCode is genuinely close.
ANALOGUE = {"p01_overlap_minutes": ("My Calendar III", "my-calendar-iii"),
            "p02_squash": ("String Compression", "string-compression"),
            "p03_ledger": ("Simple Bank System", "simple-bank-system"),
            "p04_taller_within": ("Count of Smaller Numbers After Self", "count-of-smaller-numbers-after-self"),
            "p05_pass_route": ("Cheapest Flights Within K Stops", "cheapest-flights-within-k-stops"),
            "p06_calc": ("Basic Calculator", "basic-calculator"),
            "p07_weighted_distance_sums": ("Sum of Distances in Tree", "sum-of-distances-in-tree"),
            "p08_recur": None,
            "p09_k_machine_schedule": ("Maximum Profit in Job Scheduling", "maximum-profit-in-job-scheduling"),
            "p10_avoid_count": ("Find All Good Strings", "find-all-good-strings"),
            "p11_best_average": ("Maximum Average Subarray II", "maximum-average-subarray-ii"),
            "p12_sheet": ("Design Excel Sum Formula", "design-excel-sum-formula"),
            "p13_xor_ring": None,
            "p14_bounce_board": ("Snakes and Ladders", "snakes-and-ladders"),
            "p15_paint_erase": ("Range Module", "range-module")}
# The pilot's well-known LeetCode problems, in the order the pilot ran them (round 1, then the harder round 2).
PILOT = [("Fizz Buzz", "fizz-buzz", "Easy"), ("Course Schedule II", "course-schedule-ii", "Medium"), ("Candy", "candy", "Hard"),
         ("Reconstruct Itinerary", "reconstruct-itinerary", "Hard"), ("Minimum Window Substring", "minimum-window-substring", "Hard"),
         ("Wildcard Matching", "wildcard-matching", "Hard")]


def set_definitions(s):
    main = sorted(s["problems"], key=lambda p: (s["problems"][p]["rung"], p))
    hard = sorted({p for v in s["hard"].values() for p in v["by_problem"]})
    per = s["design"]["per_rung"]
    l7 = ", ".join(DISP(c) for c in ORDER if c in s["hard"])
    return main, hard, per, l7


def l7_reason(s):
    main, hard, per, _ = set_definitions(s)
    return (f"L7 has {len(hard)} problems, not {per}, because it was added after every strong config passed L6 "
            "to look for a breaking point; it is scored separately from the main ladder.")


def method(s):
    from bench.run import CLAUDE_FLAGS, codex_flags
    lvl = lambda d: f'<span class="lc {d.lower()}" title="{d}">{d[0]}</span>'
    like = lambda p: (f'<br><span class="like">like <a href="https://leetcode.com/problems/{ANALOGUE[p][1]}/" title="closest LeetCode analogue, not the source">{esc(ANALOGUE[p][0])}</a></span>'
                      if ANALOGUE.get(p) else '<br><span class="like">no close LeetCode analogue</span>')
    # Problem name includes its rung; the difficulty badge trails the name.
    item = lambda p, r: (f'<li class="prow"><span class="pn"><a href="{REPO}{p}.py"><code>{esc(plabel(p, r))}</code></a> {lvl(LC[p])}{like(p)}</span>'
                         f'<span class="pd">{esc(TESTS[p])}</span></li>')
    main, hard, per, _ = set_definitions(s)
    li = [f'<li class="round"><b>Pilot</b>: well-known LeetCode problems. Every config passed, so it ranked nothing and is not scored.<ul>'
          + "".join(f'<li>{lvl(d)} <a href="https://leetcode.com/problems/{slug}/">{esc(n)}</a> <span class="like">source</span></li>' for n, slug, d in PILOT) + "</ul></li>",
          f'<li class="round"><b>Main ladder</b>: {len(main)} new problems, p01–p12, rungs L1–L6 ({per} per rung, rising difficulty). Every config ran it.<ul>'
          + "".join(item(p, s["problems"][p]["rung"]) for p in main) + "</ul></li>",
          f'<li class="round"><b>L7 set</b>: {len(hard)} extra-hard problems, p13–p15, rung L7. {l7_reason(s)}<ul>'
          + "".join(item(p, 7) for p in hard) + "</ul></li>"]
    flag = lambda fl: esc(" ".join(f if f else '""' for f in fl))
    group = {}
    for c, v in every(s).items():
        group.setdefault((v["cli"], v["model"]), []).append((c, v["effort"]))
    cmds = []
    for (cli, model), configs in group.items():
        efforts = "|".join(e for e in ("low", "medium", "high", "xhigh") if any(v == e for _, v in configs))
        names = ", ".join(DISP(c) for c, _ in configs)
        if cli == "claude":
            command = f"claude -p --model {model} --effort {efforts} {flag(CLAUDE_FLAGS)}"
        else:
            flags = [codex_flags(c) for c, _ in configs]
            base = list(flags[0])
            tiers = list(dict.fromkeys(f.split("=", 1)[1] for fl in flags for f in fl if f.startswith("service_tier=")))
            tiers.sort(key=lambda v: v != "default")
            base = ["service_tier=" + "|".join(tiers) if f.startswith("service_tier=") else f for f in base]
            command = f"codex exec -m {model} -c model_reasoning_effort={efforts} {flag(base)}"
        cmds.append(f'<li>{esc(names)} → <code>{command}</code></li>')
    cmds.append('<li><code>python3 -m bench.gated_repair</code>: builder answer → run the statement’s examples → haiku-low repairs only on failure</li>')
    return "".join(li), "".join(cmds)


def sets_box(s):
    """Collapsed reading guide below the cost/accuracy charts and their notes."""
    main, hard, per, l7 = set_definitions(s)
    rungs = sorted({s["problems"][p]["rung"] for p in main})
    lab = lambda ps: ", ".join(f'<span class="pl" title="{esc(TESTS[p])}">{esc(plabel(p))}</span>' for p in ps)
    return ('<details class="sets"><summary>How to read the problems, rungs and sets</summary><ul class="tight small">'
            '<li>Compare each set separately.</li>'
            f'<li>Problem labels show number, short name and rung: {lab([main[-1]])}. Hover for a one-line description.</li>'
            f'<li><b>Main ladder</b>: {len(main)} problems, {main[0].split("_")[0]}–{main[-1].split("_")[0]}, rungs L{rungs[0]}–L{rungs[-1]} ({per} per rung, easiest first). Every config ran it.</li>'
            f'<li><b>L7 set</b>: {len(hard)} extra-hard problems ({lab(hard)}), scored separately. Added after every strong config passed L{rungs[-1]} to seek a breaking point, with more than the usual {per} problems per rung.</li>'
            f'<li>Later-run configs: {l7}.</li>'
            f'<li><b>{configs.set_label("rescue set", capital=True)}</b>: {lab(s["design"]["rescue_problems"])}.</li>'
            '<li>Easy/Medium/Hard badges estimate LeetCode difficulty; rungs use this bench\'s own order and may differ.</li>'
            '<li>Config names: haiku/sonnet = Claude; luna/sol/astra = Codex; suffix = effort; -bare = stripped Codex CLI system prompt.</li>'
            '</ul></details>')


def rescue_subtitle(s=None):
    s = s or dataset.view(dataset.read())
    attempts = rescue_arms(s)["sol61-high"]["n"]
    return (f'{configs.set_label("rescue set", capital=True)}: the {len(s["design"]["rescue_problems"])} problems luna failed most. '
            f'Each row has {attempts} attempts. No intervals are shown. '
            'Purple marks pipelines. '
            'sol61-high and astra-medium never failed an example. '
            'No Haiku repair ran. '
            'Normal speed uses separate runs. ⚡ rows replay cached answers.')


def speed_frontier_text(s, names):
    E = every(s)
    return ", ".join(f"{DISP(c)} ({E[c]['latency_s']['median']:.1f} s, {dataset.usd(E[c]['usd_per_pass'])} per pass"
                     + (f", {100 * E[c]['pass_at_1']:.1f}% passed" if E[c]['passes'] < E[c]['n'] else "") + ")" for c in names)


def notation_meanings(ds):
    """Resolve the registry's prose using the cached dataset facts."""
    return {symbol: meaning.format_map(ds["facts"]) for symbol, meaning in configs.NOTATION.items()}


def legend(ds):
    items = "".join(f'<dt>{esc(symbol)}</dt><dd>{esc(meaning)}</dd>'
                    for symbol, meaning in notation_meanings(ds).items())
    return f'<details class="legend" id="notation"><summary>Notation</summary><dl>{items}</dl></details>'


def notation_tooltips(body, ds):
    """Explain the first use per section without editing attributes, scripts or source text."""
    meanings = notation_meanings(ds)
    aliases = {
        "low/medium/high": r"(?-i:\blow\s*/\s*medium\s*/\s*high\b|\b(?:low|medium|high|xhigh)\b)",
        "-bare": r"-bare\b|\bbare\b",
        "$0": r"\$0(?![\d.])",
        "≥N%": r"≥(?:N|\d+(?:\.\d+)?)%",
        "L1–L7": r"\bL\d+(?:\s*(?:to|[–-])\s*L\d+)?\b",
        "noshell B1/B2": r"\bnoshell[- ]B[12]\b|\bB[12]\b",
        "–": r"(?<!\w)–(?!\w)",
    }
    patterns = []
    symbols = sorted(meanings, key=len, reverse=True)
    for i, symbol in enumerate(symbols):
        pattern = aliases.get(symbol, re.escape(symbol))
        if symbol in ("H", "retry", "p90", "pass@1"):
            pattern = r"(?<!\w)" + pattern + r"(?!\w)"
        patterns.append(f"(?P<n{i}>{pattern})")
    match_symbol = re.compile("|".join(patterns), re.I)

    class Annotator(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.out = []
            self.stack = []
            self.seen = set()

        def handle_starttag(self, tag, attrs):
            if tag == "section":
                self.seen = set()
            raw = self.get_starttag_text()
            values = dict(attrs)
            if "dot" in values.get("class", "").split():
                symbol = "purple dot" if "--frontier" in values.get("style", "") else "family dots"
                if symbol not in self.seen:
                    self.seen.add(symbol)
                    raw = raw[:-1] + f' data-notation="{symbol}" title="{esc(meanings[symbol])}">'
            if tag not in ("area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"):
                self.stack.append((tag, dict(attrs)))
            self.out.append(raw)

        def handle_startendtag(self, tag, attrs):
            self.out.append(self.get_starttag_text())

        def handle_endtag(self, tag):
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    break
            self.out.append(f"</{tag}>")

        def handle_data(self, data):
            if any(tag in ("script", "style", "title", "option", "textarea") or attrs.get("id") == "notation"
                   for tag, attrs in self.stack):
                self.out.append(data)
                return
            wrapper = "tspan" if any(tag == "svg" for tag, _ in self.stack) else "abbr"

            def explain(match):
                symbol = symbols[int(match.lastgroup[1:])]
                if symbol in self.seen:
                    return match[0]
                self.seen.add(symbol)
                return (f'<{wrapper} class="notation-use" data-notation="{esc(symbol)}" '
                        f'title="{esc(meanings[symbol])}">{match[0]}</{wrapper}>')

            self.out.append(match_symbol.sub(explain, data))

        def handle_entityref(self, name):
            self.out.append(f"&{name};")

        def handle_charref(self, name):
            self.out.append(f"&#{name};")

        def handle_comment(self, data):
            self.out.append(f"<!--{data}-->")

    parser = Annotator()
    parser.feed(body)
    parser.close()
    return "".join(parser.out)


def winner_table(ds, need):
    """Six routing choices; pipeline metrics retain their separately measured scope."""
    ladder = lambda c: dataset.get(ds, c, "main ladder")
    default, budget, speed, fast, safety = map(ladder, (
        "sol61-high", "haiku-low", "sonnet-medium", "sol61-high-fast", "haiku-high"))
    pipeline = dataset.get(ds, "sol61-high+haiku-on-fail", "rescue arms", "rescue")
    threshold = float(ds["facts"]["budget_pass"].rstrip("%")) / 100
    eligible = [r for r in ds["rows"] if r["set"] == "main ladder" and r["pass_rate"] >= threshold]
    need(budget["usd_per_pass"] == min(r["usd_per_pass"] for r in eligible),
         "Winner budget pick is cheapest at the stated pass threshold")
    for pick in (default, speed, safety):
        for set_, source in (("main ladder", "main"), ("L7 set", "main"), ("repo tasks", "agentic")):
            r = dataset.get(ds, pick["config"], set_, source)
            need(r["passes"] == r["n"], f"Winner {pick['config']} never missed on {set_}")
    need(speed["median_s"] < safety["median_s"], "Winner speed pick is faster than the safety pick")
    need(fast["passes"] == fast["n"] and fast["median_s"] < default["median_s"],
         "Winner fast mode preserves passes and reduces time")
    need(fast["tokens_in_mean"] == default["tokens_in_mean"]
         and fast["tokens_out_mean"] <= default["tokens_out_mean"],
         "Winner fast-mode premium does not come from more tokens")
    need(pipeline["passes"] == pipeline["n"] and pipeline["spend_claude"] == 0,
         "Winner measured example-check pipeline passed without calling Haiku")
    choices = [
        ("Default", default, "Use Codex quota first"),
        ("Budget", budget, f"Cheapest passing ≥{ds['facts']['budget_pass']}"),
        ("Speed", speed, "Faster than haiku-high; no misses"),
        ("Fast mode", fast, f"Faster Codex; {ds['facts']['fm_mult']} list price"),
        ("Codex → Haiku", pipeline, "Fix failed examples; no fixes needed"),
        ("Safety / fallback", safety, "Cheapest with no misses across sets"),
    ]
    head = ("Use case", "Pick", "Why", "Pass", "$ per pass", "Time")
    widths = (16, 22, 26, 10, 15, 11)
    th = "".join(f'<th scope="col" style="width:{width}%;text-align:left">{esc(name)}</th>'
                 for name, width in zip(head, widths))
    rows = []
    for use, r, why in choices:
        pick = r["display"] if r is not pipeline else f"{default['display']} →H fail"
        price = ("~" if r["cost_kind"] == "proxy" else "") + dataset.usd(r["usd_per_pass"])
        cells = (use, pick, why, f"{r['passes']}/{r['n']}", price, f"{r['median_s']:.1f} s")
        rows.append('<tr>' + "".join(
            f'<td style="white-space:normal;text-align:left;padding:7px 8px;vertical-align:top">{esc(cell)}</td>'
            for cell in cells) + '</tr>')
    caption = (f'{configs.set_label("main ladder", capital=True)} except pipeline '
               f'({configs.set_label("rescue set")}). Time = median seconds. '
               '~ = estimated from tokens; Claude costs are measured.')
    return ('<div class="tablewrap"><table class="winner-table" style="table-layout:fixed;min-width:720px;font-size:13px">'
            f'<caption style="caption-side:bottom;text-align:left;padding:8px">{esc(caption)}</caption>'
            f'<thead><tr>{th}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def widgets(s, need, ds=None):
    arms = rescue_arms(ds or s)
    a, fa = pass_cost(s); b, fb = speed_cost(s); ha, hfa = hard_pass_cost(arms); hb, hfb = hard_speed_cost(arms); nm = dict(HARD_PTS)
    return {"pass_cost": a, "speed_cost": b, "hard_pass_cost": ha, "hard_speed_cost": hb,
            "hard_front_pass": ", ".join(SHORT(nm[c]) for c in hfa), "hard_front_speed": ", ".join(SHORT(nm[c]) for c in hfb), "sets": sets_box(s), "grid": grid(s), "floor": floor(s), "pipes": pipes(arms), "fast": fast(s), "explorer": explorer(s), "short_table": short_table(s, need), "full_table": full_table(ds or dataset.read()),
            "front_pass": ", ".join(map(DISP, fa)), "front_speed": speed_frontier_text(s, fb),
            "winner": winner_table(ds or dataset.read(), need),
            "legend": legend(ds or dataset.read()), "rescue_subtitle": rescue_subtitle(s), "problems": method(s)[0], "flags": method(s)[1]}
