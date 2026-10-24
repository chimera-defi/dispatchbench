"""Regression checks for report geometry and attribution, using existing results only."""
import json
import re
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from analysis import charts, configs, dataset, harness_bias, page, report

ROOT = Path(__file__).resolve().parents[1]
NS = {"s": "http://www.w3.org/2000/svg"}


def test_reader_set_labels_and_complete_notation_legend():
    from html import unescape
    from html.parser import HTMLParser

    class Reader(HTMLParser):
        def __init__(self):
            super().__init__()
            self.hidden = 0
            self.text = []
            self.titles = []
            self.section = None
            self.uses = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == "section":
                self.section = attrs.get("id")
            if tag in ("script", "style"):
                self.hidden += 1
            self.titles.extend(v for k, v in attrs.items() if k in ("title", "aria-label", "data-tip"))
            if "data-notation" in attrs:
                self.uses.append((self.section, attrs["data-notation"], attrs["title"]))

        def handle_endtag(self, tag):
            if tag in ("script", "style"):
                self.hidden -= 1

        def handle_data(self, data):
            if not self.hidden:
                self.text.append(data)

    output = report.render()[2]
    reader = Reader()
    reader.feed(output)
    assert not re.search(r"rescue[ -]set", "".join(reader.text + reader.titles), re.I)
    assert output.count('<details class="legend" id="notation">') == 1
    legend = output.split('<details class="legend" id="notation">', 1)[1].split('</details>', 1)[0]
    listed = [unescape(s) for s in re.findall(r'<dt>(.*?)</dt>', legend)]
    assert listed == list(configs.NOTATION)
    ds = dataset.read()
    meanings = page.notation_meanings(ds)
    for meaning in meanings.values():
        assert meaning in unescape(re.sub(r'<[^>]+>', '', legend))
    assert reader.uses
    assert {'purple dot', 'family dots'} <= {symbol for _, symbol, _ in reader.uses}
    assert len(reader.uses) == len({(section, symbol) for section, symbol, _ in reader.uses})
    assert all(title == meanings[symbol] for _, symbol, title in reader.uses)
    assert {section for section, _, _ in reader.uses} == set(re.findall(r'<section[^>]*id="([^"]+)"', output))
    assert {(r['source'], r['config']) for r in dataset.catalog_rows(ds) if r['category'] == 'low context'} == configs.LOW_CONTEXT


@pytest.fixture(scope="module")
def summary():
    return dataset.view(dataset.read())


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
        assert "[luna-miss set]" not in strip
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
        assert ("luna-miss set" if problem_set == "rescue" else "main ladder") in point.get("data-tip").lower()
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
    assert 'Main ladder' in output and '> Luna-miss set</label>' in output
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
    assert 'title="only on the luna-miss set"' in pipeline_chip
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
        assert f'{dataset.usd(cost)} per pass' in p["tip"]
        assert dataset.usd(p["normal_usd"]) in p["tip"]
        assert dataset.usd(p["free_usd"]) in p["tip"]
        assert dataset.usd(cost) in page.point_values(p, stat)
        if free and p["normal_usd"] != p["free_usd"]:
            assert f'saved {dataset.usd(p["saved_usd"])}' in page.point_values(p, stat)
    # Every displayed dollar value uses the dataset formatter.
    without_plot = re.sub(r'<svg\b.*?</svg>', '', output, flags=re.S)
    for value in re.findall(r'\$\d+(?:\.\d+)?', without_plot):
        assert value == dataset.usd(float(value[1:]))


@pytest.mark.parametrize("render", [page.pass_cost, page.speed_cost])
@pytest.mark.parametrize("problem_set", ["main", "rescue"])
@pytest.mark.parametrize("free", [False, True])
def test_scatter_ticks_use_dataset_usd_and_mobile_endpoint_fits(summary, render, problem_set, free):
    output, _ = render(summary, free=free, problem_set=problem_set)
    svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', output, re.S)[0])
    costs = [t.text for t in svg.findall("s:text", NS) if (t.text or "").startswith("$0.")]
    expected = [dataset.usd(v) for v in (0.001, 0.003, 0.01, 0.03, 0.1, 0.3)]
    if free and problem_set == "rescue":
        expected.insert(0, dataset.usd(0.0003))
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
    assert "[luna-miss set]" not in output
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
            f'({dataset.usd(medium["usd_per_pass"], sig=3)} vs {dataset.usd(low["usd_per_pass"], sig=3)}) '
            f'and passes more ({medium["passes"]}/{medium["n"]} vs {low["passes"]}/{low["n"]}).') in caption
    assert 'shown precision' not in caption
    assert '($0.00089 vs $0.000899)' in caption


