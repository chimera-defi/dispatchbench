"""Draw the report charts as plain SVG from results/summary.json. Standard library only; no model calls."""
import json, math, os
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "report", "charts")
FONT = "font-family='-apple-system, Segoe UI, Helvetica, Arial, sans-serif'"
INK, MUTED, GRID = "#1f2328", "#59636e", "#e3e6ea"
# One hue per CLI; darker = more effort.
COLOR = {"haiku-low": "#f2a46b", "haiku-medium": "#d9692a", "haiku-high": "#a8471a", "sonnet-medium": "#8a3b12", "sonnet-high": "#5e260a",
         "luna-low": "#7fb2e5", "luna-medium": "#3a7cc4", "luna-high": "#1d4f8a", "sol61-medium": "#163a66", "sol61-high": "#0b213d"}


def svg(w, h, body):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' {FONT} font-size='12'>"
            f"<rect width='{w}' height='{h}' fill='white'/>{''.join(body)}</svg>\n")


def text(x, y, s, size=12, anchor="start", fill=INK, weight="normal", rotate=None):
    t = f" transform='rotate({rotate} {x} {y})'" if rotate else ""
    return f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' fill='{fill}' font-weight='{weight}'{t}>{escape(str(s))}</text>"


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
    extra = {c: v for c, v in (s.get("exploratory") or {}).items() if v["usd_per_pass"]}  # drawn hollow, not on the frontier
    cfg_all = {**cfg, **extra}
    W, H, L, R, T, B = 760, 480, 80, 30, 50, 80
    xs = [v["latency_s"]["median"] for v in cfg_all.values()]; ys = [v["usd_per_pass"] for v in cfg_all.values()]
    x0, x1 = min(xs) / 1.4, max(xs) * 1.4; y0, y1 = min(ys) / 1.6, max(ys) * 1.6
    X = lambda v: L + (math.log(v) - math.log(x0)) / (math.log(x1) - math.log(x0)) * (W - L - R)
    Y = lambda v: H - B - (math.log(v) - math.log(y0)) / (math.log(y1) - math.log(y0)) * (H - T - B)
    b = [text(L, 24, "Cost per passing solution vs median latency (function track, both axes log)", 14, weight="600")]
    for v in log_ticks(x0, x1):
        b += [f"<line x1='{X(v):.1f}' x2='{X(v):.1f}' y1='{T}' y2='{H - B}' stroke='{GRID}'/>", text(X(v), H - B + 18, f"{v:g} s", 11, "middle", MUTED)]
    for v in log_ticks(y0, y1):
        b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(v):.1f}' y2='{Y(v):.1f}' stroke='{GRID}'/>", text(L - 8, Y(v) + 4, fmt_usd(v), 11, "end", MUTED)]
    b += [text((L + W - R) / 2, H - B + 38, "median wall-clock seconds per call", 12, "middle", MUTED),
          text(20, (T + H - B) / 2, "$ per passing call", 12, "middle", MUTED, rotate=-90)]
    front = s["pareto"]
    if len(front) > 1:
        pts = " ".join(f"{X(cfg[c]['latency_s']['median']):.1f},{Y(cfg[c]['usd_per_pass']):.1f}" for c in front)
        b.append(f"<polyline points='{pts}' fill='none' stroke='{INK}' stroke-width='1.5' stroke-dasharray='5 4'/>")
    for i, (c, v) in enumerate(sorted(cfg.items(), key=lambda kv: kv[1]["latency_s"]["median"])):
        x, y = X(v["latency_s"]["median"]), Y(v["usd_per_pass"]); on = c in front; below = i % 2 == 1
        b.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{7 if on else 5.5}' fill='{COLOR.get(c, MUTED)}' stroke='{INK if on else 'white'}' stroke-width='1.5'/>")
        b.append(text(x + 10, y + 18 if below else y - 8, f"{c} ({100 * v['pass_at_1']:.0f}%){' *' if v['cost_kind'] == 'proxy' else ''}", 11))
    for c, v in extra.items():
        x, y = X(v["latency_s"]["median"]), Y(v["usd_per_pass"])
        b.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='5.5' fill='white' stroke='{COLOR['luna-low']}' stroke-width='2'/>")
        b.append(text(x - 4, y + 22, f"{c} ({100 * v['pass_at_1']:.0f}%) *, exploratory", 11, "end", MUTED))
    b.append(text(L, H - 10, "Dashed line: Pareto frontier. Percent: pass@1. Hollow: exploratory, not pre-registered. * Codex $ is a proxy (tokens × list price); Claude $ is measured.", 10, fill=MUTED))
    return svg(W, H, b)


