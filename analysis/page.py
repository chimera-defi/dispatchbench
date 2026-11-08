"""Widgets for the page (results/report/page.html), all drawn from results/dataset.json: the two Pareto scatters, the
problem × config grid, the token-floor bars and the short result table. Inline SVG and HTML that take their colours
from the page's CSS variables, so both themes work. Standard library only."""
import html, math, os, re
import unicodedata

from analysis import charts, configs, dataset
from html.parser import HTMLParser
from analysis.charts import FAMILY, MIN_PASS
from analysis.labels import TESTS, DISP, plabel, plabel_html

# Plot order and family colour (a CSS variable of the page). luna-high is the exploratory full-ladder run.
ORDER = ["haiku-low", "haiku-medium", "haiku-high", "sonnet-medium", "sol61-medium", "luna-high", "luna-medium", "luna-low", "luna-low-bare",
         "astra-medium", "astra-medium-fast", "sol61-high", "sol61-high-fast", "sol56-high", "luna56-high", "luna56-low", "terra61-high", "terra61-high-fast", "terra61-low", "terra61-low-fast"]
# API calibration rows have their own hetzner(s) projection and join non-price widgets explicitly.
GROK_ORDER = configs.GROK_CONFIGS
from analysis.dataset import WINNER_PICKS, front, speed_dominates
FAM = FAMILY
NS = 'xmlns="http://www.w3.org/2000/svg"'


def styles():
    """Bundle CSS in cascade order for the single-file deployment."""
    page_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "page")
    return "\n".join(open(os.path.join(page_dir, name)).read().strip()
                     for name in ("tokens.css", "topbar.css", "style.css"))


def every(s):
    """Every config the $ charts and tables may plot. Free experimental tiers have no published dollar comparison and are left out."""
    return {**s["configs"], **{c: v for c, v in s["exploratory"].items() if c not in configs.FREE_TIER_CONFIGS}}


def devin(s):
    """{config: block} for the Devin free-tier lane: 1 repeat on p01-p12, no token or $ data. Never on a $ chart."""
    return {c: v for c, v in s["exploratory"].items() if c in configs.DEVIN_CONFIGS}


def hetzner(s):
    """Measured tokens, free experimental access, one repeat; no dollar comparison."""
    return s.get("hetzner", {})


def esc(t):
    return html.escape(str(t))


def anchor_slug(text):
    """Deterministic ASCII anchors, independent of typography and markup."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "heading"


def heading_link(identifier, text):
    return (f'<a class="hlink" href="#{esc(identifier)}" '
            f'aria-label="Link to this section: {esc(text)}">#</a>')


def explorer_heading(row=None):
    """The detail card is rebuilt in JS; ship its Python-generated title markup."""
    text = row["display"] if row else "No config selected"
    identifier = "config-" + anchor_slug(text)
    return f'<h3 id="{identifier}">{esc(text)}{heading_link(identifier, text)}</h3>'


def deep_links(body):
    """Add title affordances without reserializing prose or existing markup.

    Reserve all existing ids first, including headings later in the document,
    so generated slugs never steal a public anchor. Existing section ids stay put.
    """
    class Inventory(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids = set()
            self.sections, self.titles = [], {}
            self.lines = [0] + [m.end() for m in re.finditer("\n", body)]

        def handle_starttag(self, tag, attrs):
            identifier = dict(attrs).get("id")
            if identifier:
                self.ids.add(identifier)
            if tag == "section":
                self.sections.append([identifier, False])
            elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self.sections:
                section = self.sections[-1]
                if not section[1]:
                    section[1] = True
                    if section[0]:
                        line, column = self.getpos()
                        self.titles[self.lines[line - 1] + column] = section[0]

        def handle_endtag(self, tag):
            if tag == "section" and self.sections:
                self.sections.pop()

    inventory = Inventory()
    inventory.feed(body)

    def unique(base):
        identifier, suffix = base, 2
        while identifier in inventory.ids:
            identifier = f"{base}-{suffix}"
            suffix += 1
        inventory.ids.add(identifier)
        return identifier

    def heading(match):
        if match[1] is None:  # Preserve raw script/style text.
            return match[0]
        tag, attrs, content = match.groups()
        section = inventory.titles.get(match.start())
        if not section and tag not in {"h2", "h3"}:
            return match[0]
        if re.search(r'class=[\"\'][^\"\']*\bhlink\b', content):
            return match[0]
        text = " ".join(html.unescape(re.sub(r"<[^>]*>", " ", content)).split())
        existing = re.search(r'\bid=[\"\']([^\"\']+)[\"\']', attrs)
        identifier = section or (html.unescape(existing[1]) if existing else unique(anchor_slug(text)))
        if not section and not existing:
            attrs += f' id="{esc(identifier)}"'
        return f'<{tag}{attrs}>{content}{heading_link(identifier, text)}</{tag}>'

    body = re.sub(r'<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<(h[1-6])\b([^>]*)>(.*?)</\1>',
                  heading, body, flags=re.S)

    # Reading-guide disclosures have summaries rather than h3s. Give their
    # summaries addressable targets inside the closed details as well.
    def method_targets(match):
        def summary(m):
            attrs, content = m.groups()
            if re.search(r"\bid=", attrs):
                return m[0]
            text = html.unescape(re.sub(r"<[^>]*>", " ", content))
            identifier = unique("method-" + anchor_slug(text))
            return f'<summary{attrs} id="{identifier}">{content}</summary>'
        return re.sub(r"<summary\b([^>]*)>(.*?)</summary>", summary, match[0], flags=re.S)

    return re.sub(r'<section\b[^>]*\bid="method"[^>]*>.*?</section>', method_targets, body, flags=re.S)


# Marker shape by model (colour stays the vendor): read the chart without a label on every point.
def SHAPE(c):
    if c.startswith("grok"): return "hexagon"
    if c.startswith("devin"): return "plus"
    if c.startswith("hetzner"): return "pentagon"
    if c.startswith("terra"): return "pentagon"
    if "luna" in c:
        return "triangle-down" if "high" in c else "triangle-right" if "medium" in c else "triangle"
    return "circle" if c.startswith("haiku") else "square" if c.startswith("sonnet") else "star" if c.startswith("astra") else "diamond"


def marker_paint(c, hollow, col):
    """A surface outline separates Grok's blue mark from neighbouring points."""
    if c.startswith("grok"):
        return ("var(--panel)" if hollow else col, "var(--panel)", 1.5)
    return ("var(--panel)" if hollow else col, col, 2.5)


def config_marker(c, x, y, col=None, k=1.0):
    """Across plots, hollow means fast mode, dashed means a stripped prompt."""
    col = col or FAM(c)
    fill, stroke, width = marker_paint(c, "-fast" in c, col)
    return marker(SHAPE(c), x, y, fill, stroke, "bare" in c, k, width)


def point_category(c):
    if c.startswith("grok"): return "grok"  # registered as exploratory, but it is its own series
    if "+" in c: return "pipelines"
    if c.endswith("-fast"): return "fast"
    # Winner picks sit with the main ladder in chart filters, even ones added after the main run (haiku-high).
    main = configs.REGISTRY.get(("main", c), {}).get("category") == "main ladder" or c in WINNER_PICKS
    return "main" if main else "exploratory"


def marker(kind, x, y, fill, stroke, dash=False, k=1.0, width=2.5):
    a = f' fill="{fill}" stroke="{stroke}" stroke-width="{width}"' + (' stroke-dasharray="3 2"' if dash else "")
    if kind == "circle": return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{6.5 * k:.1f}"{a}/>'
    if kind == "square": return f'<rect x="{x - 6 * k:.1f}" y="{y - 6 * k:.1f}" width="{12 * k:.1f}" height="{12 * k:.1f}"{a}/>'
    if kind == "hexagon": return f'<polygon points="{charts.hexagon(x, y, 10 * k)}"{a}/>'
    if kind == "triangle": v = [(0, -8.5), (7.5, 5.5), (-7.5, 5.5)]
    elif kind == "triangle-down": v = [(0, 8.5), (7.5, -5.5), (-7.5, -5.5)]
    elif kind == "triangle-right": v = [(8.5, 0), (-5.5, 7.5), (-5.5, -7.5)]
    elif kind == "diamond": v = [(0, -8.5), (8.5, 0), (0, 8.5), (-8.5, 0)]
    elif kind == "plus": v = [(-3, -9), (3, -9), (3, -3), (9, -3), (9, 3), (3, 3), (3, 9), (-3, 9), (-3, 3), (-9, 3), (-9, -3), (-3, -3)]
    elif kind == "pentagon": v = [(8 * math.sin(math.radians(72 * i)), -8 * math.cos(math.radians(72 * i))) for i in range(5)]
    else: v = [(r * math.sin(math.radians(36 * i)), -r * math.cos(math.radians(36 * i))) for i, r in enumerate([9.5, 4] * 5)]
    return f'<polygon points="{" ".join(f"{x + dx * k:.1f},{y + dy * k:.1f}" for dx, dy in v)}"{a}/>'


def plot_xy(p, X, Y):
    return p.get("plot_x", X(p["x"])), p.get("plot_y", Y(p["y"]))