def test_measured_luna_rescue_keeps_its_own_page_metrics(summary):
    arm = page.rescue_arms(summary)["luna-low+haiku-on-fail"]
    assert (arm["passes"], arm["n"]) == (34, 35)
    assert (arm["usd_per_pass"], arm["claude_usd_per_pass"], arm["median_s"]) == (.002161, .001335, 7.88)
    assert arm["derived"] is False
    assert arm["metrics_from"] == {"source": "rescue", "config": "luna-low+haiku-on-fail", "set": "rescue arms"}
    for render in (page.pass_cost, page.speed_cost):
        output, _ = render(summary, free=False, problem_set="rescue")
        points = ET.fromstring(re.search(r'<svg\b.*?</svg>', output, re.S)[0])
        point = next(p for p in points.findall("s:g", NS) if p.get("data-c") == "luna-low+haiku-on-fail")
        assert '34/35 passed' in point.get("data-tip")


def test_rung_series_have_distinct_keys_past_all_endpoints(summary):
    svg = ET.fromstring(charts.rung_chart(summary))
    words = {e.text for e in svg.findall("s:text", NS)}
    ex = summary.get("exploratory") or {}
    shown = list(summary["configs"]) + [c for c in ("sol61-high", "sol61-high-fast", "astra-medium", "astra-medium-fast") if c in ex]
    assert {page.DISP(c) for c in shown} <= words
    assert {g for c in summary["configs"].values() for g in c["by_rung"]} <= words


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
    toc = re.search(r'<nav class="toc"[^>]*>(.*?)</nav>', template, re.S)[1]
    targets = re.findall(r'<a href="#([^\"]+)">', toc)
    assert len(targets) == 10
    for target in targets:
        assert re.search(r'<section\b[^>]*\bid="' + target + r'"[^>]*>\s*<h2\b', template)


def test_codex_orchestrator_status_requires_attributed_results():
    assert dataset.codex_orchestrator_status([{"cli": "codex", "passed": True}]) == "not run yet"
    assert dataset.codex_orchestrator_status([{"orchestrator": "Codex"}]) == "not run yet"
    assert dataset.codex_orchestrator_status([{"orchestrator": "Claude Opus", "passed": True}]) == "not run yet"
    for attribution in ("Codex", {"cli": "codex"}, {"model": "gpt-6.1-sol"}):
        assert dataset.codex_orchestrator_status([{"orchestrator": attribution, "passed": False}]) == "results available"


def test_fairness_qa_renders_counts_and_runtime_from_appendix():
    rows = [json.loads(line) for line in (ROOT / 'results/appendix/harness_bias.jsonl').read_text().splitlines()]
    rendered = report.render()[2]
    method = re.search(r'<section\b[^>]*\bid="method"[^>]*>(.*?)</section>', rendered, re.S).group(1)
    assert "Q: Does our one-shot runner make Codex look bad?" in method
    assert '<th>our one-shot runner</th>' in method
    assert '<th>vendor agent CLI (runs code, retries)</th>' in method
    appendix = re.search(r'<details id="appendix">(.*?)</details>', rendered, re.S).group(1)
    assert 'the program that sends the problem to the model and grades the answer' in method
    assert 'one-shot' in method and 'tool loop' in appendix
    assert 'not just in who built them' in appendix
    assert 'A separate run with Codex managing the benchmark' not in method
    assert f"{len({r['problem'] for r in rows})} hard problems × {len({r['repeat'] for r in rows})} repeats" in appendix
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
    assert f"about {(end - start) / 60:.0f} minutes of wall time for the recorded calls" in appendix
    assert 'no timeouts' in method
    comparison = harness_bias.pass_summary(rows)
    lo, hi = comparison['ci']
    assert 'The estimated tilt is below our 0.15 bias threshold.' in method and 'we do not call it bias' in method
    assert f'{lo:+.3f} to {hi:+.3f}' in appendix
    assert 'It also permits bias above our threshold.' in appendix


