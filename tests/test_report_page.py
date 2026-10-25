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
    assert {'✓ pick', '→H fail', '⚡'} <= {symbol for _, symbol, _ in reader.uses}
    assert len(configs.NOTATION) <= 14
    assert 'retry' not in configs.NOTATION and '★' not in configs.NOTATION
    assert len(reader.uses) == len({(section, symbol) for section, symbol, _ in reader.uses})
    assert all(title == meanings[symbol] for _, symbol, title in reader.uses)
    assert {"winner", "results", "pipes"} <= {section for section, _, _ in reader.uses}
    assert {section for section, _, _ in reader.uses} <= set(re.findall(r'<section[^>]*id="([^"]+)"', output))
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
def test_chart_free_mode_plots_zero_lane_and_set_attribution(summary, render, stat, problem_set):
    """Codex at $0 stays on the plot, in a $0 lane, and can reach the frontier."""
    normal, normal_front = render(summary, free=False, problem_set=problem_set)
    output, frontier = render(summary, free=True, problem_set=problem_set)
    svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', output, re.S)[0])
    points = {g.get("data-c"): g for g in svg.findall("s:g[@class='pt']", NS)}
    if problem_set == "main":
        values = page.every(summary)
        assert set(points) == set(page.ORDER)
        zero = {c for c in page.ORDER if values[c]["claude_usd_per_pass"] == 0}
    else:
        values = page.rescue_arms()
        assert set(points) == set(page.NAME)
        zero = {c for c in page.NAME if values[c]["claude_usd_per_pass"] == 0}
    assert zero and "free-strip" not in output
    assert "$0" in [t.text for t in svg.findall("s:text", NS)]
    assert "$0" not in [t.text for t in ET.fromstring(re.search(r'<svg\b.*?</svg>', normal, re.S)[0]).findall("s:text", NS)]
    assert set(frontier) & zero and frontier != normal_front
    assert "$0.00000" not in output and "log" in output
    for point in points.values():
        assert point.get("data-set") == problem_set
        assert ("retest set" if problem_set == "rescue" else "main ladder") in point.get("data-tip").lower()
    for c in zero:
        assert "saved" in re.search(r'<li tabindex="0" data-c="' + re.escape(c) + r'"[^>]*>.*?</li>', output, re.S)[0]


def test_free_pass_frontier_is_codex_and_pipelines(summary):
    _, normal = page.pass_cost(summary, free=False)
    _, free = page.pass_cost(summary, free=True)
    _, rescue = page.pass_cost(summary, free=True, problem_set="rescue")
    assert normal[-1] == "haiku-high"
    assert {"sol61-high", "sol61-high-fast"} <= set(free)
    assert not any(c.startswith(("haiku", "sonnet")) for c in free)
    assert "sol61-high-fast+haiku-on-fail" in rescue


def test_speed_axis_is_trimmed_with_one_second_gridlines(summary):
    output, _ = page.speed_cost(summary, free=False)
    svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', output, re.S)[0])
    ticks = [t.text for t in svg.findall("s:text", NS) if "x-tick" in t.get("class", "").split()]
    medians = [v["latency_s"]["median"] for c, v in page.every(summary).items() if c in page.ORDER]
    first, last = (int(t.split()[0]) for t in (ticks[0], ticks[-1]))
    assert first > 0 and first <= min(medians) - 1 and last >= max(medians) + 1 and last - max(medians) < 6
    assert len(svg.findall("s:line[@stroke-opacity='.45']", NS)) == (last - first) - (last - first) // 5