def separate_points(pts, X, Y):
    """Jitter coincident marks only; preserve the measured coordinates and tooltips.
    Partial points are nudged afterwards and never join a group, so they cannot move another series."""
    groups = []
    for p in pts:
        if p.get("partial") or "plot_x" in p: continue  # already placed, e.g. packed into the $0 lane
        xy = X(p["x"]), Y(p["y"])
        group = next((g for g in groups if math.dist(xy, g[0]) < 14), None)
        if group is None: groups.append((xy, [p]))
        else: group[1].append(p)
    placed = []
    for (x, y), group in groups:
        if len(group) < 2:
            placed.append((x, y))
            continue
        for i, p in enumerate(group):
            px = x + (i - (len(group) - 1) / 2) * 18
            p.update(plot_x=px, plot_y=y, label=True, jitter=True)
            placed.append((px, y))
    for p in pts:
        if p.get("partial") or "plot_x" not in p: continue
        placed.append((p["plot_x"], p["plot_y"]))
    for p in pts:
        if not p.get("partial") or "plot_x" in p: continue
        y = Y(p["y"])
        x = charts.dodge(X(p["x"]), y, placed)
        if x != X(p["x"]): p.update(plot_x=x, plot_y=y, jitter=True)
        placed.append((x, y))


def scatter(pts, fr, X, Y, xt, yt, xlab, ylab, corner, labels, W=560, H=380, L=84, R=16, T=14, B=322, extra="", stat=None, variant=None, minor=(), badges=False, picks_note="", key_labels=None):
    """pts: dicts with c, x, y, w (whisker (axis, lo, hi) or None), tip, hollow. fr: the frontier path. Only frontier points
    get a text label; every point is in the key beside the chart, and hovering (or tapping) a point or a key row shows its tip."""
    separate_points(pts, X, Y)
    g = [f'<svg viewBox="0 0 {W} {H}" width="100%" {NS} role="img" aria-label="{esc(ylab)} against {esc(xlab)}, best trade-offs ringed and numbered in purple; the key lists every point">']
    g += [f'<line x1="{X(v):.1f}" x2="{X(v):.1f}" y1="{T}" y2="{B}" stroke="var(--line)" stroke-opacity=".45"/>' for v in minor]
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
    # data-front/b/end let sort.js redraw this path from the visible points when a category is filtered out.
    start = re.match(r"M([\d.]+)", fr)
    if badges and start:  # shade what the best trade-offs beat: the corner on the worse side of the staircase
        g.append(f'<path class="zone" data-t="{T}" d="{fr}{f" V{B} Z" if stat == "pass" else f" V{T} H{start[1]} Z"}" fill="var(--frontier)" fill-opacity=".09" stroke="none" pointer-events="none"/>')
    g.append(f'<path d="{fr}" data-front="{stat or ""}" data-b="{B}" data-end="{W - R}" data-t="{T}" fill="none" stroke="var(--frontier)" stroke-width="{2.5 if badges else 4}"{"" if badges else " stroke-dasharray=\"9 6\""} stroke-linejoin="round"/>' + extra)
    for p in sorted(pts, key=lambda p: p["on"]):  # frontier points drawn last, on top
        px, py = plot_xy(p, X, Y)
        col = p.get("col") or FAM(p["c"])
        # data-out keeps sort.js from putting a partial series on the frontier. The grok colour rule undoes the fade.
        outside = (not p.get("ok", True)) or p.get("partial")
        g.append(f'<g class="pt" {point_attrs(p)} data-v="{p["x"]!r} {p["y"]!r}" data-f="{X(p["x"]):.1f} {Y(p["y"]):.1f}"'
                 f'{"" if not outside else " data-out=\"1\""}{" data-best=\"\"" if p["on"] else ""}>')
        if p["w"]:
            ax, lo, hi = p["w"]
            if ax == "x": g.append(f'<line x1="{X(lo):.1f}" x2="{X(hi):.1f}" y1="{py:.1f}" y2="{py:.1f}" stroke="{col}" stroke-width="2.5" stroke-opacity=".4"/>')
            else: g.append(f'<line x1="{px:.1f}" x2="{px:.1f}" y1="{Y(lo):.1f}" y2="{Y(hi):.1f}" stroke="{col}" stroke-width="2" stroke-opacity=".3"/>')
        if p["on"]: g.append(f'<circle class="ring" cx="{px:.1f}" cy="{py:.1f}" r="13" fill="none" stroke="var(--frontier)" stroke-width="{2.5 if badges else 3}"/>')
        fill, stroke, width = marker_paint(p["c"], p["hollow"], col)
        g.append(marker(p.get("shape", SHAPE(p["c"])), px, py, fill, stroke, p.get("dash"), width=width))
        g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="14" fill="transparent"/></g>')  # hover target
    ranked = sorted((p for p in pts if p["on"]), key=lambda p: p["x"]) if badges else []
    if ranked:  # numbered chips on the best trade-offs; the names sit in the list under the plot
        g.append('<g class="ranks" pointer-events="none">' + "".join(
            f'<g class="rk" data-c="{esc(p["c"])}" data-cat="{point_category(p["c"])}"><circle cx="{min(plot_xy(p, X, Y)[0] + 13, W - R - 11):.1f}" cy="{max(plot_xy(p, X, Y)[1] - 13, T + 11):.1f}" r="10.5" fill="var(--frontier)" stroke="var(--panel)" stroke-width="1.5"/>'
            f'<text x="{min(plot_xy(p, X, Y)[0] + 13, W - R - 11):.1f}" y="{max(plot_xy(p, X, Y)[1] - 13, T + 11) + 4.5:.1f}" text-anchor="middle" class="rk-n">{i}</text></g>'
            for i, p in enumerate(ranked, 1)) + '</g>')
    cx, cy = L + 10, T + 18 if corner.startswith("↖") else B - 10
    walls = path_boxes(fr) + [(cx, cy - LH + 3, cx + CW * len(corner), cy + 3)]
    if badges: labelled = [p for p in pts if not p.get("quiet") and not p["on"] and p.get("label") and not p.get("jitter")]  # picks off the frontier keep a name
    else: labelled = [p for p in pts if not p.get("quiet") and (p["on"] or ("+" in p["c"] if p.get("set") == "rescue" else p.get("label")))]
    labelled = [p for p in labelled if not p.get("partial")]
    anchors = [p for p in pts if not p.get("partial")]
    for p, (x, y, a) in place(labelled, X, Y, labels, (L, W - 2, T - 6, B - 2), walls, also=anchors):
        if p["lead"]: g.append((f'<line class="label-leader" data-c="{esc(p["c"])}" data-cat="{point_category(p["c"])}" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="var(--muted)" stroke-width="1"/>') % p["lead"])
        g.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{a}" class="lbl{' on' if p["on"] else ''}" data-cat="{point_category(p["c"])}" data-set="{p.get("set", "main")}">{esc(p.get("name", p["c"]))}</text>')
    g.append("</svg>")
    strip = picks(ranked, picks_note) if badges else ""
    if variant:
        return f'<div class="cvariant v-{variant}"><div class="cplot">{"".join(g)}{strip}</div>{key(pts, stat, key_labels)}</div>'
    return f'<div class="cwrap"><div class="cplot">{"".join(g)}{strip}</div>{key(pts, stat, key_labels)}<div class="ctip" hidden></div></div>'


def picks(ranked, note):
    """The numbered best trade-offs, named once, in plain words. sort.js rebuilds this list when a category is filtered out."""
    items = "".join(f'<li {point_attrs(p)} tabindex="0">{point_icon(p)}<b>{i}</b><span>{esc(p.get("name", p["c"]))}</span></li>' for i, p in enumerate(ranked, 1))
    return f'<div class="picks"><span class="pk-h">Best trade-offs</span><ol>{items}</ol><span class="pk-n">{esc(note)}</span></div>'


def point_attrs(p):
    return (f'data-c="{esc(p["c"])}" data-cat="{point_category(p["c"])}" '
            f'data-set="{p.get("set", "main")}" data-tip="{esc(p["tip"])}"')


def point_icon(p):
    col = p.get("col") or FAM(p["c"])
    fill, stroke, width = marker_paint(p["c"], p["hollow"], col)
    return (f'<svg viewBox="-10 -10 20 20" {NS} aria-hidden="true">'
            + marker(p.get("shape", SHAPE(p["c"])), 0, 0, fill, stroke, p.get("dash"), .8, width) + '</svg>')


def point_values(p, stat):
    metric = f'{p["x"]:.1f} s' if stat == "speed" else f'{100 * p["y"]:.0f}%'
    usd = p["y"] if stat == "speed" else p["x"]
    value = f'{metric} · {dataset.usd(usd)}'
    if p.get("free_mode") and p["normal_usd"] != p["free_usd"]:
        value += f' · saved {dataset.usd(p["saved_usd"])}'
    return value


