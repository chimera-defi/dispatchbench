"""Runtime checks: the shipped page JavaScript, run under node (deep links need Playwright and Chrome, never skipped)."""
import glob
import json
import os
import re
import subprocess
from pathlib import Path

import pytest

from analysis import dataset, page

ROOT = Path(__file__).resolve().parents[1]


def node(*args, input=None, **kw):
    r = subprocess.run(['node', *args], input=input, text=True, capture_output=True, cwd=ROOT, **kw)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


def test_sortable_headers_keyboard():
    node('tests/sort_runtime.cjs')


def test_explorer_all_sets_views_prices_and_widths():
    ds = dataset.read()
    out = node('tests/pareto_runtime.cjs', input=json.dumps({'explorer': page.explorer_data(dataset.view(ds)), 'expected': ds['explorer']}))
    assert 'scenarios' in out


def test_any_pair_explorer_script_and_projection():
    s = dataset.view(dataset.read())
    data, html = page.any_pair_data(s), page.any_pair(s)
    assert '100 any-pair' in node('tests/any_pair_runtime.cjs', input=json.dumps({'data': data, 'html': html}))
    for row in data['points']:
        tokens = page.every(s)[row['c']]['tokens_mean']
        assert (row['inp'], row['rsn']) == (tokens['in_tok'], tokens['reasoning_tok'])


def test_deep_links_in_chrome():
    found = [os.environ.get('NODE_PATH', ''), str(ROOT / 'node_modules')]
    found += sorted(glob.glob(os.path.expanduser('~/.npm/_npx/*/node_modules')), key=os.path.getmtime, reverse=True)
    path = os.pathsep.join(d for d in found if d and (d == found[0] or os.path.isdir(os.path.join(d, 'playwright'))))
    out = node('tests/deeplink_runtime.cjs', timeout=300, env={**os.environ, 'NODE_PATH': path})
    assert 'deep links:' in out


@pytest.fixture(scope='module')
def cost_surfaces():
    harness = (ROOT / 'tests/pareto_runtime.cjs').read_text()
    marker = 'const h=context.harness,exp=payload.explorer'
    assert marker in harness, 'explorer runtime harness entry point changed'
    script = harness.split(marker, 1)[0] + r'''
const {st,render}=context.harness, exp=payload.explorer, samples=[];
for(const kind of ['measured','proxy','unmetered']){
 const row=exp.rows.find(r=>r.cost_kind===kind);
 assert(row, `missing ${kind} sample`);
 const set=exp.sets.find(s=>s.rows.includes(row.key));
 st.set=set.id; st.off=new Set(set.rows.filter(k=>k!==row.key)); st.sel=row.key;
 for(const quota of [false,true]){
  st.quota=quota;
  for(const view of Object.keys(exp.views)){
   if(kind==='unmetered'&&view!=='side')continue;
   st.view=view;render();
   const chart=element('ex-chart').innerHTML;
   const titles=Array.from(chart.matchAll(/<(?:g|path) class="[^"]*ex-point[^>]*>\s*<title>(.*?)<\/title>/gs),m=>m[1]);
   samples.push({kind,tooltip:titles,detail:element('ex-detail').innerHTML,chips:element('ex-chips').innerHTML});
  }
 }
}
console.log(JSON.stringify(samples));
'''
    samples = json.loads(node('-e', script, input=json.dumps({'explorer': page.explorer_data(dataset.view(dataset.read()))})))
    assert {s['kind'] for s in samples} == {'measured', 'proxy', 'unmetered'}
    assert all(s['tooltip'] for s in samples)
    return samples


@pytest.mark.parametrize('surface', ['tooltip', 'detail', 'chips'])
def test_every_explorer_cost_surface_labels_cost_kind(cost_surfaces, surface):
    labels = {'measured': r'\bmeasured\b', 'proxy': r'token[ -]estimate|estimated from tokens', 'unmetered': r'\bunmetered\b'}
    for sample in cost_surfaces:
        texts = sample[surface]
        for text in [texts] if isinstance(texts, str) else texts:
            assert re.search(labels[sample['kind']], text, re.I), (surface, sample['kind'], text)