@pytest.mark.parametrize("render", [page.pass_cost, page.speed_cost])
def test_chart_set_toggle_and_grouped_keys(summary, render):
    output, _ = render(summary)
    assert 'Codex is free (subscription quota)</label>' in output
    assert 'Main ladder' in output and '> Retest set + pipelines</label>' in output
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
    assert 'title="only on the retest set"' in pipeline_chip
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
    if free and render is page.pass_cost:  # the $0 lane narrows the log axis: decades only
        expected = [dataset.usd(v) for v in ((0.0001,) if problem_set == "rescue" else ()) + (0.001, 0.01, 0.1)]
    elif free and problem_set == "rescue":
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
    assert "[retest set]" not in output
    svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', output, re.S)[0])
    for point in svg.findall("s:g[@class='pt']", NS):
        marker = point[-2]
        name = point.get("data-c")
        assert bool(marker.get("stroke-dasharray")) == ("bare" in name)
        assert (marker.get("fill") == "var(--panel)") == ("-fast" in name)
        if point.get("data-cat") == "pipelines":
            assert marker.get("stroke") == "var(--frontier)"
        elif "-fast" not in name:
            assert marker.get("fill") == marker.get("stroke")


def test_frontier_caption_uses_computed_costs(summary):
    values = page.every(summary)
    medium, low = values["luna-medium"], values["luna-low"]
    caption = page.frontier_caption(summary)
    assert 'luna-low is not a best trade-off:' in caption
    assert f'luna-medium costs the same, {dataset.usd(medium["usd_per_pass"], sig=1)} per pass.' in caption
    assert dataset.usd(low["usd_per_pass"], sig=1) == dataset.usd(medium["usd_per_pass"], sig=1)
    assert page.esc(f"It passes {medium['passes']}/{medium['n']} to luna-low's {low['passes']}/{low['n']}.") in caption
    assert 'Main ladder only' in caption
    assert 'every point counts' in caption
    for render in (page.pass_cost, page.speed_cost):
        output, _ = render(summary)
        main, rescue = output.split('<div class="cset s-rescue">', 1)
        assert output.count('class="frontier-note"') == 1
        assert caption in main
        assert 'class="frontier-note"' not in rescue


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
    assert len(targets) == 14
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
    facts = dataset.read()['facts']
    rendered = report.render()[2]
    method = re.search(r'<section\b[^>]*\bid="method"[^>]*>(.*?)</section>', rendered, re.S).group(1)
    fair = re.search(r'<section\b[^>]*\bid="fair"[^>]*>(.*?)</section>', rendered, re.S).group(1)
    assert 'make Codex look bad' not in method and 'Exact commands' not in method
    assert f"{len({r['problem'] for r in rows})} hard problems, {len({r['repeat'] for r in rows})} tries each" in fair
    for config in ('luna-low', 'haiku-low'):
        for harness in ('claude-one-shot', 'codex-tool-loop'):
            cell = [r for r in rows if (r['config'], r['harness']) == (config, harness)]
            assert f">{sum(r['passed'] for r in cell)}</text>" in fair
    codex = [r for r in rows if r['harness'] == 'codex-tool-loop']
    start = min(datetime.fromisoformat(r['ts']).timestamp() for r in codex)
    end = max(datetime.fromisoformat(r['ts']).timestamp() + r['wall_s'] for r in codex)
    assert f"{sum(r['outcome'] == 'harness_error' for r in codex)} harness errors and no timeouts" in fair
    assert facts['hb_minutes'] == f"{(end - start) / 60:.0f}"
    assert f"in about {facts['hb_minutes']} minutes." in fair
    comparison = harness_bias.pass_summary(rows)
    lo, hi = comparison['ci']
    assert f"{facts['hb_answer']} haiku-low still led on both" in fair
    assert (f"<li>The gap moved {100 * comparison['diff']:.0f} points, "
            f"below our {facts['hb_bar_points']}-point bias bar.</li>") in fair
    assert f"range is {100 * lo:.0f} to {100 * hi:.0f} points, so a larger bias is possible." in fair
    wrong = [sum(r['outcome'] == 'wrong' for r in rows if (r['harness'], r['config']) == (h, 'luna-low')) for h in ('claude-one-shot', 'codex-tool-loop')]
    assert f"wrong outputs from {wrong[0]} to {wrong[1]}" in fair



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
    assert updated['facts']['hb_claude_luna_low'] == updated['facts']['hb_codex_luna_low'] == f'{passes}/{n}'
    lo, hi = harness_bias.pass_summary(changed)['ci']
    assert f'No bias of about {max(abs(lo), abs(hi)):.1f} or more was detectable' in rendered
    assert f'{100 * lo:.0f} to {100 * hi:.0f}' in updated['facts']['hb_range_points']


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
    assert 'astra-medium-fast' in page.speed_cost(changed)[1]  # a full second faster: every point is eligible
    assert page.speed_dominates(dict(x=10, y=1), dict(x=9.9, y=2))
    assert not page.speed_dominates(dict(x=10, y=1), dict(x=9, y=2))