def key(pts, stat, labels=None):
    """Every point grouped by the filter categories; only main starts expanded."""
    labels = labels or {}
    groups = []
    for cat in ("main", "fast", "pipelines", "exploratory", "grok"):
        rows = []
        for p in sorted((p for p in pts if point_category(p["c"]) == cat),
                        key=lambda p: (p["x"] if stat == "speed" else p["y"] * -1, p["y"] if stat == "speed" else p["x"])):
            nm = p.get("lname") or p.get("name", p["c"])
            rows.append(f'<li tabindex="0" {point_attrs(p)}{" class=on" if p["on"] else ""}>'
                        f'{point_icon(p)}<span class="n">{esc(nm)}</span><span class="v">{point_values(p, stat) if stat else ""}</span></li>')
        if rows:
            title = labels.get(cat, cat)
            style = ' style="text-transform:none;letter-spacing:0"' if cat == "grok" else ""
            groups.append(f'<details class="key-group" data-cat="{cat}"{" open" if cat == "main" else ""}>'
                          f'<summary{style}>{esc(title)} ({len(rows)})</summary><ul class="ckey">{"".join(rows)}</ul></details>')
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
    dots = [(plot_xy(p, X, Y)[0] - (15 if p["on"] else 10), plot_xy(p, X, Y)[1] - (15 if p["on"] else 10),
             plot_xy(p, X, Y)[0] + (15 if p["on"] else 10), plot_xy(p, X, Y)[1] + (15 if p["on"] else 10)) for p in list(also) or pts]
    out = {}
    def rect(px, py, dx, dy, a, n):
        w = char_width * len(n); l = px + dx - (w if a == "end" else w / 2 if a == "middle" else 0)
        return (l, py + dy - label_height + 4, l + w, py + dy + 4)
    centres = [plot_xy(p, X, Y) for p in list(also) or pts]
    def gap(r, x, y): return math.hypot(max(r[0] - x, 0, x - r[2]), max(r[1] - y, 0, y - r[3]))
    def hit(r, q): return max(0, min(r[2], q[2]) - max(r[0], q[0])) * max(0, min(r[3], q[3]) - max(r[1], q[1]))
    nm = {id(p): p.get("name", p["c"]) for p in pts}
    def best(p, other_labels):
        px, py = plot_xy(p, X, Y); n = nm[id(p)]; top = None
        spots = ([p["pin"]] if "pin" in p else []) + ([labels[p["c"]]] if p["c"] in labels else []) + SPOTS + FAR
        # Empty lanes also remain candidates when every radial position is crowded.
        spots += [(x - px, y - py, "start")
                  for y in range(round(y0 + label_height), round(y1), label_height + 5)
                  for x in range(round(x0), max(round(x0) + 1, round(x1 - char_width * len(n))), 30)]
        for s in spots:
            r = rect(px, py, *s, n)
            out_of = (max(0, x0 - r[0]) + max(0, r[2] - x1) + max(0, y0 - r[1]) + max(0, r[3] - y1)) * 10000
            # Labels, marks and the frontier each reserve their own space.
            mine = gap(r, px, py); near = any(gap(r, *c) < mine - 2 for c in centres if c != (px, py))
            cost = (out_of + 1000 * sum(hit(r, q) for q in other_labels)
                    + 300 * sum(hit(r, q) for q in dots) + 500 * sum(hit(r, q) for q in walls)
                    + 30000 * near + mine)
            if top is None or cost < top[0]: top = (cost, s, r)
        return top
    order = sorted(pts, key=lambda p: not p["on"]); got = {}
    for p in order:
        got[id(p)] = best(p, [g[2] for g in got.values()])
    for _ in range(6):  # repair pass: any label that now overlaps something (even one placed clear earlier) is re-seated
        for p in order:
            others = [g[2] for k, g in got.items() if k != id(p)]
            if sum(hit(got[id(p)][2], q) for q in others + dots + list(walls)) > 0:
                got[id(p)] = best(p, others)
    for p in order:
        _, s, r = got[id(p)]; dx, dy, a = s; px, py = plot_xy(p, X, Y)
        # Every offset label gets a leader, including placements near the point.
        qx, qy = min(max(px, r[0]), r[2]), min(max(py, r[1]), r[3]); d = math.hypot(qx - px, qy - py) or 1
        lead = (px + (qx - px) * 8 / d, py + (qy - py) * 8 / d, qx, qy)
        out[id(p)] = (dict(p, name=nm[id(p)], lead=lead), (px + dx, py + dy, a))
    return list(out.values())