def test_fairness_qa_updates_when_appendix_data_change(monkeypatch):
    original = dataset.load
    rows = original(str(ROOT / 'results/appendix/harness_bias.jsonl'))
    changed = [dict(r, passed=False) if r['config'] == 'luna-low' else r for r in rows]
    monkeypatch.setattr(dataset, 'load', lambda path: changed if str(path).endswith('/appendix/harness_bias.jsonl') else original(path))
    updated = dataset.read()
    updated["facts"].update(dataset.fairness_facts())
    monkeypatch.setattr(dataset, "read", lambda: updated)
    rendered = report.render()[2]
    n = sum(r['config'] == 'luna-low' and r['harness'] == 'claude-one-shot' for r in changed)
    passes = sum(r['passed'] for r in changed if r['config'] == 'luna-low')
    assert f'<td>luna-low</td><td>{passes}/{n}</td><td>{passes}/{n}</td>' in rendered
    lo, hi = harness_bias.pass_summary(changed)['ci']
    assert f'No bias of about {max(abs(lo), abs(hi)):.1f} or more was detectable' in rendered
    assert f'{lo:+.3f} to {hi:+.3f}' in rendered


@pytest.mark.parametrize('change', ['bias', 'timeout', 'missing'])
def test_fairness_qa_rejects_data_that_invalidate_its_claims(monkeypatch, change):
    rows = dataset.load(str(ROOT / 'results/appendix/harness_bias.jsonl'))
    if change == 'bias':
        rows = [dict(r, passed=r['harness'] == 'codex-tool-loop') if r['config'] == 'luna-low'
                else dict(r, passed=True) for r in rows]
    elif change == 'timeout':
        next(r for r in rows if r['harness'] == 'codex-tool-loop')['outcome'] = 'timeout'
    else:
        rows.pop()
    monkeypatch.setattr(dataset, 'load', lambda path: rows)
    with pytest.raises(AssertionError, match='template wording no longer matches the data'):
        dataset.fairness_facts()


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
    note = dataset.read()["facts"]["quality_fast_note"]
    assert 'sol61-high ⚡: main-ladder solutions not scored' in note
    assert f'{dataset.read()["rescue"]["sol61-high"]["n"]}-attempt luna-miss run' in note
    assert 'astra-medium ⚡: main-ladder solutions not scored' in note
    assert 'No separate luna-miss-run quality scores' in note
    scored = next(r for r in dataset.quality_rows() if r['config'] == 'sol61-high-fast' and r['outcome'] == 'pass')
    main = dict(scored, phase='exploratory')
    monkeypatch.setattr(dataset, 'quality_rows', lambda: [scored, main])
    table = dataset.quality_table({'configs': {}, 'exploratory': {'sol61-high-fast': {'passes': 1}}})
    assert table['rows'][0][:2] == ['sol61-high ⚡ †', '1']


def test_rescue_label_leaders_start_at_the_named_point():
    for render in (page.hard_pass_cost, page.hard_speed_cost):
        svg = ET.fromstring(render()[0].split('<div class="cplot">')[1].split('</div>')[0])
        points = {g.get('data-c'): g.findall('s:circle', NS)[-1] for g in svg.findall("s:g[@class='pt']", NS)}
        for lead in svg.findall("s:line[@class='label-leader']", NS):
            circle = points[lead.get('data-c')]
            dx = float(lead.get('x1')) - float(circle.get('cx'))
            dy = float(lead.get('y1')) - float(circle.get('cy'))
            assert (dx * dx + dy * dy) ** .5 == pytest.approx(8, abs=.15)



def test_winner_and_conclusion_agree_and_sets_are_collapsed(summary):
    template = (ROOT / "docs/page.tmpl.md").read_text()
    verdict = "Use sol61-high when Codex has quota. Use haiku-low when it does not; use haiku-high when a miss would be costly or you need speed."
    assert template.count(verdict) == 2
    assert '<details class="sets"><summary>' in page.sets_box(summary)
    assert ' open' not in page.sets_box(summary).split('>')[0]
    assert template.index('{{w_sets}}') > template.index('{{w_pass_cost}}')
    assert page.method(summary)[0].count('We added L7 to find a breaking point.') == 1
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
