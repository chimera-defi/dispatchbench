"""P4b_chart: chart-first DOM, phone labels, clear leaders and factual captions."""
import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

import pytest

from analysis import charts, dataset, page

ROOT = Path(__file__).resolve().parents[1]
NS = {'s': 'http://www.w3.org/2000/svg'}


@pytest.fixture(scope='module')
def ds():
    return dataset.read()


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


def test_prerendered_chart_precedes_every_control(ds):
    # Exercise the renderer as well as the shipped output. No script execution.
    for html in (page.explorer(dataset.view(ds)), (ROOT / 'results/report/page.html').read_text()):
        parser = Elements()
        parser.feed(html)
        elements = parser.elements
        chart = next(i for i, (_, a) in enumerate(elements) if a.get('id') == 'ex-chart')
        svg = next(i for i, (t, _) in enumerate(elements) if i > chart and t == 'svg')
        for i, (_, attrs) in enumerate(elements):
            if attrs.get('id') in {'ex-set', 'ex-floor', 'ex-colour', 'ex-config-list', 'ex-reset'} or any(
                k in attrs for k in ('data-view', 'data-pricing', 'data-facet', 'data-config')
            ) or set(attrs.get('class', '').split()) & {'ex-controls', 'ex-filters', 'ex-configs'}:
                assert svg < i, attrs
        assert '<noscript>' in html


def test_colour_key_immediately_follows_chart_before_controls(ds):
    for html in (page.explorer(dataset.view(ds)), (ROOT / 'results/report/page.html').read_text()):
        parser = Elements()
        parser.feed(html)
        ids = [a.get('id') for tag, a in parser.elements if tag == 'div' and a.get('id', '').startswith('ex-')]
        assert ids.count('ex-legend') == 1
        assert ids[ids.index('ex-chart') + 1] == 'ex-legend'
        assert re.search(r'</svg></div>\s*<div id="ex-legend"', html)
        legend = next(i for i, (_, a) in enumerate(parser.elements) if a.get('id') == 'ex-legend')
        for i, (_, attrs) in enumerate(parser.elements):
            if set(attrs.get('class', '').split()) & {'ex-controls', 'ex-filters', 'ex-configs'}:
                assert legend < i


