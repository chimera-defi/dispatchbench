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