def test_rescue_tab_names_best_trade_offs_in_a_numbered_list_not_on_the_plot():
    for render in (page.hard_pass_cost, page.hard_speed_cost):
        html, front = render()
        svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', html, re.S)[0])
        labels = [e.text for e in svg.findall('s:text', NS)]
        assert 'luna-high-bare→retry' not in labels and not any(l in labels for l in ('plan→luna-low', 'luna-low→H fail'))
        chips = [e.text for e in svg.findall(".//s:text[@class='rk-n']", NS)]
        assert chips == [str(i) for i in range(1, len(front) + 1)] and chips
        assert svg.find(".//s:path[@class='zone']", NS) is not None
        listed = re.findall(r'<li data-c="([^"]+)"[^>]*tabindex="0">.*?<b>\d</b>', re.search(r'<div class="picks">.*?</div>', html, re.S)[0])
        assert sorted(listed) == sorted(front)
        assert 'a numbered point' in html


def test_marker_styles_distinguish_fast_generation_and_luna_variants():
    def draw(c):
        return page.config_marker(c, 0, 0)
    assert 'var(--panel)' in draw('sol61-high-fast')
    assert draw('sol61-high') != draw('sol56-high')
    assert len({draw(c) for c in ('luna-low', 'luna-medium', 'luna-high', 'luna-low-bare', 'luna56-low')}) == 5


def test_bar_charts_fit_phone_without_scrolling(summary):
    for body in (page.floor(summary), page.fast(summary), page.pipes()):
        assert 'svgscroll' not in body
        assert 'Scroll sideways' not in body
        if '<svg' not in body: continue  # pipes is plain HTML rows that wrap on a phone
        svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', body, re.S)[0])
        assert float(svg.get('viewBox').split()[2]) <= 390
        for label in svg.findall('s:text', NS):
            assert 0 <= float(label.get('x')) < 390


def test_quality_fast_coverage_keeps_main_and_separate_rescue_runs_apart(summary, monkeypatch):
    note = dataset.read()["facts"]["quality_fast_note"]
    assert 'sol61-high ⚡ and astra-medium ⚡: main-ladder solutions not scored' in note
    assert f'{dataset.read()["rescue"]["sol61-high"]["n"]}-attempt retest run' in note
    assert 'astra-medium ⚡ has no retest scores' in note
    scored = next(r for r in dataset.quality_rows() if r['config'] == 'sol61-high-fast' and r['outcome'] == 'pass')
    main = dict(scored, phase='exploratory')
    monkeypatch.setattr(dataset, 'quality_rows', lambda: [scored, main])
    table = dataset.quality_table({'configs': {}, 'exploratory': {'sol61-high-fast': {'passes': 1}}})
    assert table['rows'][0][:2] == ['sol61-high ⚡ †', '1']


def test_rescue_label_leaders_start_at_the_named_point():
    for render in (page.hard_pass_cost, page.hard_speed_cost):
        svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', render()[0], re.S)[0])
        points = {g.get('data-c'): g.findall('s:circle', NS)[-1] for g in svg.findall("s:g[@class='pt']", NS)}
        for lead in svg.findall("s:line[@class='label-leader']", NS):
            circle = points[lead.get('data-c')]
            dx = float(lead.get('x1')) - float(circle.get('cx'))
            dy = float(lead.get('y1')) - float(circle.get('cy'))
            assert (dx * dx + dy * dy) ** .5 == pytest.approx(8, abs=.15)



