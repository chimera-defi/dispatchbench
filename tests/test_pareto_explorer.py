"""Data coverage and frontier contracts for the v6 explorer."""
import copy
import pytest
from analysis import dataset, page


@pytest.fixture(scope="module")
def ds():
    return dataset.read()


def test_every_dataset_row_is_in_explorer(ds):
    exp = ds['explorer']
    have = {(r['source'], r['config'], r['set']) for r in exp['rows']}
    assert {(r['source'], r['config'], r['set']) for r in ds['rows']} <= have
    assert {r['set'] for r in ds['rows']} <= {s['id'] for s in exp['sets']}
    assert all(r['key'] in {k for s in exp['sets'] for k in s['rows']} for r in exp['rows'])
    assert all(r['model_short'] == 'devin' for r in exp['rows'] if r['family'] == 'Devin')
    assert all(r['mode'] in ('normal', 'fast', 'bare', 'pipeline') and r['effort'] and r['model_short'] for r in exp['rows'])
    for r in exp['rows']:
        if r['cost_kind'] != 'unmetered' and r['usd_per_pass'] is not None:
            assert r['quota_usd_per_pass'] == pytest.approx(r['usd_per_pass'] - r['codex_usd_per_pass'], abs=1e-6)
    pilot = next(r for r in exp['rows'] if r['config'] == 'luna-low' and r['set'] == 'pilot')
    assert pilot['mode'] == 'fast' and pilot['fast_twin'] == 'luna-low-defa'
    assert next(r for r in exp['rows'] if r['config'] == 'luna/noshell')['bare_of'] == 'luna/base'
    assert next(r for r in exp['rows'] if r['config'] == 'haiku-low-plan+luna-low')['generation'] == '6.x'
    for c in ('sol61-high-fast', 'astra-medium-fast'):

        r = next(r for r in exp['rows'] if r['config'] == c + '+haiku-on-fail')
        assert r['derived'] and r['mode'] == 'pipeline'
    repo = [r for r in exp['rows'] if r['set'] == 'repo tasks' and r['source'] == 'grok-repo']
    assert {r['config'] for r in repo} == {'grok47-low', 'grok47-high'}
    assert all(r['task_complete'] == r['hidden_pass'] == r['passes'] == r['n'] and r['quota_usd_per_pass'] == r['usd_per_pass'] for r in repo)
    r = dataset.get(ds, 'luna-low', 'repo tasks', 'agentic')
    assert r['complete_marker'] == '7/12 complete (12/12 hidden)'


def test_fixture_config_appears_without_page_edit(ds):
    changed = copy.deepcopy(ds)
    row = dict(changed['rows'][0], id='fixture/new-high', config='new-high')
    changed['rows'].append(row)
    exp = dataset.explorer_data(changed)
    assert any(r['config'] == 'new-high' for r in exp['rows'])
    assert row['id'] + '@' + row['set'] in next(s for s in exp['sets'] if s['id'] == row['set'])['rows']
    changed['rows'] = [r for r in changed['rows'] if r['set'] != 'trim probe']
    empty = next(s for s in dataset.explorer_data(changed)['sets'] if s['id'] == 'trim probe')
    assert empty['rows'] == [] and empty['empty_reason'] == 'No recorded attempts for this problem set.'


def test_strict_frontier_and_legacy_cross_check(ds):
    exp = ds['explorer']; by_key = {r['key']: r for r in exp['rows']}
    # Compare the historical eligible population with the earlier page. New
    # explorer sets include partial probes too; those intentionally differ.
    s = dataset.view(ds)
    pts = page.ladder_points(s, False, 'pass', 'main')
    legacy = {p['c'] for p in dataset.front([p for p in pts if not p.get('partial')], lambda a,b: a['x'] <= b['x'] and a['y'] >= b['y'])}
    assert legacy == set(page.pass_cost(s, free=False)[1])
    main = next(st for st in exp['sets'] if st['id'] == 'main')
    front = {by_key[k]['config'] for k,v in main['views']['list']['front']['membership'].items() if v['on_frontier']}
    assert front == {'haiku-low', 'haiku-medium', 'luna-medium', 'haiku-high', 'luna-high', 'luna-low-bare'}
    assert {by_key[k]['config'] for k,v in main['views']['list']['top']['membership'].items() if v['on_frontier']} == {'haiku-low', 'luna-high', 'astra-medium-fast'}
    assert {by_key[k]['config'] for k,v in main['views']['quota']['top']['membership'].items() if v['on_frontier']} == {'astra-medium-fast'}
    high = dataset.explorer_frontier([by_key[k] for k in main['rows']], '3d', floor=1)
    assert {by_key[k]['config'] for k,v in high.items() if v['on_frontier']} == {'sonnet-medium', 'haiku-high', 'terra61-low', 'astra-medium-fast'}
    for st in exp['sets']:
        rr = [by_key[k] for k in st['rows']]
        for price in ('list', 'quota'):
            for view in exp['views']:
                assert st['views'][price][view]['membership'] == dataset.explorer_frontier(rr, view, price == 'quota')
    a = dict(cost=1, pass_rate=1, median_s=10)
    b = dict(cost=2, pass_rate=1, median_s=9.9)
    assert not dataset.strict_dominates(a,b,exp['views']['top']['objectives'])
    assert not dataset.strict_dominates(a,a,exp['views']['3d']['objectives'])
    devin = next(r for r in exp['rows'] if r['config'].startswith('devin') and r['set'] == 'partial ladder')
    assert not main['views']['list']['front']['membership'][devin['key']]['eligible']
    assert main['views']['list']['side']['membership'][devin['key']]['eligible']


