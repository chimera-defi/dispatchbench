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


@pytest.mark.parametrize("value,expected", [
    (0, "$0"), (0.000890, "$0.000890"), (0.0011234, "$0.00112"),
    (0.012399, "$0.0124"), (0.00000001234, "$0.0000000123"),
    (0.9999, "$1.00"), (12.345, "$12.3"), (999.9, "$1000"),
])
def test_chart_cost_formatter(value, expected):
    assert page.format_cost(value) == expected


@pytest.mark.parametrize("render,stat", [(page.pass_cost, "pass"), (page.speed_cost, "speed")])
@pytest.mark.parametrize("problem_set", ["main", "rescue"])
def test_chart_free_strip_and_set_attribution(summary, render, stat, problem_set):
    normal, _ = render(summary, free=False, problem_set=problem_set)
    output, frontier = render(summary, free=True, problem_set=problem_set)
    svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', output, re.S)[0])
    points = {g.get("data-c"): g for g in svg.findall("s:g[@class='pt']", NS)}
    strip = re.search(r'<ol class="free-strip"[^>]*>(.*?)</ol>', output, re.S)[1]
    configs = re.findall(r'<li[^>]*data-c="([^"]+)"', strip)
    if problem_set == "main":
        values = page.every(summary)
        expected = [c for c in page.ORDER if not c.startswith(("haiku", "sonnet"))]
        rank = lambda c: values[c]["latency_s"]["median"] if stat == "speed" else -values[c]["pass_at_1"]
        assert set(points) | set(configs) == set(page.ORDER)
    else:
        values = page.rescue_arms()
        expected = [c for c, v in values.items() if v["claude_usd_per_pass"] == 0]
        rank = lambda c: values[c]["median_s"] if stat == "speed" else -values[c]["passes"] / values[c]["n"]
        assert set(points) | set(configs) == set(values)
        assert "[rescue set]" not in strip
    assert set(configs) == set(expected)
    assert [rank(c) for c in configs] == sorted(rank(c) for c in configs)
    assert set(points).isdisjoint(configs)
    assert set(frontier).isdisjoint(configs)
    assert "Free with Codex quota:" in output
    assert 'cost-drop' not in output
    assert "$0" not in [t.text for t in svg.findall("s:text", NS)]
    assert "$0.00000" not in output
    assert "log" in output
    for point in points.values():
        assert point.get("data-set") == problem_set
        assert ("rescue set" if problem_set == "rescue" else "main ladder") in point.get("data-tip")
    # The strip preserves the exact marker used for the same config in paid mode.
    normal_svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', normal, re.S)[0])
    normal_points = {g.get("data-c"): g for g in normal_svg.findall("s:g[@class='pt']", NS)}
    for c in configs:
        item = re.search(r'<li[^>]*data-c="' + re.escape(c) + r'".*?</li>', strip, re.S)[0]
        icon = ET.fromstring(re.search(r'<svg\b.*?</svg>', item, re.S)[0])[0]
        original = normal_points[c][-2]
        assert (icon.tag, icon.get("fill"), icon.get("stroke")) == (original.tag, original.get("fill"), original.get("stroke"))
        assert "saved" in item


@pytest.mark.parametrize("render", [page.pass_cost, page.speed_cost])
def test_chart_set_toggle_and_grouped_keys(summary, render):
    output, _ = render(summary)
    assert 'Codex is free (subscription quota)</label>' in output
    assert 'Main ladder' in output and '> Rescue set</label>' in output
    for cat in ("main", "fast", "pipelines", "exploratory"):
        assert f'data-cat="{cat}" checked' in output
        groups = re.findall(r'<details class="key-group" data-cat="' + cat + r'"([^>]*)>(.*?)</details>', output, re.S)
        assert len(groups) == (2 if cat == "pipelines" else 4)
        for attrs, body in groups:
            assert ("open" in attrs) == (cat == "main")
            assert "<summary>" in body
            assert "(0)" not in body
    pipeline_chip = re.search(r'<label[^>]*><input[^>]*data-cat="pipelines"[^>]*> pipelines</label>', output)[0]
    assert "disabled" in pipeline_chip
    assert 'title="only on the rescue set"' in pipeline_chip
    assert output.count('class="cset s-main"') == 1
    assert output.count('class="cset s-rescue"') == 1


