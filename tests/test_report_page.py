"""Regression checks for report geometry and attribution, using existing results only."""
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from analysis import charts, page, report

ROOT = Path(__file__).resolve().parents[1]
NS = {"s": "http://www.w3.org/2000/svg"}


@pytest.fixture(scope="module")
def summary():
    return json.loads((ROOT / "results/summary.json").read_text())


def test_speed_whiskers_fit_axis_even_with_a_slower_config(summary, monkeypatch):
    summary = json.loads(json.dumps(summary))
    summary["exploratory"]["sol61-high"]["latency_s"]["p75"] *= 2
    original = page.scatter
    seen = []

    def inspect(pts, fr, X, Y, *args, **kwargs):
        seen.extend(X(p["w"][2]) for p in pts if p["w"])
        return original(pts, fr, X, Y, *args, **kwargs)

    monkeypatch.setattr(page, "scatter", inspect)
    page.speed_cost(summary)
    assert seen and min(seen) >= 84 and max(seen) <= 544


@pytest.mark.parametrize("render", [page.pass_cost, page.speed_cost])
def test_main_ladder_repair_toggle(summary, render):
    output, frontier = render(summary)
    assert '<label class="cost-toggle"><input type="checkbox"' in output
    assert 'Codex is free (subscription quota)</label>' in output
    layers = re.findall(r'<div class="cvariant v-(normal|free)">(.*?)</ul></div>', output, re.S)
    assert [name for name, _ in layers] == ["normal", "free"]
    arms = page.rescue_arms()
    for variant, layer in layers:
        svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', layer, re.S)[0])
        points = {g.get("data-c"): g for g in svg.findall("s:g[@class='pt']", NS)}
        assert ("$0" in [t.text for t in svg.findall("s:text", NS)]) == (variant == "free")
        for builder in (*page.fast_gate.CONFIGS, "luna-low"):
            config = builder + "+haiku-on-fail"
            point = points[config]
            assert config not in frontier
            assert "rescue set, not the full ladder" in point.get("data-tip")
            v = arms[config]
            cost = v["claude_usd_per_pass"] if variant == "free" else v["usd_per_pass"]
            assert f"${cost:.5f} per pass" in point.get("data-tip")
            assert f"{v['passes']}/{v['n']} passed" in point.get("data-tip")
            assert f"median {v['median_s']:.1f} s" in point.get("data-tip")
            assert len(point) == 2  # hollow builder marker and hover target; no frontier ring
            assert point[0].tag == points[builder][-2].tag
            assert point[0].get("fill") == "var(--panel)"
            assert point[0].get("stroke") == "var(--codex)"
            assert f'data-c="{config}"' in layer[layer.index("<ul"):]
        assert "→" not in "".join(t.text or "" for t in svg.findall("s:text[@class='lbl on']", NS))
        for config in page.ORDER:
            cost = page.every(summary)[config]["usd_per_pass"]
            if variant == "free" and not config.startswith(("haiku", "sonnet")):
                cost = 0
            assert f"${cost:.5f} per pass" in points[config].get("data-tip")


def test_rung_series_have_distinct_keys_past_all_endpoints(summary):
    svg = ET.fromstring(charts.rung_chart(summary))
    series = svg.findall("s:polyline", NS)
    assert len({e.get("stroke-dasharray") for e in series}) == len(series)
    keys = [e for e in svg.findall("s:line", NS) if e.get("stroke-width") == "2"]
    assert len(keys) == len(series)
    max_end = max(float(e.get("points").split()[-1].split(",")[0]) for e in series)
    assert min(float(e.get("x1")) for e in keys) > max_end
    labels = {e.text: e for e in svg.findall("s:text", NS)}
    for c in ("astra-medium", "astra-medium-fast"):
        label = labels[page.DISP(c)]
        assert float(label.get("x")) + len(label.text) * 6.6 < 760


def test_agentic_leaders_stop_before_all_label_boxes(summary):
    svg = ET.fromstring(charts.agentic_chart(summary))
    labels = [e for e in svg.findall("s:text", NS) if re.search(r"\d+/\d+", e.text or "") and not e.text.startswith("All configs")]
    leaders = [e for e in svg.findall("s:line", NS) if e.get("class") == "leader"]
    assert len(labels) == len(leaders) == len(summary["agentic"])
    left = min(float(e.get("x")) for e in labels)
    assert all(max(float(e.get("x1")), float(e.get("x2"))) < left for e in leaders)
    ys = sorted(float(e.get("y")) for e in labels)
    assert all(b - a >= 15 for a, b in zip(ys, ys[1:]))


def test_every_toc_target_has_a_direct_toggle_heading():
    template = (ROOT / "docs/page.tmpl.md").read_text()
    targets = re.findall(r'<a href="#([^\"]+)">', template)
    assert len(targets) == 9
    for target in targets:
        assert re.search(r'<section\b[^>]*\bid="' + target + r'"[^>]*>\s*<h2\b', template)


def test_codex_orchestrator_status_requires_attributed_results():
    assert report.codex_orchestrator_status([{"cli": "codex", "passed": True}]) == "not run yet"
    assert report.codex_orchestrator_status([{"orchestrator": "Codex"}]) == "not run yet"
    assert report.codex_orchestrator_status([{"orchestrator": "Claude Opus", "passed": True}]) == "not run yet"
    for attribution in ("Codex", {"cli": "codex"}, {"model": "gpt-6.1-sol"}):
        assert report.codex_orchestrator_status([{"orchestrator": attribution, "passed": False}]) == "results available"
