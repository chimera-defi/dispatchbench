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


def test_rung_series_have_distinct_keys_above_the_plot(summary):
    svg = ET.fromstring(charts.rung_chart(summary))
    series = svg.findall("s:polyline", NS)
    assert len({e.get("stroke-dasharray") for e in series}) == len(series)
    keys = svg.findall("s:line[@class='rung-key']", NS)
    assert len(keys) == len(series)
    top = min(float(p.split(',')[1]) for e in series for p in e.get('points').split())
    assert max(float(e.get('y1')) for e in keys) < top
    labels = {e.text: e for e in svg.findall("s:text", NS)}
    for c in ("astra-medium", "astra-medium-fast"):
        label = labels[page.DISP(c)]
        assert float(label.get("x")) + len(label.text) * 6.6 < 760


def test_agentic_leaders_stop_before_all_label_boxes(summary):
    svg = ET.fromstring(charts.agentic_chart(summary))
    labels = [e for e in svg.findall("s:text", NS) if re.search(r"\d+/\d+", e.text or "") and not e.text.startswith("All configs")]
    leaders = [e for e in svg.findall("s:line", NS) if e.get("class") == "leader"]
    assert len(labels) == len(leaders) == len(summary["agentic"])
    # Stubs leave each dot vertically, never along the shared 100% data line.
    assert all(e.get("x1") == e.get("x2") for e in leaders)
    assert all(abs(float(e.get("y1")) - float(e.get("y2"))) > 5 for e in leaders)
    boxes = []
    for e in labels:
        x, y = float(e.get("x")), float(e.get("y"))
        w = len(e.text) * 6.6
        left = x - (w if e.get("text-anchor") == "end" else w / 2 if e.get("text-anchor") == "middle" else 0)
        box = (left, y - 12, left + w, y + 3)
        assert all(box[2] <= q[0] or q[2] <= box[0] or box[3] <= q[1] or q[3] <= box[1] for q in boxes)
        boxes.append(box)


def test_every_toc_target_has_a_direct_toggle_heading():
    template = (ROOT / "docs/page.tmpl.md").read_text()
    targets = re.findall(r'<a href="#([^\"]+)">', template)
    assert len(targets) == 10
    for target in targets:
        assert re.search(r'<section\b[^>]*\bid="' + target + r'"[^>]*>\s*<h2\b', template)


def test_codex_orchestrator_status_requires_attributed_results():
    assert report.codex_orchestrator_status([{"cli": "codex", "passed": True}]) == "not run yet"
    assert report.codex_orchestrator_status([{"orchestrator": "Codex"}]) == "not run yet"
    assert report.codex_orchestrator_status([{"orchestrator": "Claude Opus", "passed": True}]) == "not run yet"
    for attribution in ("Codex", {"cli": "codex"}, {"model": "gpt-6.1-sol"}):
        assert report.codex_orchestrator_status([{"orchestrator": attribution, "passed": False}]) == "results available"


def test_speed_frontier_treats_sub_half_second_gap_as_tie(summary):
    _, names = page.speed_cost(summary)
    assert 'haiku-low' in names
    assert 'astra-medium-fast' not in names
    changed = json.loads(json.dumps(summary))
    changed['exploratory']['astra-medium-fast']['latency_s']['median'] = 9.0
    assert 'astra-medium-fast' in page.speed_cost(changed)[1]


def test_rescue_triangle_labels_lead_to_their_own_points():
    for render in (page.hard_pass_cost, page.hard_speed_cost):
        svg = ET.fromstring(render()[0].split('<div class="cplot">')[1].split('</div>')[0])
        labels = [e.text for e in svg.findall('s:text', NS)]
        assert 'luna-high-bare→retry' in labels
        assert 'luna-low→H fail' in labels
        assert svg.findall("s:line[@class='label-leader']", NS)


def test_rung_points_explain_per_problem_passes(summary):
    svg = ET.fromstring(charts.rung_chart(summary))
    titles = [e.text for e in svg.findall('.//s:title', NS)]
    assert any('haiku-low' in t and 'p11' in t and '/5' in t for t in titles)
    labels = [e for e in svg.findall('s:text', NS) if e.get('class') == 'dip-label']
    assert labels
    assert len({e.tag for e in svg.findall('.//*[@class="rung-marker"]')}) >= 3


def test_marker_styles_distinguish_fast_generation_and_luna_variants():
    def draw(c):
        return page.config_marker(c, 0, 0)
    assert 'var(--panel)' in draw('sol61-high-fast')
    assert draw('sol61-high') != draw('sol56-high')
    assert len({draw(c) for c in ('luna-low', 'luna-medium', 'luna-high', 'luna-low-bare', 'luna56-low')}) == 5


def test_floor_charts_fit_mobile_viewport(summary):
    for body in (page.floor(summary), page.fast(summary), page.pipes()):
        assert 'class="svgscroll"' in body
        assert '--natural-width' not in body
        assert 'viewBox="0 0 360 ' in body
        assert 'Scroll sideways' in body