def logscale(lo, hi, a, b):
    return lambda v: a + (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (b - a)


def tip(c, v):
    k = " (exploratory)" if point_category(c) == "exploratory" else ""
    return (f"{DISP(c)}{k} [main ladder]: {v['passes']}/{v['n']} passed, {dataset.usd(v['usd_per_pass'])} per pass ({'estimated from tokens' if v['cost_kind'] == 'proxy' else 'measured bill'}), "
            f"median {dataset.median_seconds(v):.1f} s")


FAST_PAIRS = [("sol61-high", "sol61-high-fast"), ("astra-medium", "astra-medium-fast"),
              ("terra61-low", "terra61-low-fast"), ("terra61-high", "terra61-high-fast")]


def fast_pairs(pts, X, Y):
    """A thin line from each default-tier config to its fast-mode twin (same model and effort, priority tier), so the cost of speed reads off the chart."""
    by = {p["c"]: p for p in pts}
    return "".join(f'<line x1="{X(by[a]["x"]):.1f}" y1="{Y(by[a]["y"]):.1f}" x2="{X(by[b]["x"]):.1f}" y2="{Y(by[b]["y"]):.1f}" '
                   f'data-cat="fast" data-from-cat="{point_category(a)}" stroke="var(--codex)" stroke-width="1.5" stroke-opacity=".6"/>' for a, b in FAST_PAIRS if a in by and b in by)


def frontier_caption(s):
    """Dataset-owned frontier eligibility and comparison for both main-ladder charts."""
    return '<p class="frontier-note">' + esc(s["facts"]["frontier_caption"]) + '</p>'


def grok_group_label(s):
    """Legend name for the Grok series. The counts come from the problems the plotted configs actually ran."""
    lane = s.get("grok") or {}
    covered = sorted({p for c, v in lane.items() if c not in configs.CHART_HIDDEN for p in v.get("by_problem") or {}})
    nprob = len(s.get("problems") or [])
    if not covered or not nprob:
        return None
    return f"Grok (all {nprob} problems)" if len(covered) == nprob else f"Grok ({len(covered)} of {nprob} problems)"


def ladder_toggle(render, s):
    normal, fr = render(s, free=False)
    free, _ = render(s, free=True)
    rescue_normal, _ = render(s, free=False, problem_set="rescue")
    rescue_free, _ = render(s, free=True, problem_set="rescue")
    note = ('<p class="repair-note">Codex counted at $0 on the Claude bill (it still spends Codex quota): its points move to the $0 lane. '
            'Each saving per pass is in the key and tooltip.</p>')
    main_categories = {point_category(c) for c in ORDER}
    chips = []
    for cat in ("main", "fast", "pipelines", "exploratory"):
        on_main = cat in main_categories
        chips.append(('<label>' if on_main else f'<label class="disabled" title="only on the {configs.set_label("rescue set")}">')
                     + f'<input type="checkbox" data-cat="{cat}" checked' + ('' if on_main else ' disabled')
                     + f'> {cat}</label>')
    legend = grok_group_label(s)
    if legend:  # no rescue key-group, so the page script disables this chip on the retest set
        chips.append(f'<label><input type="checkbox" data-cat="grok" checked> {esc(legend)}</label>')
    filters = '<div class="category-filter" role="group" aria-label="Point categories">' + "".join(chips) + '</div>'
    set_name = render.__name__ + "-set"
    sets = (f'<div class="set-filter" role="group" aria-label="Problem set">'
            f'<label><input type="radio" name="{set_name}" value="main" checked> {configs.set_label("main ladder", capital=True)}</label>'
            f'<label><input type="radio" name="{set_name}" value="rescue"> {configs.set_label("rescue set", capital=True)} + pipelines</label></div>')
    return ('<div class="cwrap"><label class="cost-toggle"><input type="checkbox"> Codex at $0 on the Claude bill (spends Codex quota)</label>'
            + sets + filters + note + '<div class="cset s-main">' + normal + free + frontier_caption(s) + '</div>'
            + '<div class="cset s-rescue">' + rescue_normal + rescue_free + '</div><div class="ctip" hidden></div></div>'), fr


def quota_tip(normal, free, saving):
    return (f'Normal: {dataset.usd(normal)} per pass; Codex $0 on the Claude bill: {dataset.usd(free)} per pass '
            f'(saving {dataset.usd(saving)} per pass).')


def ladder_repairs(free, stat, arms=None):
    """All rescue configs, including baselines measured on this same subset."""
    pts = []
    for c, name in NAME.items():
        v = (arms if arms is not None else rescue_arms())[c]
        builder = c.split("+", 1)[-1] if c.startswith("haiku-low-plan+") else c.split("+", 1)[0]
        usd = v["claude_usd_per_pass"] if free else v["usd_per_pass"]
        pts.append({"c": c, "name": name, "set": "rescue", "x": v["median_s"] if stat == "speed" else usd,
                    "y": usd if stat == "speed" else v["pass_rate"], "rate": v["pass_rate"], "hollow": "-fast" in builder, "dash": "bare" in builder,
                    "col": FAM(c),
                    "shape": SHAPE(builder), "w": None, "on": False, "free_mode": free,
                    "saved_usd": v["usd_saved_per_pass"], "normal_usd": v["usd_per_pass"], "free_usd": v["claude_usd_per_pass"],
                    "tip": f"{name}: {v['passes']}/{v['n']} passed. {dataset.usd(usd)} per pass. Median {dataset.median_seconds(v):.1f} s. {configs.set_label('rescue set', capital=True)} only. "
                    + quota_tip(v["usd_per_pass"], v["claude_usd_per_pass"], v["usd_saved_per_pass"])
                    + (" (" + v["derived_note"] + ")" if "derived_note" in v else "")})
    return pts


def grok_chart_points(s, stat):
    """Each plotted Grok config on its own rows. Cost stays the measured bill in both quota modes."""
    note = (s.get("facts") or {}).get("grok_chart_note", "")
    pts = []
    lane = s.get("grok") or {}
    for c in GROK_ORDER:
        v = lane.get(c)
        if not v or not v.get("usd_per_pass") or c in configs.CHART_HIDDEN:
            continue
        usd = v["usd_per_pass"]
        if stat == "speed":
            w = ("x", v["latency_s"]["p25"], v["latency_s"]["p75"]) if "p25" in v.get("latency_s", {}) else None
            x, y = v["latency_s"]["median"], usd
        else:
            w = ("y", v["ci95_plot"][0], v["ci95_plot"][1])
            x, y = usd, v["pass_at_1"]
        pts.append({"c": c, "name": DISP(c), "set": "main", "partial": True,
                    "x": x, "y": y, "rate": v["pass_at_1"], "hollow": "-fast" in c, "dash": "bare" in c, "w": w,
                    "saved_usd": v.get("usd_saved_per_pass") or 0, "normal_usd": usd, "free_usd": usd, "free_mode": False,
                    "tip": (f"{DISP(c)}: {v['passes']}/{v['n']} passed, {dataset.usd(usd)} per pass "
                            f"(measured bill), median {dataset.median_seconds(v):.1f} s. {note}")})
    return pts


def ladder_points(s, free, stat, problem_set):
    if problem_set == "rescue": return ladder_repairs(free, stat, rescue_arms(s))
    pts = []
    for c in ORDER:
        v = every(s)[c]; normal = v["usd_per_pass"]
        quota = v["claude_usd_per_pass"]
        usd = quota if free else normal
        w = (("x", v["latency_s"]["p25"], v["latency_s"]["p75"]) if "p25" in v["latency_s"] else None) if stat == "speed" else ("y", v["ci95_plot"][0], v["ci95_plot"][1])
        pts.append({"c": c, "name": DISP(c), "set": "main", "x": v["latency_s"]["median"] if stat == "speed" else usd,
                    "y": usd if stat == "speed" else v["pass_at_1"], "rate": v["pass_at_1"], "hollow": "-fast" in c, "dash": "bare" in c, "w": w,
                    "saved_usd": v["usd_saved_per_pass"], "normal_usd": normal, "free_usd": quota, "free_mode": free,
                    "tip": tip(c, dict(v, usd_per_pass=usd)) + ". " + quota_tip(normal, quota, v["usd_saved_per_pass"])})
    if problem_set == "main":
        pts.extend(grok_chart_points(s, stat))
    return pts


PICKS_NOTE = {"pass": "Nothing is both cheaper and more accurate. Shaded: beaten by a numbered point.",
              "speed": f"Nothing is both faster and cheaper. Shaded: a numbered point is cheaper and about as fast. Faded: under {MIN_PASS:.0%} pass."}
ZERO_LANE = {"pass": 110, "speed": 64}  # px kept for $0 points before a log $ axis starts


def pick(c):
    """A Winner pick, or a pipeline built on one."""
    return c.split("+")[0] in WINNER_PICKS


def zero_lane(log, at):
    """A log $ scale with $0 drawn in its own lane: log(0) has no position."""
    return lambda v: at if v == 0 else log(v)


def speed_cost(s, free=None, problem_set="main"):
    """Median seconds against paid $ per pass, log; frontier requires MIN_PASS."""
    if free is None: return ladder_toggle(speed_cost, s)
    L, R, T, B, W = 84, 16, 14, 410 if problem_set == "main" else 316, 560
    H = B + 58
    pts = ladder_points(s, free, "speed", problem_set)
    # Axis spans every median plus a margin, in 5 s blocks, so slower Grok points fit the same 560 px canvas. Whiskers are clipped to it.
    base = [p for p in pts if not p.get("partial")]  # Grok must not set the lowest $ or join the frontier
    xmin = max(0, math.floor((min(p["x"] for p in base) - 1) / 5) * 5)
    xmax = math.ceil((max(p["x"] for p in pts) + 1) / 5) * 5
    X = lambda v: L + (v - xmin) / (xmax - xmin) * (W - R - L)
    for p in pts:
        if p["w"]: p["w"] = ("x", max(xmin, p["w"][1]), min(xmax, p["w"][2]))
    paid = [p["y"] for p in base if p["y"] > 0]
    lo = 5e-4 if min(paid) >= 5e-4 else 10 ** math.floor(math.log10(min(paid)))
    lane = any(p["y"] == 0 for p in base)
    Y = zero_lane(logscale(lo, 3e-1, B - ZERO_LANE["speed"] * lane, T), B - 16)
    for p in pts: p["ok"] = (not p.get("partial")) and p.get("rate", 0) >= MIN_PASS
    ok = [p for p in pts if p["ok"]]
    fr = sorted(front(ok, speed_dominates), key=lambda p: p["x"])
    for p in pts:
        p["on"] = p in fr
        p["quiet"] = p["y"] == 0 and not p["on"] and not pick(p["c"])
    d = (f"M{X(fr[0]['x']):.1f} {Y(fr[0]['y']):.1f}" + "".join(f" H{X(p['x']):.1f} V{Y(p['y']):.1f}" for p in fr[1:]) + f" H{W - R}") if fr else ""
    step = next(v for v in (5, 10, 20, 25, 50) if len(range(xmin, xmax + 1, v)) <= 8)
    xt = [(v, f"{v} s") for v in range(xmin, xmax + 1, step)]
    # Keep unlabelled 5 s gridlines alongside the existing 1 s minor grid.
    minor = sorted(({v for v in range(xmin + 1, xmax) if v % 5}
                    | set(range(xmin, xmax + 1, 5))) - {v for v, _ in xt})
    yt = [(v, dataset.usd(v)) for v in (3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1) if v >= lo] + [(0, "$0")] * lane
    zero = f'<line x1="{L}" x2="{W - R}" y1="{B - 44}" y2="{B - 44}" stroke="var(--muted)" stroke-dasharray="2 4"/>' if lane else ""
    lab = {"luna-low": (0, -14, "middle"), "luna-medium": (14, 10, "start"), "haiku-low": (0, -20, "middle"), "luna-high": (14, -10, "start"),
           "haiku-medium": (14, 5, "start"), "sonnet-medium": (14, 4, "start"), "sol61-medium": (-14, -12, "end"),
           "luna56-high": (-14, 5, "end"), "luna56-low": (0, 26, "middle"), "haiku-high": (0, -14, "middle")}
    for p in pts:
        if pick(p["c"]): p["label"] = True
    xlab = "median seconds per call" + (" (bar on hover: middle half of calls)" if any(p["w"] for p in pts) else "")
    legend = grok_group_label(s)
    g = scatter(pts, d, X, Y, xt, yt, xlab, "$ per pass (log)", "", lab,
                H=H, B=B, extra=zero + fast_pairs(pts, X, Y), stat="speed", variant="free" if free else "normal",
                badges=True, picks_note=PICKS_NOTE["speed"],
                minor=minor,
                key_labels={"grok": legend} if legend else None)
    return g.replace("</svg>", f'<text x="{W - R - 6}" y="{T + 18}" text-anchor="end" class="better">↙ better</text></svg>', 1), [p["c"] for p in fr]


# Display names for rescue-set rows, used by every chart and table so a pipeline reads the same everywhere. luna-high on the hard
# set is the stripped harness (luna-high-bare); the name says so. Haiku in a pipeline reviews the answer and rewrites it if wrong.
from analysis.configs import RESCUE_NAMES as NAME
SHORT = lambda n: n.replace("Haiku plan → ", "plan→").replace(" → Haiku if samples fail", "→H fail").replace(" → Haiku fixes all", "→H all").replace(" → retry if samples fail", "→retry")


def rescue_arms(ds=None):
    """Cached measured and derived arms, including their validated provenance."""
    return (ds or dataset.read())["rescue"]


def grid(s, grok=None):
    """Problems (rows, by rung) × configs (columns); each cell is passes out of the attempts at that problem.
    grok maps each Grok config to {problem: [passes, attempts]}; a config that skipped a problem shows a dash there."""
    grok = grok or {}; cols = ORDER + [c for c in GROK_ORDER if c in grok] + list(configs.DEVIN_CONFIGS) + list(hetzner(s))
    E = {**every(s), **devin(s), **hetzner(s)}; probs = sorted(s["problems"], key=lambda p: (s["problems"][p]["rung"], p))
    main = set(probs)
    hard = sorted({p for v in s["hard"].values() for p in v["by_problem"]})
    def cell(p, c):
        if c in grok:
            k, n = grok[c].get(p, (None, None)); return (k, n)
        v = E.get(c) if p in main else s["hard"].get(c)
        cell = v["by_group"].get(p) if v else None
        return (cell["passes"], cell["n"]) if cell else (None, None)
    out = [f'<div class="grid" style="--n:{len(cols)};grid-template-columns:minmax(150px,auto) repeat({len(cols)},minmax(40px,1fr))">', '<div class="h m">problem</div>']
    out += [f'<div style="color:{FAM(c)}" class="h{" fast" if c.endswith("-fast") else " devin" if c in configs.DEVIN_CONFIGS else " hetzner" if c in configs.HETZNER_CONFIGS else ""}"'
            + (f' title="{esc(s["facts"]["devin_group"])}"' if c in configs.DEVIN_CONFIGS else f' title="{esc(configs.HETZNER_NOTE)}"' if c in configs.HETZNER_CONFIGS else "") + f'>{esc(DISP(c))}</div>' for c in cols]
    for p in probs + hard:
        if p == hard[0]: out.append(f'<div class="set-separator" style="grid-column:1 / -1">L7 set</div>')
        rung = s["problems"][p]["rung"] if p in main else 7
        out.append(f'<div class="m">{plabel_html(p, rung)}'
                   f'<span class="lc {LC[p].lower()}" title="{LC[p]}: my LeetCode difficulty guess">{LC[p][0]}</span></div>')
        for c in cols:
            k, n = cell(p, c)
            if k is None:
                out.append('<div class="muted">–</div>'); continue
            cls = "pass" if k == n else "part" if k * 2 > n else "fail"
            out.append(f'<div class="{cls}" title="{esc(DISP(c))} on {esc(plabel(p, rung))}: {k} of {n} passed">{k}/{n}</div>')
    out.append("</div>")
    return "".join(out)


def floor(s):
    """Input bars fit a phone; the darker share was cached."""
    E = every(s)
    names = [("haiku-low", "haiku-low"), ("sonnet-medium", "sonnet-medium"),
             ("luna-low", "luna-low, Codex's normal prompt"), ("sol61-medium", "sol61-medium"),
             ("luna-low-bare", "luna-low, trimmed prompt")]
    names += [(c, DISP(c)) for c in E if c.endswith("-fast")]
    names.sort(key=lambda row: configs.low_context(row[0]))
    rows = [(name, E[c]["tokens_mean"]["in_tok"], FAM(c), False) for c, name in names]
    low = next((i for i, (c, _) in enumerate(names) if configs.low_context(c)), None)
    body = charts.bars("Mean input tokens per call", rows, lambda v: f"{v:,.0f}",
                       "Solid = cached input. Faded = uncached input.", low_start=low,
                       cached=[E[c]["tokens_mean"]["cached_tok"] / E[c]["tokens_mean"]["in_tok"] for c, _ in names], responsive=True)
    return '<div class="compact-bars">' + body + '</div>'


PIPE_GROUPS = [("Single models", lambda c: "+" not in c),
               ("Build, then Haiku fixes it only if a sample test fails (→H fail)", lambda c: c.endswith("+haiku-on-fail")),
               ("Haiku checks every answer (→H all)", lambda c: c.endswith("+haiku-review-all")),
               ("Plan first, then build (plan→)", lambda c: c.startswith("haiku-low-plan+")),
               ("Retry once if a sample test fails (→retry)", lambda c: c.endswith("+retry-on-fail"))]


def pipes(arms=None):
    """Rows grouped under plain headings; fast-mode rows get a striped fill so they never read as empty."""
    a = arms if arms is not None else rescue_arms()
    entries = sorted(NAME.items(), key=lambda row: configs.low_context(row[0], "rescue"))
    assert sorted(c for _, test in PIPE_GROUPS for c, _ in entries if test(c)) == sorted(NAME), "every pipeline row needs a group"
    body = [f'<b class="bar-title">{esc(configs.set_label("rescue set", capital=True))}</b>',
            '<p class="pg-key"><span><i style="--bar-color:var(--claude)"></i>Haiku</span><span><i style="--bar-color:var(--sonnet)"></i>Sonnet</span>'
            '<span><i style="--bar-color:var(--codex)"></i>Codex</span><span><i style="--bar-color:var(--codex56)"></i>older Codex</span>'
            '<span><i style="--bar-color:var(--pipeline)"></i>pipeline</span><span><i class="bar-hollow" style="--bar-color:var(--muted)"></i>⚡ fast mode</span></p>']
    for heading, test in PIPE_GROUPS:
        rows = []
        for c, name in (e for e in entries if test(e[0])):
            v = a[c]; low = configs.low_context(c, "rescue")
            if low and not any("Low context" in r for r in rows): rows.append('<p class="pg-d">Low context</p>')
            col = FAM(c)
            fill = f'<span class="bar-fill{" bar-hollow" if "-fast" in c else ""}" style="--bar-color:{col};--bar-width:{100 * v["pass_rate"]:.3f}%"></span>'
            rows.append(f'<div class="pg-row"><span class="bar-name">{esc(name)}</span><span class="bar-track">{fill}</span>'
                        f'<span class="bar-value">{v["passes"]}/{v["n"]} · {esc(dataset.usd(v["usd_per_pass"]))} · {v["median_s"]:.0f}s</span></div>')
        body.append(f'<div class="pg" role="group" aria-label="{esc(heading)}"><p class="pg-h">{esc(heading)}</p>{"".join(rows)}</div>')
    return '<div class="pipes">' + "".join(body) + '</div>'


def hatch_phone(body):
    """charts.bars draws a fast-mode bar on phones as an outline only: add the same tint behind it."""
    return re.sub(r"<rect (x='[\d.]+' y='[\d.]+' width='[\d.]+' height='[\d.]+') fill='var\(--panel[^']*' stroke='([^']+)' stroke-width='2'/>",
                  lambda m: m[0] + f"<rect {m[1]} fill='{m[2]}' fill-opacity='.3'/>", body)


def fast(s):
    entries = [(label, c, group[c]) for label, group in ((configs.set_label("main ladder"), every(s)),
               (configs.set_label("L7 set"), s["hard"])) for pair in FAST_PAIRS for c in pair if c in group]
    rows = [(f"{'L7' if label == configs.set_label('L7 set') else 'ladder'} · {DISP(c)}",
             v["latency_s"]["median"], FAM(c), c.endswith("-fast")) for label, c, v in entries]
    values = [f"{dataset.median_seconds(v):.1f}s · {dataset.usd(v['usd_per_pass'])}" for _, _, v in entries]
    return '<div class="compact-bars">' + hatch_phone(charts.bars("Normal and fast mode", rows, str, "", values=values, responsive=True)) + '</div>'


def any_pair_data(s):
    """The explorer's numbers: a projection of the dataset, embedded in the page's data block. The script reads them from there."""
    points = [{"c": c, "d": DISP(c), "exp": e, "col": FAM(c), "fast": "-fast" in c,
               "mark": config_marker(c, 0, 0), "kind": v["cost_kind"], "pass": v["pass_at_1"], "usd": v["usd_per_pass"], "usd_text": v["usd_text"],
               "med": v["latency_s"]["median"], "inp": v["tokens_mean"]["in_tok"], "rsn": v["tokens_mean"]["reasoning_tok"]}
              for e, group in ((False, s["configs"]), (True, every(s))) for c, v in group.items()
              if e == (c not in s["configs"])]  # Devin has no $, so it stays out of the any-two-measures plot
    d = s["design"]["explorer"]
    return {"points": points, "usd_ticks": s["design"]["usd_ticks"], "floors": d["floors"], "default_floor": d["default_floor"], "tie": d["tie"]}


def any_pair(s):
    """Render interactive geometry around the embedded measurements and dollar labels."""
    src = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "page", "any_pair.html")
    options = '<option value="0">all shown</option>' + "".join(f'<option value="{f}">pass rate ≥ {round(100 * f)}%</option>' for f in s["design"]["explorer"]["floors"])
    body = open(src).read().replace("__FLOOR_OPTIONS__", options)
    # Reuse the historical speed chart, including server-rendered main/rescue and list/free variants.
    speed, _ = speed_cost(s)
    link = heading_link("speed-vs-per-pass", "Speed vs $ per pass")
    body = body.replace("__SPEED_COST__", speed).replace("__SPEED_LINK__", link)
    body = body.replace("frontier over", "best trade-offs over")
    older = s["exploratory"]["sol56-high"]["model"].split("-")[1]
    body = body.replace("Hollow = exploratory config. Codex $ is a proxy.",
                        f"Solid = normal speed. Hollow = fast mode. Dashed edge = bare prompt. Alternate Codex colour = {older} generation. Shapes match the charts above. Labels connect to their own points. Codex $ is a list-price estimate.")
    # Match the static speed chart: differences below both the absolute and the relative tolerance (design.explorer.tie) are ties.
    body = body.replace('return M[k].up?a>=b:a<=b', 'return k=="med"?a<=b+Math.min(X.tie.abs_s,X.tie.rel*b):M[k].up?a>=b:a<=b')
    body = body.replace('return M[k].up?a>b:a<b', 'return k=="med"?a<=b-Math.min(X.tie.abs_s,X.tie.rel*b):M[k].up?a>b:a<b')
    body = body.replace('sx.t.forEach(function(v){', 'var tickEnd=-Infinity; sx.t.forEach(function(v){')
    body = body.replace('if(x<L-1||x>W-R+1)return;',
                        'if(x<L-1||x>W-R+1)return;var tw=tf(st.x,v).length*(small?6:7);if(x-tw/2<tickEnd+10)return;tickEnd=x+tw/2;')
    start, end = body.index(' var placed=[];'), body.index(" box.innerHTML='<svg")
    body = body[:start] + r"""
 var placed=[],dots=pts.map(function(p){return [sx.f(p[st.x]),sy.f(p[st.y])]}),fontSize=small?11:12;
 var measure=document.createElement('canvas').getContext('2d');measure.font=fontSize+'px '+getComputedStyle(document.body).fontFamily;
 pts.forEach(function(p){var x=sx.f(p[st.x]),y=sy.f(p[st.y]),onf=fr.indexOf(p)>=0;
  g.push('<g class="explorer-point" tabindex="0" role="button" aria-label="'+esc('Inspect measurements for '+p.d)+'" aria-controls="pair-tip" aria-expanded="false" data-i="'+D.indexOf(p)+'" data-x="'+x+'" data-y="'+y+'" transform="translate('+x+' '+y+')" style="cursor:pointer">'+
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


def explorer_data(s):
    """The browser sees only the canonical dataset's explorer projection."""
    exp = s["explorer"]
    # The browser computes subset membership. Only axis extents are needed
    # from the stored comparisons; model panels and repeated view graphs aren't.
    sets = [dict(st, views={price: {"extents": group["extents"]}
                            for price, group in st["views"].items()}) for st in exp["sets"]]
    keep = {"key", "set", "config", "display", "family", "generation", "model_short",
            "effort", "mode", "prereg", "provenance", "fast_twin", "passes", "n",
            "pass_rate", "ci95_plot", "usd_per_pass", "quota_usd_per_pass",
            "cost_kind", "median_s", "winner_pick", "panel", "complete_marker",
            "coverage_note", "rule", "derived", "derived_note"}
    def rounded(value):
        if isinstance(value, float): return float(f"{value:.8g}")
        if isinstance(value, list): return [rounded(v) for v in value]
        if isinstance(value, dict): return {k: rounded(v) for k, v in value.items()}
        return value
    return dict({k: v for k, v in exp.items() if k not in {"rows", "sets", "winner_picks", "winner_pricing", "legacy_rule", "rule", "floors", "tie"}},
                sets=rounded(sets), empty_heading=explorer_heading(),
                rows=[dict({k: v for k, v in r.items() if k in keep},
                           ci95_plot=rounded(r["ci95_plot"]),
                           heading_id="config-" + anchor_slug(r["display"])) for r in exp["rows"]])


