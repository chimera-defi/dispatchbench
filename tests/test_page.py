"""Page guards for operator-reported regressions, run against results/report/page.html."""
import re
import xml.etree.ElementTree as ET
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from analysis import configs, dataset, page

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'results/report/page.html').read_text()
SECTIONS = ['winner', 'pareto', 'results', 'fail', 'pipes', 'equiv', 'grok', 'extras', 'fair', 'interesting', 'conclusion',
            'method', 'problems', 'tokens', 'limits', 'notes']
TOPBAR = ('<div class="ds-topbar"><div><a href="https://chimericlabs.xyz/">← Chimeric Labs</a>'
          '<a href="https://github.com/chimera-defi/dispatchbench">Source on GitHub</a></div></div>')


def test_first_choice_fonts_are_requested():
    urls = [unescape(u) for t in re.findall(r'<link\b[^>]*>', HTML) if 'rel="stylesheet"' in t
            for u in re.findall(r'href="([^"]+)"', t) if urlsplit(unescape(u)).hostname == 'fonts.googleapis.com']
    requested = {f.split(':')[0] for u in urls for f in parse_qs(urlsplit(u).query).get('family', [])}
    for token in ('body', 'heading', 'mono'):
        family = re.findall(r'--font-' + token + r'\s*:\s*([^,;]+)', HTML)[-1].strip('" ')
        if family not in {'system-ui', 'ui-monospace', 'monospace', 'sans-serif', 'serif'}:
            assert family in requested, (token, family, requested)
    assert {'Inter', 'JetBrains Mono'} <= requested


def test_page_is_self_contained():
    for m in re.finditer(r'<link\b[^>]*>', HTML):
        tag = m[0]
        if 'stylesheet' in tag:
            assert re.search(r'href="(https?:)?//', tag), tag
    assert not re.search(r'\b(?:src|href)="\.{1,2}/', HTML)
    css = '\n'.join(s.strip() for s in re.findall(r'<style>(.*?)</style>', HTML, re.S))
    expected = '\n'.join((ROOT / 'docs/page' / n).read_text().strip() for n in ('tokens.css', 'topbar.css', 'style.css'))
    assert css == expected
    for name in ('--color-surface', '--accent'):
        assert re.search(re.escape(name) + r'\s*:', css), name


def test_title_and_topbar():
    heads = re.findall(r'<h1[^>]*>(.*?)</h1>', HTML, re.S)
    assert heads == ['DispatchBench: which model should a coding task go to?']
    assert HTML.index('<h1') < HTML.index('<svg')
    assert re.search(r'<body[^>]*>\s*' + re.escape(TOPBAR), HTML)
    assert HTML.count(TOPBAR) == 1


class Charts(HTMLParser):
    VOID = {'input', 'meta', 'link', 'br', 'hr', 'img', 'wbr'}

    def __init__(self):
        super().__init__(); self.stack = []; self.charts = 0; self.xfig = False; self.hero = False; self.explorer = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in self.VOID: self.stack.append((tag, a))
        ids = {s[1].get('id') for s in self.stack}
        closed = any(t == 'details' for t, _ in self.stack)
        if tag == 'svg' and 'hero-wide' in a.get('class', '') and a.get('role') == 'img' and 'pareto' in ids and not closed:
            self.charts += 1
        if a.get('id') == 'hero' and tag == 'figure' and a.get('class') == 'hero-chart' and 'pareto' in ids: self.hero = True
        if a.get('id') == 'ex-chart' and 'extras' in ids and not closed: self.explorer = True
        if tag == 'figure' and a.get('id') == 'xfig' and 'extras' in ids: self.xfig = True

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]; break


def test_charts_visible_with_details_closed_and_xfig_present():
    p = Charts(); p.feed(HTML)
    assert p.charts == 1 and p.hero and p.explorer and p.xfig
    for frag in ('<button type="button" id="pair-speed-preset" aria-pressed="true" aria-controls="pair-speed">Speed vs $ per pass</button>',
                 '<div id="pair-speed" class="chart">', '<div id="pair-custom" hidden>', '<p id="speed-vs-per-pass" class="ctl pair-presets"',
                 '<details open><summary>Explore tokens, reasoning, and latency</summary>'):
        assert frag in HTML, frag


def test_speed_chart_ticks_are_sparse():
    charts = [ET.fromstring(s) for s in re.findall(r'<svg\b.*?</svg>', HTML, re.S)
              if 'against median seconds per call' in s.split('>', 1)[0]]
    assert len(charts) == 4
    for chart in charts:
        ticks = [t for t in chart.findall('{http://www.w3.org/2000/svg}text')
                 if 'x-tick' in t.get('class', '').split() and re.fullmatch(r'\d+ s', t.text or '')]
        assert 2 <= len(ticks) <= 8
        xs = [float(t.get('x')) for t in ticks]
        assert all(b - a >= 40 for a, b in zip(xs, xs[1:])), xs


def boxes(labels):
    out = []
    for x, y, anchor, txt in labels:
        w = len(unescape(txt)) * 5.5
        left = float(x) - w if anchor == 'end' else float(x) - w / 2 if anchor == 'middle' else float(x)
        out.append((txt, left, float(y) - 11, left + w, float(y) + 3))
    return out


def overlaps(bs):
    return [(a[0], b[0]) for i, a in enumerate(bs) for b in bs[i + 1:]
            if a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]]


