"""Regression checks for report geometry and attribution, using existing results only."""
import json
import re
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from analysis import charts, harness_bias, page, report

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


def test_fairness_qa_renders_counts_and_runtime_from_appendix():
    rows = [json.loads(line) for line in (ROOT / 'results/appendix/harness_bias.jsonl').read_text().splitlines()]
    rendered = report.render()[2]
    method = re.search(r'<section\b[^>]*\bid="method"[^>]*>(.*?)</section>', rendered, re.S).group(1)
    assert "Q: Does Claude's harness make Codex look bad?" in method
    assert 'the program that sends the problem to the model and grades the answer' in method
    assert 'one-shot' in method and 'tool loop' in method
    assert 'not just in who built them' in method
    assert 'A separate run with Codex managing the benchmark' not in method
    assert f"{len({r['problem'] for r in rows})} hard problems × {len({r['repeat'] for r in rows})} repeats" in method
    for config in ('luna-low', 'haiku-low'):
        counts = []
        for harness in ('claude-one-shot', 'codex-tool-loop'):
            cell = [r for r in rows if (r['config'], r['harness']) == (config, harness)]
            counts.append(f"{sum(r['passed'] for r in cell)}/{len(cell)}")
        assert f"<td>{config}</td><td>{counts[0]}</td><td>{counts[1]}</td>" in method
    codex = [r for r in rows if r['harness'] == 'codex-tool-loop']
    start = min(datetime.fromisoformat(r['ts']).timestamp() for r in codex)
    end = max(datetime.fromisoformat(r['ts']).timestamp() + r['wall_s'] for r in codex)
    assert f"{sum(r['outcome'] == 'harness_error' for r in codex)} harness errors" in method
    assert f"about {(end - start) / 60:.0f} minutes of wall time for the recorded calls" in method
    assert 'no timeouts' in method
    comparison = harness_bias.pass_summary(rows)
    lo, hi = comparison['ci']
    assert 'Slightly, but below the 0.15' in method and 'we do not call it bias' in method
    assert f'{lo:+.3f} to {hi:+.3f}' in method


def test_fairness_qa_updates_when_appendix_data_change(monkeypatch):
    original = report.load
    rows = original(str(ROOT / 'results/appendix/harness_bias.jsonl'))
    changed = [dict(r, passed=False) if r['config'] == 'luna-low' else r for r in rows]
    monkeypatch.setattr(report, 'load', lambda path: changed if str(path).endswith('/appendix/harness_bias.jsonl') else original(path))
    rendered = report.render()[2]
    n = sum(r['config'] == 'luna-low' and r['harness'] == 'claude-one-shot' for r in changed)
    passes = sum(r['passed'] for r in changed if r['config'] == 'luna-low')
    assert f'<td>luna-low</td><td>{passes}/{n}</td><td>{passes}/{n}</td>' in rendered
    lo, hi = harness_bias.pass_summary(changed)['ci']
    assert f'No bias of about {max(abs(lo), abs(hi)):.1f} or more was detectable' in rendered
    assert f'{lo:+.3f} to {hi:+.3f}' in rendered


@pytest.mark.parametrize('change', ['bias', 'timeout', 'missing'])
def test_fairness_qa_rejects_data_that_invalidate_its_claims(monkeypatch, change):
    rows = report.load(str(ROOT / 'results/appendix/harness_bias.jsonl'))
    if change == 'bias':
        rows = [dict(r, passed=r['harness'] == 'codex-tool-loop') if r['config'] == 'luna-low'
                else dict(r, passed=True) for r in rows]
    elif change == 'timeout':
        next(r for r in rows if r['harness'] == 'codex-tool-loop')['outcome'] = 'timeout'
    else:
        rows.pop()
    monkeypatch.setattr(report, 'load', lambda path: rows)
    with pytest.raises(AssertionError, match='template wording no longer matches the data'):
        report.fairness_facts()


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


def test_floor_charts_keep_natural_size(summary):
    for body in (page.floor(summary), page.fast(summary), page.pipes()):
        assert 'class="svgscroll"' in body
        assert '--natural-width:760px' in body
        assert 'Scroll sideways' in body


def test_quality_fast_coverage_keeps_main_and_separate_rescue_runs_apart(summary, monkeypatch):
    note = report.quality_fast_note(summary)
    assert 'sol61-high-fast: main-ladder solutions not scored' in note
    assert '35-attempt rescue run' in note
    assert 'astra-medium-fast: main-ladder solutions not scored' in note
    assert 'No separate rescue-run quality scores' in note
    scored = next(r for r in report.quality_rows() if r['config'] == 'sol61-high-fast' and r['outcome'] == 'pass')
    main = dict(scored, phase='exploratory')
    monkeypatch.setattr(report, 'quality_rows', lambda: [scored, main])
    table = report.quality_table({'configs': {}, 'exploratory': {'sol61-high-fast': {'passes': 1}}})
    assert 'sol61-high ⚡ | 1 |' in table


def test_rescue_label_leaders_start_at_the_named_point():
    for render in (page.hard_pass_cost, page.hard_speed_cost):
        svg = ET.fromstring(render()[0].split('<div class="cplot">')[1].split('</div>')[0])
        points = {g.get('data-c'): g.findall('s:circle', NS)[-1] for g in svg.findall("s:g[@class='pt']", NS)}
        for lead in svg.findall("s:line[@class='label-leader']", NS):
            circle = points[lead.get('data-c')]
            dx = float(lead.get('x1')) - float(circle.get('cx'))
            dy = float(lead.get('y1')) - float(circle.get('cy'))
            assert (dx * dx + dy * dy) ** .5 == pytest.approx(8, abs=.15)