def explorer(s):
    exp = s["explorer"]
    st = next(st for st in exp["sets"] if st["id"] == exp["default_set"])
    rows = [r for r in exp["rows"] if r["key"] in st["rows"]]
    membership = st["views"]["list"]["front"]["membership"]
    plotted = [r for r in rows if r["cost_kind"] != "unmetered" and r["usd_per_pass"] is not None]
    legend = {charts.explorer_family_label(r):
              charts.explorer_colour(r) for r in plotted}
    fr = sorted([r for r in plotted if membership[r["key"]]["on_frontier"]], key=lambda r:(r["usd_per_pass"], r["key"]))
    button = lambda r: f'<button class="btn" data-key="{esc(r["key"])}">{esc(r["display"])} · {charts.explorer_cost_label(r)}</button>'
    detail = ""
    if plotted:
        r = plotted[0]
        detail = (explorer_heading(r) + f'<p>{r["passes"]}/{r["n"]} passed · {dataset.usd(r["usd_per_pass"])} per pass · {r["median_s"]:g} s median</p>'
                  f'<p class="ex-meta">CI {100*r["ci95_plot"][0]:.1f}%–{100*r["ci95_plot"][1]:.1f}% · {esc(charts.explorer_cost_label(r))} · {esc(r["provenance"])} · {esc(r["rule"])}</p>')
    tokens = {
        "__VIEW_BUTTONS__": "".join(f'<button class="btn" data-view="{v}" aria-pressed="{str(v == exp["default_view"]).lower()}">{esc(spec["label"])}</button>' for v, spec in exp["views"].items()),
        "__SET_OPTIONS__": "".join(f'<option value="{esc(t["id"])}">{esc(t["label"])}</option>' for t in exp["sets"]),
        "__FLOOR_OPTIONS__": "".join(f'<option value="{v}">{"Any" if not v else "≥ " + str(round(v*100)) + "%"}</option>' for v in exp["floors"]),
        "__SET_NOTE__": esc(st["note"]),
        "__LEGEND__": " · ".join(f'<span style="border-left:8px solid {colour};padding-left:6px;">{esc(label)}</span>' for label, colour in legend.items()),
        "__EXPLORER_SVG__": charts.explorer_svg(exp, width=320),
        "__EXCLUDED__": " ".join(esc(r["display"] + ": cost unavailable. Use Speed × Pass.") for r in rows if r not in plotted),
        "__CHIPS__": "".join(f'<li><b>{i}</b>'+button(r)+"</li>" for i,r in enumerate(fr,1)),
        "__DETAIL__": detail,
        "__CONFIG_BUTTONS__": "".join(f'<button class="btn" data-config="{esc(r["key"])}" aria-pressed="true">{esc(r["display"])} · {charts.explorer_cost_label(r)}</button>' for r in rows),
        "__FACET_BUTTONS__": "".join(f'<button class="btn" data-facet="{esc(k)}" aria-pressed="true">{esc(label)}</button>'
                                   for k,label in [("family:"+f,f) for f in sorted({r["family"] for r in exp["rows"]})]
                                   + [("mode:"+m,m) for m in ("normal","fast","bare","pipeline")]
                                   + [("generation:5.6","gpt-5.6")]) + '<button class="btn" data-facet="prereg" aria-pressed="false">Pre-registered only</button>',
    }
    body = open(os.path.join(os.path.dirname(__file__), "..", "docs", "page", "explorer.html")).read()
    for key,value in tokens.items(): body = body.replace(key,value)
    return body