def test_winner_and_conclusion_agree_and_sets_are_collapsed(summary):
    template = (ROOT / "docs/page.tmpl.md").read_text()
    assert template.count('<b>{{winner_line}}</b>') == 2
    assert 'Codex first' not in template
    winner = re.search(r'<section[^>]*id="winner">(.*?)</section>', template, re.S)[1]
    assert winner.index('{{winner_line}}') < winner.index('<details') < winner.index('{{w_winner}}')
    assert '<details class="sets"><summary>' in page.sets_box(summary)
    assert ' open' not in page.sets_box(summary).split('>')[0]
    assert template.index('{{w_sets}}') > template.index('{{w_pass_cost}}')
    assert page.method(summary)[0].count("We added L7 to find the others' limit.") == 1
    assert 'L7 has' not in page.sets_box(summary)
    problems = page.method(summary)[0]
    assert 'p01 overlap_minutes (L1)' in problems
    first = problems.split('<li class="prow">', 1)[1].split('</li>', 1)[0]
    assert first.index('p01 overlap_minutes (L1)') < first.index('class="lc medium"')


def test_winner_verdict_and_luna_high_tradeoff(summary):
    E = page.every(summary)
    verdicts = {c: page.verdict(c, E[c], report.need, E) for c in page.ORDER}
    assert verdicts['haiku-low'] == 'trade-off'
    assert verdicts['sol61-high-fast'] == '✓ pick'
    assert verdicts['haiku-high'] == '✓ pick (budget)'
    assert verdicts['sonnet-medium'] == '✓ pick (speed)'
    assert verdicts['luna-high'] == 'trade-off'
    winner = page.winner_table(dataset.read(), report.need)
    picks = set(re.findall(r'<td data-label="Pick"><span>(.*?)</span></td>', winner))
    assert {configs.display(c) for c, verdict in verdicts.items() if verdict.startswith('✓ pick')} == picks
    results = page.short_table(summary, report.need)
    result_rows = ET.fromstring('<root>' + results + '</root>').findall('.//tbody/tr')
    result_picks = [''.join(row[0].itertext()) for row in result_rows
                    if (cell := row.find('td[@class="verdict-cell"]')) is not None
                    and cell.text.startswith('✓ pick')]
    assert set(result_picks) == picks
    assert len(result_picks) == len(picks)


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


def test_cost_accuracy_has_one_selector_per_chart_and_one_sets_guide():
    template = (ROOT / 'docs/page.tmpl.md').read_text()
    assert template.count('{{w_sets}}') == 1
    assert 'name="pset"' not in template
    rendered = report.render()[2]
    section = re.search(r'<section id="pareto">(.*?)</section>', rendered, re.S)[1]
    assert section.count('class="cost-toggle"') == 2
    assert section.count('class="set-filter"') == 2
    assert section.index('class="cplot"') < section.index('<summary>How to read these charts</summary>') < section.index('Ringed, numbered points are best trade-offs')


def test_main_markers_follow_config_encoding(summary):
    output, _ = page.pass_cost(summary, free=False)
    svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', output, re.S)[0])
    for point in svg.findall("s:g[@class='pt']", NS):
        c = point.get('data-c')
        expected = ET.fromstring(f'<svg xmlns="{NS["s"]}">{page.config_marker(c, 0, 0)}</svg>')[0]
        mark = point[-2]
        assert mark.tag == expected.tag
        for attr in ('fill', 'stroke', 'stroke-dasharray'):
            assert mark.get(attr) == expected.get(attr)