@pytest.fixture(scope='module')
def phone(ds):
    setup = (ROOT / 'tests/pareto_runtime.cjs').read_text().split('const h=context.harness,exp=payload.explorer', 1)[0]
    script = setup + '''
const h=context.harness,samples=[];
for(const width of [320,390,480,481,1280]){
 element('ex-chart').clientWidth=width;
 for(const focused of [false,true]){
  h.st.sel=focused?payload.explorer.rows.find(r=>r.config==='sonnet-medium'&&r.key.endsWith('@main ladder')).key:null;
  h.st.zk=focused?3:1;h.render();
  samples.push({width,focused,chart:element('ex-chart').innerHTML,legend:element('ex-legend').innerHTML,inspect:element('ex-inspect').textContent});
 }
}
console.log(JSON.stringify(samples));
'''
    result = subprocess.run(['node', '-e', script], input=json.dumps({'explorer': page.explorer_data(dataset.view(ds))}),
                            capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_prerendered_colour_key_matches_js_rebuilds_at_phone_and_desktop_widths(ds, phone):
    html = page.explorer(dataset.view(ds))
    legend = re.search(r'<div id="ex-legend" class="ex-meta">(.*?)</div>', html).group(1)
    exp = ds['explorer']
    st = next(s for s in exp['sets'] if s['id'] == exp['default_set'])
    rows = [r for r in exp['rows'] if r['key'] in st['rows'] and r['cost_kind'] != 'unmetered'
            and r['usd_per_pass'] is not None]
    for row in rows:
        label = row['family'] + ' ' + row['generation'] if charts.explorer_colour(row) == 'var(--data-codex-old)' else row['family']
        assert f'solid {charts.explorer_colour(row)};padding-left:6px;">{label}</span>' in legend
    assert {390, 1280} <= {sample['width'] for sample in phone}
    for sample in phone:
        assert sample['legend'] == legend


def test_phone_labels_are_frontier_only_even_after_selection_or_zoom(ds, phone):
    exp = ds['explorer']
    st = next(s for s in exp['sets'] if s['id'] == exp['default_set'])
    frontier = {key for key, m in st['views']['list']['front']['membership'].items() if m['on_frontier']}
    for sample in phone:
        tree = ET.fromstring(sample['chart'])
        keys = {key for e in tree.findall('.//s:text[@class="ex-label"]', NS)
                for key in json.loads(e.get('data-keys'))}
        if sample['width'] <= 480:
            assert keys == frontier
        else:
            assert frontier < keys
        if sample['focused']:
            assert 'sonnet-medium' in sample['inspect']
    tree = ET.fromstring(charts.explorer_svg(exp, width=390))
    assert {e.get('data-key') for e in tree.findall('.//s:text[@class="ex-label"]', NS)} == frontier
    assert tree.get('style') == 'min-width:0'


def segments(path):
    # All leader paths use deterministic orthogonal M/L coordinates.
    points = [tuple(map(float, p.split())) for p in re.split('[ML]', path) if p]
    return list(zip(points, points[1:]))


def assert_clear(tree):
    points = [(float(e.get('data-x')), float(e.get('data-y')))
              for e in tree.findall('.//s:g[@data-x]', NS)]
    if not points:
        # The static SVG's rings/markers carry their plotted centres.
        for e in tree.findall('.//s:g[@class="ex-point"]', NS):
            marker = next(c for c in e if c.tag.endswith(('circle', 'path')) and c.get('class') != 'ex-ring')
            if marker.tag.endswith('circle'):
                points.append((float(marker.get('cx')), float(marker.get('cy'))))
            else:
                x,y = map(float,re.match(r'M([\d.-]+) ([\d.-]+)',marker.get('d')).groups())
                points.append((x,y+6))
    bars = []
    for bar in tree.findall('.//s:path[@class="ex-ci"]', NS):
        nums = list(map(float, re.findall(r'-?\d+(?:\.\d+)?(?:e[+-]?\d+)?', bar.get('d'))))
        x,y = nums[:2]
        xx,yy = nums[2:] if len(nums) == 4 else (x,nums[2])
        bars.append((min(x,xx)-1,min(y,yy)-1,max(x,xx)+1,max(y,yy)+1))
    leaders = tree.findall('.//s:path[@class="ex-leader"]', NS)
    assert leaders
    for leader in leaders:
        assert leader.get('d'), leader.attrib
        for (x,y),(xx,yy) in segments(leader.get('d')):
            assert x == xx or y == yy
            left,right,top,bottom = min(x,xx),max(x,xx),min(y,yy),max(y,yy)
            for px,py in points:
                assert not (left-10 <= px <= right+10 and top-10 <= py <= bottom+10), leader.attrib
            for l,t,r,b in bars:
                assert not (left <= r and l <= right and top <= b and t <= bottom), leader.attrib


def test_default_leaders_clear_points_and_confidence_intervals(ds, phone):
    for width in (390,760):
        svg = charts.explorer_svg(ds['explorer'],width=width)
        assert svg == charts.explorer_svg(ds['explorer'],width=width)
        assert_clear(ET.fromstring(svg))
    for sample in phone:
        if not sample['focused']:
            assert_clear(ET.fromstring(sample['chart']))


def test_phone_leaders_do_not_overlap_each_other(ds, phone):
    trees = [ET.fromstring(charts.explorer_svg(ds['explorer'], width=390))]
    trees.extend(ET.fromstring(sample['chart']) for sample in phone
                 if sample['width'] == 390 and not sample['focused'])
    for tree in trees:
        routes = [segments(e.get('d')) for e in tree.findall('.//s:path[@class="ex-leader"]', NS)]
        for i, route in enumerate(routes):
            assert route
            for (x,y),(xx,yy) in route:
                for other in routes[:i]:
                    for (ox,oy),(oxx,oyy) in other:
                        assert not (max(min(x,xx),min(ox,oxx)) <= min(max(x,xx),max(ox,oxx))
                                    and max(min(y,yy),min(oy,oyy)) <= min(max(y,yy),max(oy,oyy)))


def test_caption_uses_dataset_fact_and_changes_with_measurements(ds):
    finding = ds['facts']['explorer_finding']
    assert finding == dataset.explorer_finding(ds['explorer'])
    assert finding in page.explorer(dataset.view(ds))
    assert finding.startswith('haiku-high is cheapest at 100%, at $0.0028 per pass. ')
    assert 'On the main ladder plus partial runs, at list price, that is the top observed pass rate; the frontier is ' in finding
    st = next(s for s in ds['explorer']['sets'] if s['id'] == ds['explorer']['default_set'])
    assert finding.endswith(st['note'])
    exp = copy.deepcopy(ds['explorer'])
    row = next(r for r in exp['rows'] if r['config'] == 'haiku-high' and r['set'] == 'main ladder')
    row['usd_per_pass'] = 1
    row['display'] = 'fixture renamed config'
    st = next(s for s in exp['sets'] if s['id'] == exp['default_set'])
    rows = [r for r in exp['rows'] if r['key'] in st['rows']]
    st['views']['list']['front']['membership'] = dataset.explorer_frontier(rows,'front')
    changed = dataset.explorer_finding(exp)
    assert changed != finding
    assert 'haiku-high' not in changed
    assert changed.startswith('terra61-low is cheapest at 100%, at ')

    # A changed best rate, price, name and scope must all reach the caption.
    for row in exp['rows']:
        if row['key'] in st['rows']:
            row['pass_rate'] = .5
    winner = next(r for r in rows if st['views']['list']['front']['membership'][r['key']]['eligible'])
    winner.update(pass_rate=.75, usd_per_pass=.25, display='fixture winner')
    st['label'] = 'Fixture scope'
    st['note'] = 'Fixture coverage caveat.'
    rows = [r for r in exp['rows'] if r['key'] in st['rows']]
    st['views']['list']['front']['membership'] = dataset.explorer_frontier(rows, 'front')
    changed = dataset.explorer_finding(exp)
    assert changed.startswith('fixture winner is cheapest at 75%, at $0.25 per pass. ')
    assert 'On the fixture scope, at list price, that is the top observed pass rate; the frontier is ' in changed
    assert changed.endswith(st['note'])
