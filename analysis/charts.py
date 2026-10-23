"""Draw the report charts as plain SVG from results/summary.json. Standard library only; no model calls."""
import json, math, os
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
    extra = {c: v for c, v in (s.get("exploratory") or {}).items() if v["usd_per_pass"]}  # drawn hollow, not on the frontier
    allc = {**cfg, **extra}
    W, H, L, R, T, B = 760, 480, 96, 30, 50, 80
    xs = [v["usd_per_pass"] for v in allc.values()]
    x0, x1 = min(xs) / 1.6, max(xs) * 1.6; y0 = 0.6
    X = lambda v: L + (math.log(v) - math.log(x0)) / (math.log(x1) - math.log(x0)) * (W - L - R)
    Y = lambda p: H - B - (p - y0) / (1 - y0) * (H - T - B)
    b = [text(L, 24, "Pass rate vs cost per passing solution (function track, x log)", 14, weight="600")]
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
        x, y = X(v["usd_per_pass"]), Y(v["pass_at_1"]); on = c in front; hollow = c in extra
        lo, hi = v["ci95"]
        col = FAMILY(c)
        b.append(f"<line x1='{x:.1f}' x2='{x:.1f}' y1='{Y(max(lo, y0)):.1f}' y2='{Y(hi):.1f}' stroke='{col}' stroke-width='2' opacity='0.35'/>")
        if hollow:
            b.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='5.5' fill='{PLATE}' stroke='{col}' stroke-width='2'/>")
        else:
            b.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{7 if on else 5.5}' fill='{col}' stroke='{INK if on else PLATE}' stroke-width='1.5'/>")
        right = x > W - R - 170 or c in LABEL_LEFT
        label = f"{c} ({100 * v['pass_at_1']:.0f}%){' *' if v['cost_kind'] == 'proxy' else ''}{', exploratory' if hollow else ''}"
        b.append(text(x - 10 if right else x + 10, y + LABEL_DY.get(c, -8), label, 11, "end" if right else "start", MUTED if hollow else INK))
    b.append(text(L, H - 10, "Dashed: Pareto. Bars: 95% CI. Hollow: exploratory. * Codex cost is proxy.", 10, fill=MUTED))
    return svg(W, H, b)


MIN_PASS = 0.90
PURPLE = "var(--frontier,#7b3fe4)"


def cost_time_chart(s):
    """$ per pass against median latency, function track L1-L6. The frontier is drawn over configs at or above MIN_PASS
    pass@1: among those, the ones no other config beats on both cost and time."""
    allc = {**{c: v for c, v in s["configs"].items() if v["usd_per_pass"]}, **{c: v for c, v in (s.get("exploratory") or {}).items() if v["usd_per_pass"]}}
    pts = {c: (v["usd_per_pass"], v["latency_s"]["median"]) for c, v in allc.items()}
    ok = {c: p for c, p in pts.items() if allc[c]["pass_at_1"] >= MIN_PASS}
    front = [a for a, (x, y) in ok.items() if not any(x2 <= x and y2 <= y and (x2 < x or y2 < y) for b, (x2, y2) in ok.items() if b != a)]
    front.sort(key=lambda c: pts[c][0])
    W, H, L, R, T, B = 760, 440, 96, 30, 50, 80
    xs = [p[0] for p in pts.values()]; x0, x1 = min(xs) / 1.6, max(xs) * 1.6
    y1 = math.ceil(max(p[1] for p in pts.values()) / 5) * 5 + 5
    X = lambda v: L + (math.log(v) - math.log(x0)) / (math.log(x1) - math.log(x0)) * (W - L - R)
    Y = lambda t: H - B - t / y1 * (H - T - B)
    b = [text(L, 24, "Cost per passing solution vs median latency (function track, x log)", 14, weight="600")]
    for t in range(0, int(y1) + 1, 5):
        b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(t):.1f}' y2='{Y(t):.1f}' stroke='{GRID}'/>", text(L - 8, Y(t) + 4, f"{t} s", 11, "end", MUTED)]
    for v in log_ticks(x0, x1):
        b += [f"<line x1='{X(v):.1f}' x2='{X(v):.1f}' y1='{T}' y2='{H - B}' stroke='{GRID}'/>", text(X(v), H - B + 18, fmt_usd(v), 11, "middle", MUTED)]
    b += [text((L + W - R) / 2, H - B + 38, "$ per passing call", 12, "middle", MUTED),
          text(26, (T + H - B) / 2, "median seconds per call", 12, "middle", MUTED, rotate=-90)]
    if len(front) > 1:
        b.append(f"<polyline points='{' '.join(f'{X(pts[c][0]):.1f},{Y(pts[c][1]):.1f}' for c in front)}' fill='none' stroke='{PURPLE}' stroke-width='2.5' stroke-dasharray='6 4'/>")
    dy = {"luna-low": 16, "sonnet-medium": 16, "haiku-low": -12, "luna-medium": 4}; left = {"luna-high", "luna-low-bare"}
    for c, (x, t) in pts.items():
        hollow = c not in s["configs"]; px, py = X(x), Y(t)
        col = FAMILY(c)
        b.append(f"<circle cx='{px:.1f}' cy='{py:.1f}' r='6' fill='{PLATE if hollow else col}' stroke='{PURPLE if c in front else col if hollow else PLATE}' stroke-width='{3 if c in front else 2 if hollow else 1.5}'/>")
        right = px > W - R - 170 or c in left
        lab = f"{c} ({100 * allc[c]['pass_at_1']:.0f}%){' *' if allc[c]['cost_kind'] == 'proxy' else ''}"
        b.append(text(px - 10 if right else px + 10, py + dy.get(c, -8), lab, 11, "end" if right else "start", MUTED if hollow else INK))
    b.append(text(L, H - 10, f"Purple ring: frontier, pass@1 ≥ {100 * MIN_PASS:.0f}%, then cost and time. Hollow: exploratory. * Codex cost is proxy.", 10, fill=MUTED))
    return svg(W, H, b)


