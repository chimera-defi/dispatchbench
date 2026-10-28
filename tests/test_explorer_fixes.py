"""S4 regressions: portable paint, provenance and readable explorer geometry."""
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
def exp():
    return dataset.read()['explorer']


def test_standalone_charts_carry_exact_canonical_tokens():
    tokens = (ROOT / 'docs/page/tokens.css').read_text().strip()
    for name, svg in charts.build().items():
        if svg is None:
            continue
        tree = ET.fromstring(svg)
        styles = [e.text for e in tree.findall('s:style', NS)]
        assert styles.count(tokens) == 1, name
        assert '@import' not in svg, name


@pytest.mark.parametrize(('source', 'category', 'expected'), [
    ('main', 'main ladder', 'pre-registered'),
    ('pilot', 'pilot', 'pilot (preceded the main run)'),
    ('pilot-agentic', 'pilot', 'pilot (preceded the main run)'),
    ('main', 'exploratory', 'later exploration'),
    ('future-source', '?', 'unknown'),
])
def test_provenance_uses_declared_metadata(source, category, expected):
    assert dataset.explorer_provenance({'source': source, 'category': category}) == expected


@pytest.fixture(scope='module')
def runtime(exp):
    harness = (ROOT / 'tests/pareto_runtime.cjs').read_text()
    setup = harness.split('const h=context.harness,exp=payload.explorer', 1)[0]
    script = setup + r'''
const h=context.harness, samples={};
for(const name of ['default','focus','top']){
 h.st.view=name==='top'?'top':'front';
 h.st.sel=name==='focus'?payload.explorer.rows.find(r=>r.config==='sol61-high'&&r.key.endsWith('@main ladder')).key:null;
 h.render();samples[name]={chart:element('ex-chart').innerHTML,panels:element('ex-model-grid').innerHTML};
}
console.log(JSON.stringify(samples));
'''
    result = subprocess.run(['node', '-e', script],
                            input=json.dumps({'explorer': page.explorer_data({'explorer': exp})}),
                            text=True, capture_output=True, cwd=ROOT)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_axes_and_ticks_are_outside_plot_clip(runtime):
    for name in ('default', 'top'):
        tree = ET.fromstring(runtime[name]['chart'])
        clipped = tree.find('s:g[@clip-path]', NS)
        assert not clipped.findall('.//s:text', NS)
        labels = [e.text for e in tree.findall('s:text', NS)]
        assert '$ per pass (log) · left is cheaper' in labels
        if name == 'default':
            assert '100%' in labels
        else:
            assert 'Median seconds · up is faster' in labels
        clip = tree.find('s:defs/s:clipPath/s:rect', NS)
        assert float(clip.get('x')) >= 90


def test_speed_shade_closes_toward_slower(runtime):
    tree = ET.fromstring(runtime['top']['chart'])
    shade = tree.find('.//s:path[@class="ex-shade"]', NS)
    assert re.search(r'V412H[^Z]+Z$', shade.get('d'))
    assert 'V160H' in runtime['top']['panels']


def assert_labels_clear(tree, points):
    labels = [(e.text, float(e.get('x')), float(e.get('y')))
              for e in tree.findall('.//s:text[@class="ex-label"]', NS)]
    assert {'haiku-low', 'sonnet-medium'} <= {text for text, _, _ in labels}
    assert len(tree.findall('.//s:path[@class="ex-leader"]', NS)) == len(labels)
    for i, (text, x, y) in enumerate(labels):
        assert not any(x-8 <= px <= x+len(text)*7+8 and y-21 <= py <= y+9
                       for px, py in points), text
        for other, ox, oy in labels[:i]:
            assert not (abs(y-oy) < 18 and x < ox+len(other)*7+5 and ox < x+len(text)*7+5), (text, other)


def test_default_and_focused_labels_clear_points_and_each_other(exp, runtime):
    for name in ('default', 'focus'):
        tree = ET.fromstring(runtime[name]['chart'])
        points = [(float(e.get('data-x')), float(e.get('data-y')))
                  for e in tree.findall('.//s:g[@data-x]', NS)]
        assert_labels_clear(tree, points)
    # Static SVG positions are recorded in each point's vendor marker.
    tree = ET.fromstring(charts.explorer_svg(exp))
    points = []
    for group in tree.findall('.//s:g[@class="ex-point"]', NS):
        marker = next(e for e in group if e.tag.endswith(('circle', 'path')) and e.get('class') != 'ex-ring')
        if marker.tag.endswith('circle'):
            points.append((float(marker.get('cx')), float(marker.get('cy'))))
        else:
            x, y = map(float, re.match(r'M([\d.-]+) ([\d.-]+)', marker.get('d')).groups())
            points.append((x, y + 6))
    assert_labels_clear(tree, points)
