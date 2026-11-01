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


def assert_clear(tree):
    assert not tree.findall('.//s:path[@class="ex-leader"]', NS)
    assert not tree.findall('.//s:clipPath[@id="ex-label-clip"]', NS)
    points = [(float(e.get('data-x')), float(e.get('data-y')))
              for e in tree.findall('.//s:g[@data-x]', NS)]
    labels = tree.findall('.//s:text[@class="ex-label"]', NS)
    assert len(labels) <= 3
    for label in labels + tree.findall('.//s:text[@class="ex-number"]', NS):
        x, y = float(label.get('x')), float(label.get('y'))
        w = float(label.get('data-width'))
        left = x - (w if label.get('text-anchor') == 'end' else w/2 if label.get('text-anchor') == 'middle' else 0)
        for px, py in points:
            assert not (left < px+12 and px-12 < left+w and y-12 < py+12 and py-12 < y+3), label.attrib


def test_numbered_frontier_and_local_pick_labels_at_every_width(ds, phone):
    exp = ds['explorer']
    st = next(s for s in exp['sets'] if s['id'] == exp['default_set'])
    rows = {r['key']: r for r in exp['rows']}
    frontier = sorted((k for k, m in st['views']['list']['front']['membership'].items() if m['on_frontier']),
                      key=lambda k: (rows[k]['usd_per_pass'], k))
    trees = [(sample['width'], ET.fromstring(sample['chart'])) for sample in phone]
    trees += [(width, ET.fromstring(charts.explorer_svg(exp, width=width))) for width in (390, 760)]
    for width, tree in trees:
        numbered = tree.findall('.//s:text[@class="ex-number"]', NS)
        assert [e.get('data-key') for e in numbered] == frontier
        assert [e.text for e in numbered] == list(map(str, range(1, len(frontier)+1)))
        labels = tree.findall('.//s:text[@class="ex-label"]', NS)
        if width <= 480: assert not labels
        assert all(rows[e.get('data-key')]['winner_pick'] for e in labels)
        assert_clear(tree)
    for sample in phone:
        if sample['focused']: assert 'sonnet-medium' in sample['inspect']
    rendered = page.explorer(dataset.view(ds))
    chips = re.search(r'<ol id="ex-chips">(.*?)</ol>', rendered, re.S)[1]
    assert re.findall(r'data-key="([^"]+)"', chips) == frontier


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