def rung_chart(s):
    cfg = s["configs"]; rungs = sorted({g for v in cfg.values() for g in v["by_rung"]}, key=lambda g: int(g[1:]))
    W, H, L, R, T, B = 760, 420, 60, 170, 50, 50
    X = lambda i: L + i / max(1, len(rungs) - 1) * (W - L - R); Y = lambda p: H - B - p * (H - T - B)
    b = [text(L, 24, "Pass rate by difficulty rung (10 attempts per rung per config)", 14, weight="600")]
    for p in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        b += [f"<line x1='{L}' x2='{W - R}' y1='{Y(p):.1f}' y2='{Y(p):.1f}' stroke='{GRID}'/>", text(L - 8, Y(p) + 4, f"{100 * p:.0f}%", 11, "end", MUTED)]
    b.append(f"<line x1='{L}' x2='{W - R}' y1='{Y(0.4):.1f}' y2='{Y(0.4):.1f}' stroke='var(--bad,#b3261e)' stroke-dasharray='4 3'/>")
    b.append(text(L + 6, Y(0.4) - 6, "breaking point (≤ 40%)", 11, fill="var(--bad,#b3261e)"))
    for i, g in enumerate(rungs):
        b.append(text(X(i), H - B + 18, g, 11, "middle", MUTED))
    b.append(text((L + W - R) / 2, H - 12, "rung (L1 easiest)", 12, "middle", MUTED))
    n = len(cfg); labels = []; seen = {}
    for k, (c, v) in enumerate(cfg.items()):
        off = (k - (n - 1) / 2) * 3  # small horizontal jitter so overlapping lines stay visible
        pts = [(X(i) + off, Y(v["by_rung"][g]["passed"] / v["by_rung"][g]["n"])) for i, g in enumerate(rungs) if g in v["by_rung"]]
        col = FAMILY(c); j = seen.get(col, 0); seen[col] = j + 1; dash = ("", " stroke-dasharray='5 3'", " stroke-dasharray='2 3'")[j % 3]
        b.append(f"<polyline points='{' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)}' fill='none' stroke='{col}' stroke-width='2'{dash}/>")
        b += [f"<circle cx='{x:.1f}' cy='{y:.1f}' r='3.5' fill='{col}'/>" for x, y in pts]
        labels.append((pts[-1][1], c))
    labels.sort(); last = -1e9
    for y, c in labels:  # spread end labels so they don't collide
        y = max(y, last + 14); last = y
        b.append(text(W - R + 6, y + 4, c, 11, fill=FAMILY(c)))
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
            k = v[c]; fill, op = ("var(--bad,#b3261e)", 0.35) if k == 0 else ("var(--good,#1c7c3c)", 0.1 + 0.09 * k)
            b.append(f"<rect x='{L + j * cw + 1}' y='{y + 1}' width='{cw - 2}' height='{ch - 2}' fill='{fill}' opacity='{op:.2f}'/>")
            b.append(text(L + j * cw + cw / 2, y + ch / 2 + 4, k, 11, "middle", INK))
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
        b += [f"<rect x='{L}' y='{y}' width='{X(tot) - L:.1f}' height='{bh}' fill='{FAMILY(c)}' opacity='0.35'/>",
              f"<rect x='{L}' y='{y}' width='{X(cached) - L:.1f}' height='{bh}' fill='{FAMILY(c)}'/>",
              text(L - 8, y + 14, c, 11, "end"), text(X(tot) + 6, y + 14, f"{tot:,}", 11, fill=MUTED)]
        y += bh + 8
    b.append(text(12, y + 22, f"Solid: cached. Pale: uncached. Codex includes ~{HOST_AGENTS_MD} host AGENTS.md tokens.", 11, fill=MUTED))
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
        if v["hidden_pass"] == v["n"]: lo = 0.05 ** (1 / len(v["by_task"]))  # bootstrap collapses at 100%; one-sided bound over tasks, as in the tables
        b.append(f"<line x1='{x:.1f}' x2='{x:.1f}' y1='{Y(lo):.1f}' y2='{Y(hi):.1f}' stroke='{FAMILY(c)}' stroke-width='2' opacity='0.5'/>")
        b.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='6' fill='{FAMILY(c)}'/>")
        right = x > W - R - 150
        b.append(text(x - 10 if right else x + 10, y - 8 if i % 2 == 0 else y + 18, anchor="end" if right else "start", s=f"{c} {v['hidden_pass']}/{v['n']}{' *' if v['cost_kind'] == 'proxy' else ''}", size=11))
    b.append(text(L, H - 10, "All configs passed 12/12. Bars: one-sided 95% lower bound. * Codex cost is proxy.", 11, fill=MUTED))
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
    return [(c, v, False) for c, v in s["configs"].items()] + [(c, v, True) for c, v in (s.get("exploratory") or {}).items()]


