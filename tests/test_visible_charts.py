"""R3: useful charts stay visible when every details element is closed."""
from html.parser import HTMLParser
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class Visibility(HTMLParser):
    VOID = {'input', 'meta', 'link', 'br', 'hr', 'img', 'wbr'}
    def __init__(self):
        super().__init__(); self.stack = []; self.charts = 0; self.any_pair = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in self.VOID: self.stack.append((tag, a))
        ids = {a.get('id') for _, a in self.stack}
        if tag == 'svg' and a.get('role') == 'img' and 'pareto' in ids and not any(t == 'details' for t, _ in self.stack):
            # Multiple pricing/set variants are one chart figure.
            if not any('v-free' in a.get('class', '') or 's-rescue' in a.get('class', '') for _, a in self.stack):
                self.charts += 1
        if tag == 'figure' and a.get('id') == 'xfig' and 'extras' in ids: self.any_pair = True
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]; break


def test_visible_charts_and_any_pair_explorer():
    p = Visibility(); p.feed((ROOT / 'results/report/page.html').read_text())
    assert p.charts == 1
    assert p.any_pair
    html = (ROOT / 'results/report/page.html').read_text()
    assert '<button type="button" id="pair-speed-preset" aria-pressed="true" aria-controls="pair-speed">Speed vs $ per pass</button>' in html
    assert '<div id="pair-speed" class="chart">' in html
    assert '<div id="pair-custom" hidden>' in html
    # Native navigation to an already-selected hash must target the whole control row,
    # even when the link itself wraps onto another line on phones.
    assert '<p id="speed-vs-per-pass" class="ctl pair-presets"' in html



def test_restored_any_pair_script_and_projection():
    import json
    import subprocess
    from analysis import dataset, page
    s = dataset.view(dataset.read())
    data, html = page.any_pair_data(s), page.any_pair(s)
    result = subprocess.run(['node', 'tests/any_pair_runtime.cjs'],
                            input=json.dumps({'data': data, 'html': html}),
                            text=True, capture_output=True, cwd=ROOT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '100 any-pair' in result.stdout
    for row in data['points']:
        config = page.every(s)[row['c']]
        assert row['inp'] == config['tokens_mean']['in_tok']
        assert row['rsn'] == config['tokens_mean']['reasoning_tok']


def test_speed_chart_x_tick_labels_are_sparse():
    page = (ROOT / 'results/report/page.html').read_text()
    charts = [ET.fromstring(svg) for svg in re.findall(r'<svg\b.*?</svg>', page, re.S)
              if 'against median seconds per call' in svg.split('>', 1)[0]]
    assert len(charts) == 4  # main/rescue sets, each with list/free pricing
    for chart in charts:
        ticks = [t for t in chart.findall('{http://www.w3.org/2000/svg}text')
                 if 'x-tick' in t.get('class', '').split()
                 and re.fullmatch(r'\d+ s', t.text or '')]
        assert 2 <= len(ticks) <= 8, [t.text for t in ticks]
        xs = [float(t.get('x')) for t in ticks]
        assert all(b - a >= 40 for a, b in zip(xs, xs[1:])), xs