def verdict(c, v, need, E, arms=None):
    """One word per config; each is checked against the data so the table cannot drift from it."""
    if c == "haiku-medium":
        need(v["passes"] == v["n"] - 1 and (arms if arms is not None else rescue_arms())[c]["passes"] == (arms if arms is not None else rescue_arms())[c]["n"], "haiku-medium: one miss, none on the rescue set")
        return f"missed {v['n'] - v['passes']}"
    if c == "haiku-high":
        need(v["passes"] == v["n"] and v["usd_per_pass"] == min(E[d]["usd_per_pass"] for d in ORDER if E[d]["passes"] == E[d]["n"]), "haiku-high is the cheapest with 0 misses")
        return "✓ pick (budget)"
    if c == "sol61-high-fast":
        need(v["passes"] == v["n"] == 60, "Winner sol61-high ⚡ passed every main-ladder answer")
        return "✓ pick"
    if c == "sonnet-medium":
        need(v["passes"] == v["n"], "Winner speed pick has no misses")
        return "✓ pick (speed)"
    if c == "luna-high":
        need(v["usd_per_pass"] > E["luna-low"]["usd_per_pass"] and v["passes"] > E["luna-low"]["passes"], "luna-high trades cost for more passes")
        return "trade-off"
    if v["passes"] == v["n"]: return "0 misses"
    if v["pass_at_1"] < MIN_PASS: return "avoid"
    dominated = any(d != c and E[d]["usd_per_pass"] <= v["usd_per_pass"] and E[d]["pass_at_1"] >= v["pass_at_1"] for d in ORDER)
    return "beaten" if dominated else "trade-off"


# Hard-set rows for the results table: single models, then pipelines (arrow = a second model or call after the first).
HARD = list(NAME.items())


def dot(col, grok=False):
    """The family-colour swatch before a config name, with Grok's surface ring."""
    return f'<span class="dot" style="background:{col}{";box-shadow:0 0 0 1.5px var(--panel)" if grok else ""}"></span>'


def row(name, col, k, n, usd, cusd, sec, verdict, proxy=False, derived="", *, rate, key="", set_name="", cost_label=None, missing_label=None):
    r = rate; cls = "good" if r >= 0.95 else "warn" if r >= MIN_PASS else "bad"
    attr = f' title="{esc(derived)}"' if derived else ""
    suffix = f'<span class="muted"> · {esc(set_name)}</span>' if set_name else ""
    price = lambda value: missing_label if value is None and missing_label else dataset.usd(value)
    seconds = f"{sec:.1f}" if sec is not None else "not measured"
    return (f'<tr{attr}><td>{dot(col)}{esc(name)}{suffix}</td><td><span class="pill {cls}">{100 * r:.0f}% ({k}/{n})</span></td>'
            f'<td>{configs.cell_markup(("~" if proxy else "") + (cost_label or price(usd)))}</td><td>{price(cusd)}</td><td>{seconds}</td><td class="verdict-cell" title="{esc(key)}">{verdict}</td></tr>')


def grok_results(s):
    """Group Grok by measured problem coverage and repeats, independently of retest rows."""
    groups = {}
    for c in GROK_ORDER:
        v = (s.get("grok") or {}).get(c)
        if not v: continue
        problems = tuple(sorted(v["by_group"]))
        repeats = sorted({g["n"] for g in v["by_group"].values()})
        full = set(problems) == set(s["problems"])
        scope = "main ladder" if full else "partial ladder"
        repeat_label = str(repeats[0]) if len(repeats) == 1 else f"{repeats[0]}–{repeats[-1]}"
        label = f"Grok · {scope} ({problems[0][:3]}–{problems[-1][:3]}). {repeat_label} repeats per problem."
        missed = v["n"] - v["passes"]
        beaten = full and any(
            o["pass_at_1"] >= v["pass_at_1"]
            and dataset.median_seconds(v) is not None
            and dataset.median_seconds(o) < dataset.median_seconds(v)
            and o["usd_per_pass"] is not None and v["usd_per_pass"] is not None
            and o["usd_per_pass"] < v["usd_per_pass"] for o in every(s).values())
        verdict = ("beaten; " if beaten else "partial ladder; " if not full else "") + (
            f"missed {missed}" if missed else "0 misses")
        floor = bool(v.get("outcomes", {}).get("timeout")) and v["usd_per_pass"] is not None
        note = "Unbilled timeout; cost per pass is a lower bound." if floor else ""
        body = row(DISP(c), FAM(c), v["passes"], v["n"], v["usd_per_pass"], v["claude_usd_per_pass"],
                   dataset.median_seconds(v), verdict, derived=note, rate=v["pass_at_1"],
                   key=s["facts"]["verdict_key"],
                   cost_label="≥" + dataset.usd(v["usd_per_pass"]) if floor else None, missing_label="no data")
        groups.setdefault(label, []).append(body)
    return "".join('<tbody><tr class="grp"><th colspan="6">' + esc(label) + '</th></tr>'
                   + "".join(rows) + '</tbody>' for label, rows in groups.items())