def cost_tokens_chart(s):
    """Total $ for the 60 function-track calls, and $ per 1,000 tokens processed (input plus output), per config."""
    rows = all_configs(s)
    tot = [(c + (" *" if v["cost_kind"] == "proxy" else ""), v["usd_total"], FAMILY(c), x) for c, v, x in rows]
    per = [(c + (" *" if v["cost_kind"] == "proxy" else ""), 1000 * v["usd_per_call"] / (v["tokens_mean"]["in_tok"] + v["tokens_mean"]["out_tok"]), FAMILY(c), x)
           for c, v, x in rows]
    a = bars("Total $ for the 60 function-track calls (L1–L6)", tot, lambda v: f"${v:.3f}", "Hollow: exploratory. * Codex cost is proxy; Claude is measured.")
    b = bars("$ per 1,000 tokens processed (input + output, mean per call)", per, lambda v: f"${v:.5f}",
                "Cached input costs less per token. * Codex cost is proxy.")
    return a, b


TOKEN_IN = ["luna-low", "luna-low-bare", "haiku-low", "sonnet-medium"]


def token_in_chart(s):
    allc = {c: v for c, v, _ in all_configs(s)}
    lab = {"luna-low": "luna-low, stock Codex", "luna-low-bare": "luna-low, stripped Codex", "haiku-low": "haiku-low, tools off", "sonnet-medium": "sonnet-medium, tools off"}
    rows = [(lab[c], allc[c]["tokens_mean"]["in_tok"], FAMILY(c), c not in s["configs"]) for c in TOKEN_IN if c in allc]
    return bars("Mean input tokens per call (function track, 60 calls each)", rows, lambda v: f"{v:,}",
                f"Includes cached input. Codex includes ~{HOST_AGENTS_MD} host AGENTS.md tokens.", L=200, R=80)


def check_design(s):
    """Chart titles and notes state the design (12 problems x 5 attempts = 60 calls per config, 10 per rung, 5 per cell). Fail if the data differ."""
    bad = [c for c, v, _ in all_configs(s) if v["n"] != 60 or any(r["n"] != 10 for r in v["by_rung"].values())]
    if bad or len(s["problems"]) != 12:
        raise SystemExit(f"chart text assumes 12 problems, 60 calls per config and 10 per rung; check {bad or 'the problem count'}")


def build(s):
    """{file name: SVG text or None} for every chart."""
    check_design(s)
    charts = {"pareto.svg": pareto_chart(s), "cost_time.svg": cost_time_chart(s), "pass_by_rung.svg": rung_chart(s), "heatmap.svg": heatmap(s),
              "token_floor.svg": floor_chart(s), "agentic.svg": agentic_chart(s), "token_in.svg": token_in_chart(s)}
    charts["cost_total.svg"], charts["cost_per_1k.svg"] = cost_tokens_chart(s)
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