@pytest.mark.parametrize("render,stat", [(page.pass_cost, "pass"), (page.speed_cost, "speed")])
@pytest.mark.parametrize("problem_set", ["main", "rescue"])
@pytest.mark.parametrize("free", [False, True])
def test_chart_costs_and_tooltips_share_precision(summary, render, stat, problem_set, free):
    output, _ = render(summary, free=free, problem_set=problem_set)
    points = page.ladder_points(summary, free, stat, problem_set)
    for p in points:
        cost = p["y"] if stat == "speed" else p["x"]
        assert f'{page.format_cost(cost)} per pass' in p["tip"]
        assert page.format_cost(p["normal_usd"]) in p["tip"]
        assert page.format_cost(p["free_usd"]) in p["tip"]
        assert page.format_cost(cost) in page.point_values(p, stat)
        if free and p["normal_usd"] != p["free_usd"]:
            assert f'saved {page.format_cost(p["normal_usd"] - p["free_usd"])}' in page.point_values(p, stat)
    # Tick labels use exact, compact amounts; key and tooltip values keep 3 sig figs.
    without_plot = re.sub(r'<svg\b.*?</svg>', '', output, flags=re.S)
    for value in re.findall(r'\$\d+(?:\.\d+)?', without_plot):
        assert value == page.format_cost(float(value[1:]))


@pytest.mark.parametrize("render", [page.pass_cost, page.speed_cost])
@pytest.mark.parametrize("problem_set", ["main", "rescue"])
@pytest.mark.parametrize("free", [False, True])
def test_scatter_ticks_are_compact_and_mobile_endpoint_fits(summary, render, problem_set, free):
    output, _ = render(summary, free=free, problem_set=problem_set)
    svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', output, re.S)[0])
    costs = [t.text for t in svg.findall("s:text", NS) if (t.text or "").startswith("$0.")]
    expected = ["$0.001", "$0.003", "$0.01", "$0.03", "$0.1", "$0.3"]
    if free and problem_set == "rescue":
        expected.insert(0, "$0.0003")
    assert costs == expected
    ticks = [t for t in svg.findall("s:text", NS) if "x-tick" in t.get("class", "").split()]
    assert ticks
    assert ticks[-1].get("text-anchor") == "end"
    assert float(ticks[-1].get("x")) <= 544
    mobile_ticks = [t for t in ticks if "tick-skip" not in t.get("class", "").split()]
    assert mobile_ticks == ticks[::-2][::-1]


@pytest.mark.parametrize("render", [page.pass_cost, page.speed_cost])
@pytest.mark.parametrize("free", [False, True])
def test_rescue_labels_and_markers_are_clean(summary, render, free):
    output, _ = render(summary, free=free, problem_set="rescue")
    assert "[rescue set]" not in output
    svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', output, re.S)[0])
    for point in svg.findall("s:g[@class='pt']", NS):
        marker = point[-2]
        assert marker.get("stroke-dasharray") is None
        if point.get("data-cat") != "pipelines":
            assert marker.get("fill") == marker.get("stroke")


def test_frontier_caption_uses_computed_costs(summary):
    values = page.every(summary)
    medium, low = values["luna-medium"], values["luna-low"]
    caption = page.frontier_caption(summary)
    assert (f'luna-low is off the frontier: luna-medium costs about the same '
            f'({page.format_cost(medium["usd_per_pass"])} vs {page.format_cost(low["usd_per_pass"])}) '
            f'and passes more ({medium["passes"]}/{medium["n"]} vs {low["passes"]}/{low["n"]}).') in caption
    assert 'shown precision' not in caption


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