def test_speed_frontier_lines_and_single_point_free_mode(summary):
    output, names = page.speed_cost(summary, free=False)
    assert names == ['haiku-low', 'luna-high']
    svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', output, re.S)[0])
    path = next(p for p in svg.findall('s:path', NS) if p.get('stroke') == 'var(--frontier)')
    assert path.get('d')
    labels = {t.text for t in svg.findall('s:text', NS) if 'lbl' in t.get('class', '')}
    assert {'sol61-high ⚡', 'sonnet-medium'} <= labels  # picks off the frontier keep a name
    assert not {'haiku-low', 'luna-high'} & labels  # frontier points are numbered chips named in the list under the plot
    assert [t.text for t in svg.findall('.//s:text[@class="rk-n"]', NS)] == ['1', '2']
    assert re.findall(r'<b>(\d)</b><span>([^<]+)</span>', output.split('class="picks"', 1)[1])[:2] == [('1', 'haiku-low'), ('2', 'luna-high')]
    assert svg.find('s:path[@class="zone"]', NS).get('d').endswith('Z')
    output, names = page.speed_cost(summary, free=True)
    assert names == ['astra-medium-fast']
    svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', output, re.S)[0])
    labels = {t.text for t in svg.findall('s:text', NS) if 'lbl' in t.get('class', '')}
    assert '<b>1</b><span>astra-medium ⚡</span>' in output
    assert svg.find('s:path[@class="zone"]', NS) is not None  # a single best point still shades what it beats


def test_svg_data_lets_sort_js_rebuild_the_frontier(summary):
    # sort.js refront() redraws the frontier from data-v when a category is hidden; with none hidden it must match.
    for chart in (page.pass_cost, page.speed_cost):
        for free in (False, True):
            output, names = chart(summary, free=free)
            svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', output, re.S)[0])
            path = next(p for p in svg.findall('s:path', NS) if p.get('data-front'))
            speed = path.get('data-front') == 'speed'
            pts = [(g.get('data-c'), *map(float, g.get('data-v').split()))
                   for g in svg.findall("s:g[@class='pt']", NS) if g.get('data-out') is None]
            def better(a, b):
                if not speed: return a[1] <= b[1] and a[2] >= b[2]
                t = min(.5, b[1] * .05)
                return a[2] < b[2] and a[1] <= b[1] + t or a[2] == b[2] and a[1] <= b[1] - t
            front = {p[0] for p in pts if not any(q is not p and better(q, p) and q[1:] != p[1:] for q in pts)}
            assert front == set(names), (chart.__name__, free)


def test_luna_miss_views_share_points_and_separate_coincident_models(summary):
    for primary, hard in ((page.pass_cost, page.hard_pass_cost), (page.speed_cost, page.hard_speed_cost)):
        direct, frontier = primary(summary, free=False, problem_set='rescue')
        alternate, alternate_frontier = hard(page.rescue_arms(summary))
        assert direct == alternate
        assert frontier == alternate_frontier
        svg = ET.fromstring(re.search(r'<svg\b.*?</svg>', direct, re.S)[0])
        points = {g.get('data-c'): g for g in svg.findall("s:g[@class='pt']", NS)}
        targets = {c: (g[-1].get('cx'), g[-1].get('cy')) for c, g in points.items()}
        labels = {t.text for t in svg.findall('s:text', NS) if 'lbl' in t.get('class', '')}
        # Names stay off the plot: only a pick that is not a numbered best trade-off keeps one (the rest are in the list).
        assert 'sonnet-medium' in labels and labels <= {page.NAME[c] for c in page.WINNER_PICKS}
        assert not labels & {page.NAME[c] for c in frontier}
        stat = 'pass' if primary is page.pass_cost else 'speed'
        expected_points = page.ladder_repairs(False, stat, page.rescue_arms(summary))
        assert set(targets) == {p['c'] for p in expected_points}
        for point in expected_points:
            assert points[point['c']].get('data-tip') == point['tip']
        builders = ('sol61-high', 'astra-medium') if primary is page.pass_cost else ('sol61-high-fast', 'astra-medium-fast')
        for builder in builders:
            pipeline = builder + '+haiku-on-fail'
            assert targets[builder] != targets[pipeline]
        assert set(targets) == set(page.NAME)


def test_winner_has_three_rows_and_metric_columns_before_why():
    ds = dataset.read()
    output = page.winner_table(ds, dataset.need)
    head = re.findall(r'<th scope="col">(.*?)</th>', output)
    assert head == ['Use case', 'Pick', 'Pass', '$ per pass', 'Time', 'Why']
    body = re.search(r'<tbody>(.*?)</tbody>', output, re.S)[1]
    assert body.count('<tr>') == 3
    assert 'table-layout:fixed' not in output and 'min-width:720px' not in output
    for label in head:
        assert body.count(f'data-label="{label}"') == 3
    assert 'Numbers:' in output and 'retest set' not in output  # pipelines are not Winner picks
    assert ds['facts']['speed_why'] in output