def test_scatter_labels_do_not_overlap():
    assert overlaps(boxes([('10', '20', 'start', 'aaaa (100%)')] * 2))  # the detector works
    bad, seen = [], 0
    for svg in re.findall(r'<svg.*?</svg>', HTML, re.S):
        labs = re.findall(r'<text x="([\d.-]+)" y="([\d.-]+)" text-anchor="(\w+)" class="lbl[^"]*" data-cat="(\w+)" data-set="(\w+)">([^<]*)</text>', svg)
        if labs:
            seen += 1
            bad += overlaps(boxes([(x, y, a, c + ':' + t) for x, y, a, c, _, t in labs]))
    assert seen >= 4 and bad == []


def test_sections_ids_and_permalinks():
    ids = re.findall(r'\sid="([^"]+)"', HTML)
    assert len(ids) == len(set(ids))
    assert re.findall(r'<section\b[^>]*?\bid="([^"]+)"', HTML) == SECTIONS
    toc = re.search(r'<nav class="toc"[^>]*>(.*?)</nav>', HTML, re.S)[1]
    assert re.findall(r'href="#([^"]+)"', toc) == SECTIONS  # the contents strip lists every section, in page order
    for s in SECTIONS:
        m = re.search(r'<section\b[^>]*?\bid="' + s + r'"[^>]*>.*?<h[1-6][^>]*>(.*?)</h[1-6]>', HTML, re.S)
        assert f'<a class="hlink" href="#{s}" aria-label="Link to this section: ' in m[1], s
    assert re.findall(r'<li class="prow" id="(p\d\d)"|<li id="(pilot-[^"]+)"', HTML)  # problem rows exist
    for i in range(1, 16):
        assert f'href="#p{i:02}" aria-label="Link to this section' in HTML, i


def test_sortable_headers_and_script_inlined():
    script = (ROOT / 'docs/page/sort.js').read_text().strip().replace(
        '__RESCUE_SET_LABEL__', __import__('json').dumps(configs.set_label('rescue set')))
    assert script in [b.strip() for b in re.findall(r'<script>(.*?)</script>', HTML, re.S)]


def test_explorer_chart_first_then_legend_then_controls():
    elements = []

    class P(HTMLParser):
        def handle_starttag(self, tag, attrs): elements.append((tag, dict(attrs)))
    P().feed(HTML)
    chart = next(i for i, (_, a) in enumerate(elements) if a.get('id') == 'ex-chart')
    svg = next(i for i, (t, _) in enumerate(elements) if i > chart and t == 'svg')
    legend = next(i for i, (_, a) in enumerate(elements) if a.get('id') == 'ex-legend')
    assert svg < legend
    assert re.search(r'</svg></div>\s*<div id="ex-legend"', HTML)
    for i, (_, a) in enumerate(elements):
        if a.get('id') in {'ex-set', 'ex-floor', 'ex-colour', 'ex-config-list', 'ex-reset'} or set(a.get('class', '').split()) & {'ex-controls', 'ex-filters', 'ex-configs'}:
            assert legend < i, a


def test_grok_section_bytes_pinned():
    import hashlib
    body = re.search(r'<section id="grok">.*?</section>', HTML, re.S)[0]
    original, restored = body.split('<details class="small"><summary>Grok comparisons and methods</summary>', 1)
    assert hashlib.sha256((original + '</section>').encode()).hexdigest() == '9fcb9868f2abc0cbde44f46607fc6447466c17aa7eabab271d38c049f6558fda'
    assert 'id="closest-lanes-by-pass-rate"' in restored and 'id="devin"' in restored


def test_every_config_family_appears_on_the_page():
    rows = dataset.read()['rows']
    families = {r['family'] for r in rows}
    assert {'Claude', 'Codex', 'Grok', 'Devin', 'Hetzner'} <= families
    for family in sorted(families):
        assert family in HTML, family
    for name in {r['display'] for r in rows}:
        assert unescape(name) in unescape(HTML) or name in HTML, name


def hero_svgs():
    fig = re.search(r'<figure class="hero-chart" id="hero">.*?</figure>', HTML, re.S)[0]
    return re.findall(r'<svg\b.*?</svg>', fig, re.S)


def test_pick_sentences_sit_inside_the_picks_block():
    block = re.search(r'<div class="wpicks">.*?</div>\s*</div>|<div class="wpicks">.*', HTML, re.S)[0]
    facts = dataset.read()['facts']
    for pick in dataset.WINNER_PICKS.values():
        assert unescape(facts['winner_' + pick]) in unescape(re.sub(r'<[^>]+>', '', block)), pick
    assert block.count('class="wpick ') == len(dataset.WINNER_PICKS)


def test_hero_labels_are_readable_and_every_config_is_titled():
    plotted = page.main_ladder_rows(dataset.view(dataset.read()))
    svgs = hero_svgs()
    assert len(svgs) == 2
    for svg in svgs:
        sizes = [float(x) for x in re.findall(r'<text\b[^>]*font-size=\'([\d.]+)\'', svg)]
        assert sizes and min(sizes) >= 12
        assert svg.count('<title>') == len(plotted)


def test_pick_rows_match_the_winner_picks():
    ladder = re.search(r'<tbody><tr class="grp"><th colspan="6">Main ladder: 12 problems.*?</tbody>', HTML, re.S)[0]
    assert ladder.count('class="pickrow"') == len(dataset.WINNER_PICKS)
