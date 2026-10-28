"""Label bounding boxes in the generated pareto charts: no two text labels may overlap."""
import re
from pathlib import Path
from html import unescape

ROOT = Path(__file__).resolve().parents[1]
CHAR_W, HEIGHT = 6.0, 11


def boxes(svg, min_size=10, max_size=12):
    out = []
    for m in re.finditer(r"<text x='([\d.-]+)' y='([\d.-]+)' font-size='(\d+)' text-anchor='(\w+)'[^>]*>([^<]*)</text>", svg):
        x, y, size, anchor, txt = float(m[1]), float(m[2]), int(m[3]), m[4], unescape(m[5])
        if "rotate(" in m[0] or not (min_size <= size <= max_size) or "(" not in txt or "%" not in txt: continue
        w = len(txt) * CHAR_W * size / 11
        left = x - w if anchor == "end" else x - w / 2 if anchor == "middle" else x
        out.append((txt, left, y - size, left + w, y + 3))
    return out


def overlaps(bs):
    return [(a[0], b[0]) for i, a in enumerate(bs) for b in bs[i + 1:]
            if a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]]


def test_static_pareto_labels_do_not_overlap():
    svg = (ROOT / "results/report/charts/pareto.svg").read_text()
    bs = boxes(svg)
    assert len(bs) >= 10
    assert overlaps(bs) == []


def test_overlap_detector_catches_a_pileup():
    svg = "<text x='10.0' y='20.0' font-size='11' text-anchor='start' style='fill:x' font-weight='normal'>aaaa (100%)</text>" * 2
    assert overlaps(boxes(svg))


def test_interactive_scatter_labels_do_not_overlap_per_chart():
    """Every interactive scatter in page.html: label boxes (x, y, len * char width) within one svg and one category view."""
    html = (ROOT / "results/report/page.html").read_text()
    bad, seen = [], 0
    for svg in re.findall(r"<svg.*?</svg>", html, re.S):
        labs = re.findall(r'<text x="([\d.-]+)" y="([\d.-]+)" text-anchor="(\w+)" class="lbl[^"]*" data-cat="(\w+)" data-set="(\w+)">([^<]*)</text>', svg)
        if not labs: continue
        seen += 1
        bs = []
        for x, y, a, cat, st, txt in labs:
            w = len(unescape(txt)) * 5.5  # the 11px chart label face; the placer reserves 11px per char
            left = float(x) - w if a == "end" else float(x) - w / 2 if a == "middle" else float(x)
            bs.append((f"{cat}:{unescape(txt)}", left, float(y) - 11, left + w, float(y) + 3))
        bad += overlaps(bs)
    assert seen >= 4
    assert bad == []