def test_failure_copy_keeps_main_and_l7_counts_separate():
    facts = dataset.read()['facts']
    assert int(facts['hl_main_timeouts']) + int(facts['hl_main_crashes']) == int(facts['hl_main_misses'])
    assert int(facts['hl_main_timeouts']) + int(facts['l7_hl_fail']) == int(facts['hl_timeouts'])
    assert int(facts['hl_main_crashes']) == int(facts['hl_crashes'])


def test_conclusion_is_short_and_has_one_route_scope():
    template = (ROOT / "docs/page.tmpl.md").read_text()
    section = re.search(r'<section class="verdict conclusion".*?</section>', template, re.S)[0]
    steps, bullets = re.search(r'<ol.*?</ol>', section, re.S)[0], re.search(r'<ul.*?</ul>', section, re.S)[0]
    assert steps.count('<li>') == 3
    assert bullets.count('<li>') <= 5
    assert '{{default_route_scope}}' in steps
    assert 'See <a' not in bullets
    assert bullets.count('{{sonnet_medium_med}}') == 1
    assert bullets.count('{{sm_vs_hh_x}}') == 1


def test_badges_and_thresholds_have_distinct_meanings():
    ds = dataset.read()
    body = ('<section><span class="lc hard" title="Hard: my LeetCode difficulty guess">H</span>'
            '<p>E/M/H = my LeetCode difficulty guess. Cheapest at ≥95%.</p>'
            '<p>≥N% and ≥95% (all passed). luna→H fail</p></section>')
    rendered = page.notation_tooltips(body, ds)
    assert '>H</span>' in rendered
    assert 'E/M/H = my' in rendered
    assert 'Cheapest at ≥95%.' in rendered
    assert rendered.count('data-notation="≥N%"') == 1
    assert 'title="Hard: my LeetCode difficulty guess"' in rendered
    assert 'data-notation="→H fail"' in rendered


def test_winner_cells_have_one_content_element():
    from html.parser import HTMLParser
    class Cells(HTMLParser):
        def __init__(self):
            super().__init__(); self.depth = 0; self.children = []; self.text = []
        def handle_starttag(self, tag, attrs):
            if tag == 'td': self.depth = 1; self.children.append([])
            elif self.depth:
                if self.depth == 1: self.children[-1].append(tag)
                self.depth += 1
        def handle_endtag(self, tag):
            if self.depth: self.depth -= 1
    parser = Cells(); parser.feed(page.winner_table(dataset.read(), dataset.need))
    assert parser.children == [['span']] * 18


def test_low_context_has_one_final_group_and_a_set_column(summary):
    body = page.short_table(summary, dataset.need)
    groups = re.findall(r'<tbody[^>]*>(.*?)</tbody>', body, re.S)
    assert len(groups) == 3
    assert body.count('Low context (trimmed prompt):') == 1
    assert groups[-1].count('<tr') == 1  # one line, not one row per config
    assert 'luna-low-bare' in groups[-1] and 'luna-high-bare' in groups[-1]
    assert configs.set_label('main ladder') in groups[-1]
    assert configs.set_label('rescue set') in groups[-1]
    assert all('luna-low-bare' not in group and '</span>luna-high-bare</td>' not in group for group in groups[:-1])
    titles = re.findall(r'class="verdict-cell" title="([^"]+)"', body)
    assert titles and all(title == page.esc(summary['facts']['verdict_key']) for title in titles)


def test_scatter_categories_follow_registry_and_shared_rescue_names(summary):
    for c in page.ORDER:
        if c.endswith('-fast'):
            assert page.point_category(c) == 'fast'
        else:
            main = configs.REGISTRY['main', c]['category'] == 'main ladder' or c in page.WINNER_PICKS
            expected = 'main' if main else 'exploratory'
            assert page.point_category(c) == expected
    points = page.ladder_repairs(False, 'pass', page.rescue_arms(summary))
    assert {p['c'] for p in points} == set(page.NAME)
    assert all(p['name'] == configs.RESCUE_NAMES[p['c']] for p in points)
    assert 'luna-low+haiku-low-repair' not in {p['c'] for p in points}