def test_quality_fast_coverage_keeps_main_and_separate_rescue_runs_apart(summary, monkeypatch):
    note = report.quality_fast_note(summary)
    assert 'sol61-high ⚡: main-ladder solutions not scored' in note
    assert '35-attempt rescue run' in note
    assert 'astra-medium ⚡: main-ladder solutions not scored' in note
    assert 'No separate rescue-run quality scores' in note
    scored = next(r for r in report.quality_rows() if r['config'] == 'sol61-high-fast' and r['outcome'] == 'pass')
    main = dict(scored, phase='exploratory')
    monkeypatch.setattr(report, 'quality_rows', lambda: [scored, main])
    table = report.quality_table({'configs': {}, 'exploratory': {'sol61-high-fast': {'passes': 1}}})
    assert 'sol61-high ⚡ † | 1 |' in table


def test_rescue_label_leaders_start_at_the_named_point():
    for render in (page.hard_pass_cost, page.hard_speed_cost):
        svg = ET.fromstring(render()[0].split('<div class="cplot">')[1].split('</div>')[0])
        points = {g.get('data-c'): g.findall('s:circle', NS)[-1] for g in svg.findall("s:g[@class='pt']", NS)}
        for lead in svg.findall("s:line[@class='label-leader']", NS):
            circle = points[lead.get('data-c')]
            dx = float(lead.get('x1')) - float(circle.get('cx'))
            dy = float(lead.get('y1')) - float(circle.get('cy'))
            assert (dx * dx + dy * dy) ** .5 == pytest.approx(8, abs=.15)



def test_every_results_config_appears_once_in_inventory():
    from analysis.summarize import load
    body = page.everything_tried()
    configs = {r["config"] for path in (ROOT / "results").rglob("*.jsonl")
               for r in load(path) if "config" in r}
    configs.update('pilot-repo-' + r['pipeline'] for r in load(ROOT / 'results/2026-10-22-pilot-agentic.jsonl'))
    ids = re.findall(r'<tr data-config="([^"]+)"', body)
    assert set(ids) == configs
    assert len(ids) == len(set(ids))
    for category in ("Main ladder", "L7", "Rescue / pipelines", "Pilot", "Trim probes",
                     "Harness bias / appendix arms", "Repo tasks", "Fast mode / priority variants"):
        assert category in body
    # This is the table actually inserted at the end of Results.
    template = (ROOT / "docs/page.tmpl.md").read_text()
    assert "{{w_everything}}" in template.split('id="results"')[1].split('</section>')[0]


def test_winner_and_conclusion_agree_and_sets_are_collapsed(summary):
    template = (ROOT / "docs/page.tmpl.md").read_text()
    verdict = "Use sol61-high when Codex has quota. Use haiku-low when it does not; use haiku-high when a miss would be costly or you need speed."
    assert template.count(verdict) == 2
    assert '<details class="sets"><summary>' in page.sets_box(summary)
    assert ' open' not in page.sets_box(summary).split('>')[0]
    assert template.index('{{w_sets}}') > template.index('{{w_pass_cost}}')
    assert page.method(summary)[0].count('L7 has') == 1
    assert 'L7 has' not in page.sets_box(summary)
    problems = page.method(summary)[0]
    assert 'p01 overlap_minutes (L1)' in problems
    first = problems.split('<li class="prow">', 1)[1].split('</li>', 1)[0]
    assert first.index('p01 overlap_minutes (L1)') < first.index('class="lc medium"')


def test_winner_verdict_and_luna_high_tradeoff(summary):
    E = page.every(summary)
    assert page.verdict('haiku-high', E['haiku-high'], report.need, E) == '★ pick: 0 misses, cheapest'
    assert page.verdict('luna-high', E['luna-high'], report.need, E) == 'trade-off: costs more than luna-low, passes more'


def test_rung_dip_labels_clear_series_and_breaking_line(summary):
    svg = ET.fromstring(charts.rung_chart(summary))
    segments = []
    for series in svg.findall('s:polyline', NS):
        points = [tuple(map(float, pair.split(','))) for pair in series.get('points').split()]
        segments.extend(zip(points, points[1:]))
    for line in svg.findall('s:line', NS):
        if line.get('stroke') == 'var(--bad,#b3261e)':
            segments.append(((float(line.get('x1')), float(line.get('y1'))),
                             (float(line.get('x2')), float(line.get('y2')))))
    for label in svg.findall('s:text[@class="dip-label"]', NS):
        x, y = float(label.get('x')), float(label.get('y'))
        width = len(label.text) * 6.6  # 11px monospace text
        left = x - (width if label.get('text-anchor') == 'end' else width / 2 if label.get('text-anchor') == 'middle' else 0)
        for (ax, ay), (bx, by) in segments:
            assert not any(left < ax + (bx - ax) * k / 200 < left + width and
                           y - 11 < ay + (by - ay) * k / 200 < y + 2 for k in range(201)), label.text


def test_inventory_keeps_sets_separate_and_deduplicates_cached_trials(summary):
    from analysis.configs import registry
    inventory = registry()
    for c, expected in page.every(summary).items():
        parts = {m['context']: m for m in inventory[c]['measurements']}
        main = parts['main ladder']
        assert (main['attempts'], main['passed']) == (expected['n'], expected['passes'])
        assert main['usd_per_pass'] == pytest.approx(expected['usd_per_pass'], abs=1e-6)
        if c in summary['hard']:
            hard = summary['hard'][c]
            assert (parts['L7']['attempts'], parts['L7']['passed']) == (hard['n'], hard['passes'])
        if c in summary['agentic']:
            ag = summary['agentic'][c]
            assert (parts['repo tasks']['attempts'], parts['repo tasks']['passed']) == (ag['n'], ag['hidden_pass'])