CODEX = lambda c: any(x in c for x in ("luna", "sol", "astra"))


def short_table(s, need):
    """One table grouped by measured problem coverage; each group sorts separately."""
    E = every(s); a = rescue_arms(s)
    top = [(c, row(DISP(c), FAM(c), E[c]["passes"], E[c]["n"], E[c]["usd_per_pass"], 0.0 if CODEX(c) or c in ("terra61-low-fast", "terra61-high-fast") else E[c]["usd_per_pass"],
               dataset.median_seconds(E[c]), verdict(c, E[c], need, E, a) + ("; " + s["facts"]["terra_noise_caveat"] if c in ("terra61-high", "terra61-high-fast") else ""),
               E[c]["cost_kind"] == "proxy", rate=E[c]["pass_at_1"], key=s["facts"]["verdict_key"],
               set_name=configs.set_label("main ladder") if configs.low_context(c) else "")) for c in ORDER]
    clean = [c for c, _ in HARD if a[c]["passes"] == a[c]["n"]]; need(clean, "some rescue-set row never failed")
    hv = lambda c: "0 misses" if c in clean else f"missed {a[c]['misses']}"
    duplicates = set(configs.PLAIN_PIPELINE_DUPLICATES)
    hard = [(c, row(SHORT(name), FAM(c), a[c]["passes"], a[c]["n"], a[c]["usd_per_pass"], 0.0 if CODEX(c) and "+" not in c else a[c]["claude_usd_per_pass"],
                dataset.median_seconds(a[c]), hv(c), CODEX(c), a[c].get("derived_note", ""), rate=a[c]["pass_rate"], key=s["facts"]["verdict_key"],
                set_name=configs.set_label("rescue set") if configs.low_context(c, "rescue") else "")) for c, name in HARD if c not in duplicates]
    dv = devin(s)
    dv_rows = [(c, row(DISP(c), FAM(c), v["passes"], v["n"], None, None, dataset.median_seconds(v), "not a delegate (free tier)",
                       rate=v["pass_at_1"], key=s["facts"]["verdict_key"])) for c, v in dv.items()]
    devin_rows = ('<tr class="grp"><th colspan="6">' + esc("Devin: " + configs.DEVIN_NOTE) + '</th></tr>' if dv_rows else "") + "".join(b for _, b in dv_rows)
    hz = hetzner(s)
    hetzner_rows = [(c, row(DISP(c) + " †", FAM(c), v["passes"], v["n"], None, None, dataset.median_seconds(v),
                    "usable but slow; not recommended", derived=configs.HETZNER_NOTE,
                    rate=v["pass_at_1"], key=s["facts"]["verdict_key"], cost_label="free tier")) for c, v in hz.items()]
    problems = sorted(s["problems"])
    def group(label, rows, source, extra=""):
        regular = "".join(body for c, body in rows if not configs.low_context(c, source))
        return f'<tbody><tr class="grp"><th colspan="6">{esc(label)}</th></tr>{regular}{extra}</tbody>'
    low = ([f"{DISP(c)} passed {E[c]['passes']}/{E[c]['n']} on the {configs.set_label('main ladder')}." for c in ORDER if configs.low_context(c)]
           + [f"{SHORT(name)} passed {a[c]['passes']}/{a[c]['n']} on the {configs.set_label('rescue set')}." for c, name in HARD
              if c not in duplicates and configs.low_context(c, "rescue")])
    low_group = ('<tbody class="low-context"><tr class="grp"><th colspan="6">'
                 + esc("Low context (trimmed prompt): " + " ".join(low)) + '</th></tr></tbody>')
    repeats = E[ORDER[0]]["n"] // len(problems)
    ladder_label = f'{configs.set_label("main ladder", capital=True)}: {len(problems)} problems × {repeats} tries = {E[ORDER[0]]["n"]} calls'
    subset_label = f'{configs.set_label("rescue set", capital=True)}: {len(s["design"]["rescue_problems"])} problems × {repeats} tries = {a[HARD[0][0]]["n"]} attempts'
    return ('<div class="tablewrap"><table class="sortable"><thead><tr><th>config</th><th>passed</th><th>$ per pass</th>'
            '<th>Claude $</th><th>median s</th><th>verdict</th></tr></thead>'
            + group(ladder_label, top, "main", extra=(
                '<tr class="grp"><th colspan="6">' + esc("Main ladder: Hetzner " + configs.HETZNER_NOTE)
                + '</th></tr>' + "".join(body for _, body in hetzner_rows)))
            + grok_results(s) + group(subset_label, hard, "rescue", extra=devin_rows) + low_group + '</table></div>')


def result_notes(s):
    """Shared scope notes for the Results section's tables."""
    problems = sorted(s["problems"]); rungs = [v["rung"] for v in s["problems"].values()]
    return ('<ul class="tight small">'
            f'<li>Ladder problems: {problems[0][:3]}–{problems[-1][:3]}. Rungs: L{min(rungs)}–L{max(rungs)}.</li>'
            '<li>Low-context rows use trimmed prompts. Other variants: Notes → Everything we tried.</li></ul>')


def full_table(ds):
    """Retain every interval, tail latency and total in a compact grouped table."""
    spec = ds["tables"]["result_detail"]
    label = configs.set_label("main ladder", capital=True)
    low_names = {configs.display(c) + " †" for source, c in configs.REGISTRY if source == "main" and configs.low_context(c)}
    def rows(low):
        return "".join('<tr>' + "".join(f'<td>{configs.cell_markup(esc(cell))}</td>' for cell in r) + '</tr>'
                       for r in spec["rows"] if (r[0] in low_names) == low)
    return ('<div class="tablewrap"><table class="sortable"><thead><tr>'
            + "".join(f'<th>{esc(h)}</th>' for h in spec["head"]) + '</tr></thead>'
            f'<tbody><tr class="grp"><th colspan="4">{esc(label)}</th></tr>{rows(False)}</tbody>'
            f'<tbody class="low-context"><tr class="grp"><th colspan="4">Low context: trimmed prompt</th></tr>{rows(True)}</tbody>'
            '</table></div>')




REPO = "https://github.com/chimera-defi/dispatchbench/blob/main/bench/problems/"


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
            "p13_xor_ring": ("Prison Cells After N Days", "prison-cells-after-n-days"),
            "p14_bounce_board": ("Snakes and Ladders", "snakes-and-ladders"),
            "p15_paint_erase": ("Range Module", "range-module")}
# The pilot's well-known LeetCode problems, in the order the pilot ran them (round 1, then the harder round 2).
PILOT = [("Fizz Buzz", "fizz-buzz", "Easy"), ("Course Schedule II", "course-schedule-ii", "Medium"), ("Candy", "candy", "Hard"),
         ("Reconstruct Itinerary", "reconstruct-itinerary", "Hard"), ("Minimum Window Substring", "minimum-window-substring", "Hard"),
         ("Wildcard Matching", "wildcard-matching", "Hard")]