def rung_chart(s):
    cfg = s["configs"]; rungs = sorted({g for v in cfg.values() for g in v["by_rung"]}, key=lambda g: int(g[1:]))
    W, H, L, R, T, B = 760, 420, 60, 170, 50, 50
    X = lambda i: L + i / max(1, len(rungs) - 1) * (W - L - R); Y = lambda p: H - B - p * (H - T - B)
    b = [text(L, 24, "Pass rate by difficulty rung (10 attempts per rung per config)", 14, weight="600")]
    for p in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(p):.1f}' y2='{Y(p):.1f}' stroke='{GRID}'/>", text(L - 8, Y(p) + 4, f"{100 * p:.0f}%", 11, "end", MUTED)]
    b.append(f"<line x1='{L}' x2='{W - R}' y1='{Y(0.4):.1f}' y2='{Y(0.4):.1f}' stroke='#b42318' stroke-dasharray='4 3'/>")
    b.append(text(W - R + 6, Y(0.4) + 4, "breaking point (≤ 40%)", 11, fill="#b42318"))
    for i, g in enumerate(rungs):
        b.append(text(X(i), H - B + 18, g, 11, "middle", MUTED))
    b.append(text((L + W - R) / 2, H - 12, "rung (L1 easiest)", 12, "middle", MUTED))
    n = len(cfg); labels = []
    for k, (c, v) in enumerate(cfg.items()):
        off = (k - (n - 1) / 2) * 3  # small horizontal jitter so overlapping lines stay visible
        pts = [(X(i) + off, Y(v["by_rung"][g]["passed"] / v["by_rung"][g]["n"])) for i, g in enumerate(rungs) if g in v["by_rung"]]
        b.append(f"<polyline points='{' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)}' fill='none' stroke='{COLOR.get(c, MUTED)}' stroke-width='2'/>")
        b += [f"<circle cx='{x:.1f}' cy='{y:.1f}' r='3.5' fill='{COLOR.get(c, MUTED)}'/>" for x, y in pts]
        labels.append((pts[-1][1], c))
    labels.sort(); last = -1e9
    for y, c in labels:  # spread end labels so they don't collide
        y = max(y, last + 14); last = y
        b.append(text(W - R + 6, y + 4 + 20, c, 11, fill=COLOR.get(c, MUTED)))
    return svg(W, H, b)


def heatmap(s):
    cfg = list(s["configs"]); probs = list(s["problems"])
    cw, ch, L, T = 92, 24, 210, 70
    W, H = L + cw * len(cfg) + 20, T + ch * len(probs) + 50
    b = [text(12, 24, "Passes out of 5 per problem and config", 14, weight="600")]
    for j, c in enumerate(cfg):
        b.append(text(L + j * cw + cw / 2, T - 10, c, 11, "middle", MUTED))
    for i, p in enumerate(probs):
        v = s["problems"][p]; y = T + i * ch
        b.append(text(L - 10, y + ch / 2 + 4, f"L{v['rung']}  {p}", 11, "end", INK))
        for j, c in enumerate(cfg):
            k = v[c]; shade = ["#b42318", "#e8705f", "#f4b8a8", "#cfe3c9", "#86c27a", "#2f8a3b"][k]
            b.append(f"<rect x='{L + j * cw + 1}' y='{y + 1}' width='{cw - 2}' height='{ch - 2}' fill='{shade}'/>")
            b.append(text(L + j * cw + cw / 2, y + ch / 2 + 4, k, 11, "middle", "white" if k in (0, 5) else INK))
    return svg(W, H, b)