# Preserve the earlier plots independently of the v6 rendering and filtering.
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


class EarlierCharts(HTMLParser):
    VOID = {'input', 'meta', 'link', 'br', 'hr', 'img', 'wbr'}

    def __init__(self):
        super().__init__(); self.stack=[]; self.charts={}; self.capture=None

    def handle_starttag(self, tag, attrs):
        a=dict(attrs); frame={'tag':tag,'attrs':a}
        if tag not in self.VOID: self.stack.append(frame)
        if not any(f['tag']=='section' and f['attrs'].get('id')=='pareto' for f in self.stack): return
        variant=next((f for f in reversed(self.stack) if 'cvariant' in f['attrs'].get('class','').split()),None)
        if variant is None: return
        if tag=='path' and a.get('data-front'):
            set_=next(f['attrs']['class'].split('s-')[1] for f in reversed(self.stack) if 'cset' in f['attrs'].get('class','').split())
            price=variant['attrs']['class'].split('v-')[1]
            key=(a['data-front'],set_,price)
            obj={'points':[],'labels':[],'key_labels':[]}
            self.charts[key]=obj; variant['chart']=obj
        obj=variant.get('chart')
        if obj is None: return
        if tag=='g' and 'pt' in a.get('class','').split(): obj['points'].append((a['data-c'],a['data-v']))
        if tag=='text' and 'lbl' in a.get('class','').split(): self.capture=(tag,len(self.stack),obj['labels'],[])
        if tag=='span' and a.get('class')=='n': self.capture=(tag,len(self.stack),obj['key_labels'],[])

    def handle_data(self,data):
        if self.capture: self.capture[3].append(data)

    def handle_endtag(self,tag):
        if self.capture and tag==self.capture[0] and len(self.stack)==self.capture[1]:
            self.capture[2].append(''.join(self.capture[3])); self.capture=None
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i]['tag']==tag: del self.stack[i:];break


def earlier_counts(html):
    p=EarlierCharts();p.feed(html);return p.charts


def test_earlier_points_and_labels_match_main_3561692():
    before=earlier_counts(subprocess.check_output(['git','show','3561692:results/report/page.html'],text=True))
    after=earlier_counts((ROOT/'results/report/page.html').read_text())
    assert len(before)==len(after)==8
    assert before.keys()==after.keys()
    for key in before:
        for field in ('points','labels','key_labels'):
            assert Counter(before[key][field])==Counter(after[key][field]), (key,field)


def test_explorer_is_prerendered_and_earlier_charts_remain_in_pareto(ds):
    html=(ROOT/'results/report/page.html').read_text()
    section=html.split('<section id="pareto">',1)[1].split('</section>',1)[0]
    assert section.index('id="pareto-explorer"')<section.index('<summary>Earlier charts</summary>')
    assert 'class="ex-svg"' in section and 'class="ex-point"' in section
    assert all(label in section for label in ('Parallel coordinates','Radar per config','By model','Configs in this set','Best trade-offs'))
    assert 'const MAIN' not in html and 'const RETEST' not in html and 'const PICKS' not in html
    assert '7/12 complete (12/12 hidden)' in html
    for s in ds['explorer']['sets']:
        assert f'<option value="{s["id"]}"' in section


def test_css_colours_live_only_in_swappable_token_block():
    import re
    css=(ROOT/'docs/page/tokens.css').read_text()
    assert css.count('/* FABLE TOKENS BEGIN')==css.count('/* FABLE TOKENS END */')==1
    rest=css.split('/* FABLE TOKENS END */',1)[1]+(ROOT/'docs/page/style.css').read_text()
    assert not re.search(r'#[0-9a-fA-F]{3,8}\b|\brgba?\(',rest)
    assert '--color-accent-300:#fec2c5' in css
    assert '--data-grok:#8fc7c0' in css
    assert ':root[data-theme="dark"]' in css and 'color-scheme:light dark' in css


def test_shipped_javascript_all_sets_views_prices_and_widths(ds):
    import json
    r=subprocess.run(['node','tests/pareto_runtime.cjs'],input=json.dumps({'explorer':page.explorer_data(dataset.view(ds)), 'expected':ds['explorer']}),text=True,capture_output=True,cwd=ROOT)
    assert r.returncode==0,r.stdout+r.stderr
    assert 'scenarios' in r.stdout