def method(s):
    lvl = lambda d: f'<span class="lc {d.lower()}" title="{d}: my LeetCode difficulty guess">{d[0]}</span>'
    like = lambda p: (f'<br><span class="like">like <a href="https://leetcode.com/problems/{ANALOGUE[p][1]}/" title="closest LeetCode analogue, not the source">{esc(ANALOGUE[p][0])}</a></span>'
                      if ANALOGUE.get(p) else '<br><span class="like">no close LeetCode analogue</span>')
    # Problem name includes its rung; the difficulty badge trails the name.
    description = lambda p: TESTS[p].replace("for huge t", f"for t ≤ {s['design']['xor_time_bound']}")
    def item(p, r):
        from bench.problems import load
        module = load(p)
        identifier = p.split("_", 1)[0]
        return (f'<li class="prow" id="{identifier}"><span class="pn" id="{esc(p)}"><code>{esc(plabel(p, r))}</code>{heading_link(identifier, plabel(p, r))} {lvl(LC[p])}{like(p)}</span>'
                f'<span class="pd">{esc(description(p))}</span>'
                f'<details class="problem-try" id="{identifier}-try"><summary>Try it</summary>'
                f'<pre class="problem-signature"><code>{esc(module.SIGNATURE)}</code></pre>'
                f'<pre class="problem-statement"><code>{esc(module.STATEMENT)}</code></pre>'
                f'<p><a href="{REPO}{p}.py">reference solution (spoiler)</a></p></details></li>')
    main = sorted(s["problems"], key=lambda p: (s["problems"][p]["rung"], p))
    hard = sorted({p for v in s["hard"].values() for p in v["by_problem"]})
    li = [f'<li class="round"><b>{configs.set_label("main ladder", capital=True)}</b>: {len(main)} new problems.<ul>'
          + "".join(item(p, s["problems"][p]["rung"]) for p in main) + "</ul></li>",
          f'<li class="round"><b>{configs.set_label("L7 set")}</b>: extra-hard problems, scored separately.<ul>'
          + "".join(item(p, 7) for p in hard) + "</ul></li>"]
    return "".join(li)


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
        "≥N%": r"≥N%|≥\d+% \(all passed\)",
        "H": r"(?<=→)H\b|\bH (?:fail|all)\b",
        "L1–L7": r"\bL\d+(?:\s*(?:to|[–-])\s*L\d+)?\b",
        "noshell B1/B2": r"\bnoshell[- ]B[12]\b|\bB[12]\b",
        "–": r"(?<!\w)–(?!\w)",
    }
    patterns = []
    symbols = sorted(meanings, key=len, reverse=True)
    for i, symbol in enumerate(symbols):
        pattern = aliases.get(symbol, re.escape(symbol))
        if symbol in ("H", "retry", "slow-call time", "pass@1"):
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
            # Terminate inline CSS declarations so tooling cannot read a later
            # prose colour word as part of the preceding style value.
            raw = re.sub(r'(style="[^"]*?)(?<!;)"', r'\1;"', raw)
            values = dict(attrs)
            if "dot" in values.get("class", "").split():
                symbol = "purple dot" if "--frontier" in values.get("style", "") else "family dots"
                if symbol in meanings and symbol not in self.seen:
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
            if any(tag in ("script", "style", "title", "option", "textarea") or attrs.get("id") == "notation" or "problem-try" in attrs.get("class", "").split()
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
    """Three primary choices; secondary routes retain their separately measured scope."""
    ladder = lambda c: dataset.get(ds, c, "main ladder")
    plain, budget, speed, default = map(ladder, ("sol61-high", "haiku-high", "sonnet-medium", "sol61-high-fast"))
    pipeline = dataset.get(ds, "sol61-high+haiku-on-fail", "rescue arms", "rescue")
    clean = [r for r in ds["rows"] if r["set"] == "main ladder" and r["passes"] == r["n"]]
    need(budget["usd_per_pass"] == min(r["usd_per_pass"] for r in clean), "Winner budget pick is the cheapest with no misses")
    for pick in (plain, budget, speed, default):  # sol61-high ⚡ has no repo-task run; plain sol61-high covers that model
        for set_, source in (("main ladder", "main"), ("L7 set", "main"), ("repo tasks", "agentic"))[:2 if pick is default else 3]:
            r = dataset.get(ds, pick["config"], set_, source)
            need(r["passes"] == r["n"], f"Winner {pick['config']} never missed on {set_}")
    need(speed["median_s"] < budget["median_s"], "Winner speed pick is faster than the budget pick")
    need(default["median_s"] < plain["median_s"], "Winner fast mode reduces time")
    need(default["tokens_in_mean"] == plain["tokens_in_mean"]
         and default["tokens_out_mean"] <= plain["tokens_out_mean"],
         "Winner fast-mode premium does not come from more tokens")
    need(pipeline["passes"] == pipeline["n"] and pipeline["spend_claude"] == 0,
         "Winner measured example-check pipeline passed without calling Haiku")
    F = ds["facts"]
    faster = next(r for r in clean if r["display"] == F["fastest_nomiss"])
    need(faster["passes"] == faster["n"] == 60 and faster["median_s"] < default["median_s"]
         and 3 < default["usd_per_pass"] / faster["usd_per_pass"] < 4,
         "fastest no-miss main-ladder config is faster and about three times cheaper than Default")
    astra = ladder("astra-medium-fast")
    quota = astra["usd_per_pass"] / default["usd_per_pass"]
    need(astra["passes"] == astra["n"] and astra["median_s"] < default["median_s"] and quota > 2,
         "astra-medium ⚡ is faster but burns much more Codex quota")
    why = {"default": (f"No misses. $0 on the Claude bill (spends Codex quota). ⚡ saves {plain['median_s'] - default['median_s']:.0f} s. "
                       f"astra ⚡ is faster but uses {quota:.0f}× the quota. "
                       f"{F['fastest_nomiss']} is faster ({F['fastest_nomiss_med']} s) and ~{F['terra_fast_cheaper']} cheaper; {F['terra_low_l7_miss']} L7 miss per tier, {F['terra_low_l7_clause']}"),
           "budget": F["budget_why"], "speed": F["speed_why"]}
    choices = [(use.title(), ladder(c), why[use]) for c, use in WINNER_PICKS.items()]
    head = ("Use case", "Pick", "Pass", "$ per pass", "Time", "Why")
    th = "".join(f'<th scope="col">{esc(name)}</th>' for name in head)
    rows = []
    for i, (use, r, why) in enumerate(choices, 1):
        price = ("~" if r["cost_kind"] == "proxy" else "") + dataset.usd(r["usd_per_pass"])
        cells = (f"{i}. {use}", r["display"], f"{r['passes']}/{r['n']}", price, f"{dataset.median_seconds(r):.1f} s", why)
        rows.append('<tr>' + "".join(
            f'<td data-label="{esc(label)}"><span>{configs.cell_markup(esc(cell))}</span></td>' for label, cell in zip(head, cells)) + '</tr>')
    caption = ds["facts"]["winner_caption"]
    return ('<div class="tablewrap"><table class="winner-table">'
            f'<caption>{esc(caption)}</caption><thead><tr>{th}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>'
            '<ul class="tight small">' + "".join(f'<li>{esc(route)}</li>' for route in ds["facts"]["winner_other_routes"])
            + '</ul><p class="small">Caveat: sonnet-medium\'s code read worst in a blind review (see Notes).</p>')


def catalog_rows(ds):
    """Current evidence on the short page; superseded runs stay in raw sources."""
    return [r for r in dataset.catalog_rows(ds) if r["source"] not in {"pilot", "pilot-agentic"}
            and r["config"] != "luna-low+haiku-low-repair"]


def grok_summary(s, ds):
    lane = s.get("grok") or {}
    rows = []
    measurements = {r["config"]: r for r in ds["rows"]
                    if r["source"] == "main" and r["set"] in {"main ladder", "partial ladder"}}
    for c in lane:
        r = measurements[c]
        rows.append([DISP(c), f"{r['passes']}/{r['n']}",
                     f"{dataset.median_seconds(r):.1f}", dataset.usd(r["usd_per_pass"]),
                     "full ladder" if r["groups"] == len(s["problems"]) else f"{r['groups']} problems"])
    for c in devin(s):
        r = measurements[c]
        rows.append([DISP(c), f"{r['passes']}/{r['n']}",
                     f"{dataset.median_seconds(r):.1f}", "unmetered", "one try/problem"])
    from analysis import report
    table = report.to_html(report.md_table(["config", "passed", "median s", "$ per pass", "coverage"], rows), dots=True)
    repo = [r for r in ds["explorer"]["rows"] if r["source"] == "grok-repo" and r["set"] == "repo tasks"]
    full = [c for c, v in lane.items() if v["n"] == s["configs"]["haiku-low"]["n"]]
    dataset.need(all(lane[c]["passes"] < lane[c]["n"] for c in full), "full-ladder Grok configs missed")
    comparison = ds["grok_comparison"]
    m = comparison["metrics"]
    dataset.need(all(any(m[o]["pass_rate"] >= m[c]["pass_rate"]
                         and m[o]["median_s"] < m[c]["median_s"]
                         and m[o]["usd_per_pass"] < m[c]["usd_per_pass"]
                         for o in comparison["lanes"]) for c in full),
                 "comparable lanes beat every full-ladder Grok config on all three measures")
    bullets = ["Every full-ladder Grok config missed somewhere.",
               "Comparable Claude and Codex configs beat Grok on accuracy, speed, and cost."]
    bullets += [f"Repo tasks: {DISP(r['config'])} completed {r['task_complete']}/{r['n']} with all hidden tests passing."
                for r in repo]
    bullets += ["Grok's repository results allow tools; function results disable them.",
                "One killed Grok call was unbilled; high-effort cost is a lower bound.",
                "Devin used the free tier; it reports no tokens or cost.",
                "Devin has one attempt per problem, so its coverage differs."]
    return table + '<ul class="tight small">' + ''.join(f'<li>{esc(t)}</li>' for t in bullets) + '</ul>'


def widgets(s, need, ds=None, names=None):
    arms = rescue_arms(ds or s)
    renderers = {"grid": lambda: grid(s, (ds or dataset.read()).get("grok_comparison", {}).get("by_problem")), "floor": lambda: floor(s), "pipes": lambda: pipes(arms),
            "fast": lambda: fast(s), "any_pair": lambda: any_pair(s), "explorer": lambda: explorer(s), "short_table": lambda: short_table(s, need),
            "full_table": lambda: full_table(ds or dataset.read()), "result_notes": lambda: result_notes(s),
            "grok_summary": lambda: grok_summary(s, ds or dataset.read()),
            "winner": lambda: winner_table(ds or dataset.read(), need),
            "legend": lambda: legend(ds or dataset.read()),
            "problems": lambda: method(s)}
    return {name: draw() for name, draw in renderers.items() if names is None or name in names}