def test_close_points_are_separated_and_labelled():
    points = [dict(c='luna-low', x=100, y=20), dict(c='luna-medium', x=108, y=24)]
    page.separate_points(points, lambda v: v, lambda v: v)
    assert all(p['label'] for p in points)
    assert abs(points[0]['plot_x'] - points[1]['plot_x']) >= 14


def test_pilot_display_names_preserve_run_ids():
    for old in ('codex-low', 'codex-medium', 'codex-low-lean', 'codex-bare'):
        assert configs.display(old).startswith('sol61-')
        assert configs.entry('pilot', old)['id'] == 'pilot/' + old
    assert configs.display('codex-low') != configs.display('sol61-low-prio')


def test_monetary_ratios_use_raw_prices(summary):
    facts = summary['facts']
    raw = json.loads((Path(__file__).resolve().parents[1] / 'results' / 'summary.json').read_text())
    sm, hh = raw['configs']['sonnet-medium']['usd_per_pass'], raw['exploratory']['haiku-high']['usd_per_pass']
    assert facts['sm_vs_hh_x'] == f"{sm / hh:.1f}×"  # from raw values, not the rounded prices
    table = dataset.read()['tables']['fastmode']['rows']
    a, b = (float(table[i][4].replace('$', '')) for i in (2, 0))
    assert facts['fm_x_cost'] == f"{a / b:.1f}×"


def test_pipes_are_grouped_under_plain_headings_and_fast_rows_are_filled():
    body = page.pipes()
    headings = re.findall(r'<p class="pg-h">([^<]+)</p>', body)
    assert headings[0] == 'Single models' and len(headings) == len(page.PIPE_GROUPS)
    assert all(h.count('(') == 0 or '→' in h for h in headings)
    assert body.count('class="pg-row"') == len(page.NAME)  # every row stays
    fast_rows = [c for c in page.NAME if '-fast' in c]
    assert body.count('bar-fill bar-hollow') == len(fast_rows) > 0
    assert 'fast mode' in body


def test_equiv_rows_pair_a_claude_config_with_a_codex_config_in_the_rendered_page():
    # Regression: the 8-column table hid every Codex column on a narrow screen.
    d = json.loads((ROOT / "results" / "dataset.json").read_text())
    fam = {r["display"]: r["family"] for r in d["rows"]}
    rows = d["tables"]["equiv"]["rows"]
    assert rows
    for r in rows:
        left, right = r[0].split(" → ")
        assert (fam[left], fam[right]) == ("Claude", "Codex"), r
        assert all(" → " in c for c in r[1:]), r
    html = (ROOT / "results" / "report" / "page.html").read_text()
    sec = html[html.index('id="equiv"'):]
    assert all(r[0].split(" → ")[1] in sec for r in rows)
    # The reverse table gives every Codex main-ladder config its own row.
    back = d["tables"]["equiv_back"]["rows"]
    codex = {r["display"] for r in d["rows"] if r["family"] == "Codex" and r["source"] == "main" and r["set"] == "main ladder"}
    assert {r[0].split(" → ")[0] for r in back} == codex
    assert all(fam[r[0].split(" → ")[1]] == "Claude" for r in back)
    text = " ".join(re.sub(r"<[^>]+>", "", sec).split())
    assert all(c in text for c in codex)


def test_landcheck_lists_removed_page_text_and_header():
    from analysis import landcheck
    old = landcheck.read('<h2>A</h2><table><tr><th>Claude</th><th>Codex match</th></tr></table><p>gone line</p>')
    new = landcheck.read('<h2>A</h2><table><tr><th>Claude</th></tr></table>')
    assert old.lines - new.lines == {"Codex match", "gone line"}
    assert set(old.heads) - set(new.heads) == {"Claude | Codex match"}