def floor_chart(s):
    rows = [(c, "function", v["input_floor"][0], v["input_floor"][1]) for c, v in s["configs"].items()]
    rows += [(c, "agentic", v["input_floor"][0], v["input_floor"][1]) for c, v in (s.get("agentic") or {}).items()]
    W, L, R, T, bh = 760, 190, 90, 50, 20
    H = T + len(rows) * (bh + 8) + 70
    mx = max(r[2] for r in rows) * 1.05; X = lambda v: L + v / mx * (W - L - R)
    b = [text(12, 24, "Minimum input tokens over all calls (the harness floor), cached share shaded", 14, weight="600")]
    y = T; last = None
    for c, track, tot, cached in rows:
        if track != last:
            b.append(text(12, y + 12, f"{track} track", 11, fill=MUTED, weight="600")); y += 18; last = track
        b += [f"<rect x='{L}' y='{y}' width='{X(tot) - L:.1f}' height='{bh}' fill='{COLOR.get(c, MUTED)}' opacity='0.35'/>",
              f"<rect x='{L}' y='{y}' width='{X(cached) - L:.1f}' height='{bh}' fill='{COLOR.get(c, MUTED)}'/>",
              text(L - 8, y + 14, c, 11, "end"), text(X(tot) + 6, y + 14, f"{tot:,}", 11, fill=MUTED)]
        y += bh + 8
    b.append(text(12, y + 22, "Solid: served from cache. Pale: uncached input. Codex floors include ~1.3k tokens of user AGENTS.md the CLI cannot switch off.", 11, fill=MUTED))
    return svg(W, y + 40, b)


def agentic_chart(s):
    ag = s.get("agentic") or {}
    if not ag: return None
    W, H, L, R, T, B = 760, 420, 80, 30, 50, 80
    xs = [v["usd_per_run"] for v in ag.values()]
    x0, x1 = min(xs) / 1.5, max(xs) * 1.5
    X = lambda v: L + (math.log(v) - math.log(x0)) / (math.log(x1) - math.log(x0)) * (W - L - R); Y = lambda p: H - B - p * (H - T - B)
    b = [text(L, 24, "Agentic track: hidden-test pass rate vs $ per run (x log)", 14, weight="600")]
    for p in (0, 0.25, 0.5, 0.75, 1.0):
        b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(p):.1f}' y2='{Y(p):.1f}' stroke='{GRID}'/>", text(L - 8, Y(p) + 4, f"{100 * p:.0f}%", 11, "end", MUTED)]
    for v in log_ticks(x0, x1):
        b += [f"<line x1='{X(v):.1f}' x2='{X(v):.1f}' y1='{T}' y2='{H - B}' stroke='{GRID}'/>", text(X(v), H - B + 18, fmt_usd(v), 11, "middle", MUTED)]
    b += [text((L + W - R) / 2, H - B + 38, "$ per run", 12, "middle", MUTED), text(20, (T + H - B) / 2, "runs passing all hidden tests", 12, "middle", MUTED, rotate=-90)]
    for i, (c, v) in enumerate(sorted(ag.items(), key=lambda kv: kv[1]["usd_per_run"])):
        x, y = X(v["usd_per_run"]), Y(v["hidden_pass_rate"]); lo, hi = v["ci95"]
        if v["hidden_pass"] == v["n"]: lo = 0.05 ** (1 / v["n"])  # bootstrap collapses at 100%; use the exact one-sided bound
        b.append(f"<line x1='{x:.1f}' x2='{x:.1f}' y1='{Y(lo):.1f}' y2='{Y(hi):.1f}' stroke='{COLOR.get(c, MUTED)}' stroke-width='2' opacity='0.5'/>")
        b.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='6' fill='{COLOR.get(c, MUTED)}'/>")
        right = x > W - R - 150
        b.append(text(x - 10 if right else x + 10, y - 8 if i % 2 == 0 else y + 18, anchor="end" if right else "start", s=f"{c} {v['hidden_pass']}/{v['n']}{' *' if v['cost_kind'] == 'proxy' else ''}", size=11))
    b.append(text(L, H - 10, "Every config passed 12/12, so the track does not separate them. Bars: exact one-sided 95% lower bound. * Codex $ is a proxy.", 11, fill=MUTED))
    return svg(W, H, b)


def main():
    s = json.load(open(os.path.join(ROOT, "results", "summary.json")))
    os.makedirs(OUT, exist_ok=True)
    charts = {"pareto.svg": pareto_chart(s), "pass_by_rung.svg": rung_chart(s), "heatmap.svg": heatmap(s),
              "token_floor.svg": floor_chart(s), "agentic.svg": agentic_chart(s)}
    for name, body in charts.items():
        if body: open(os.path.join(OUT, name), "w").write(body)
    print("charts ->", os.path.relpath(OUT, ROOT), ", ".join(n for n, b in charts.items() if b))


if __name__ == "__main__":
    main()
