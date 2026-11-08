"""Single source of truth: dataset.json, its manifest, raw run index, and the numbers on the page."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest

from analysis import audit, configs, dataset, page, raw_runs, report, summarize

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / 'analysis'
HTML = (ROOT / 'results/report/page.html').read_text()
# Modules that may open results/*.jsonl, and the renderers that may only read dataset.json.
RENDERERS = {'page.py', 'charts.py', 'report.py', 'grok.py', 'raw_runs.py', 'audit.py', 'og.py', 'labels.py'}
PATHLIKE = re.compile(r'[\w\-/]\.jsonl\b|summary\.json\b')


@pytest.fixture(scope='module')
def ds():
    return json.loads(dataset.PATH.read_text()) if hasattr(dataset.PATH, 'read_text') else json.load(open(dataset.PATH))


def test_renderers_never_name_a_jsonl_or_summary_json():
    import ast
    bad = []
    for name in sorted(RENDERERS):
        for n in ast.walk(ast.parse((ANALYSIS / name).read_text())):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and PATHLIKE.search(n.value):
                bad.append(f'{name}:{n.lineno}')
    assert not bad
    assert not (ROOT / 'results/summary.json').exists()


def test_cached_dataset_current_and_keys_unique():
    built = dataset.build()
    assert open(dataset.PATH).read() == dataset.text(built)
    keys = [(r['config'], r['set']) for r in built['rows']]
    assert len(keys) == len(set(keys))
    assert configs.check_registry(dataset.keys(built)) == []
    by = {(r['source'], r['config']): r for r in dataset.catalog_rows(built)}
    assert set(by) == set(configs.REGISTRY)
    for source, name, passes, n in (('main', 'haiku-high', 75, 75), ('agentic', 'haiku-high', 12, 12), ('main', 'sonnet-medium', 85, 85)):
        assert (by[source, name]['passes'], by[source, name]['n']) == (passes, n)


def test_generated_from_lists_every_jsonl_with_hash_and_rows(ds):
    on_disk = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / 'results').rglob('*.jsonl'))
    assert [g['path'] for g in ds['generated_from']] == on_disk
    for g in ds['generated_from']:
        path = ROOT / g['path']
        assert g['sha256'] == hashlib.sha256(path.read_bytes()).hexdigest(), g['path']
        assert g['rows'] == sum(1 for line in path.read_text().splitlines() if line.strip()), g['path']


def test_manifest_is_independent_of_head_and_matches_published(monkeypatch):
    summary, _, expected = summarize.build()
    rows, agent = summarize.function_rows(), summarize.agentic_rows()
    manifests = []
    for sha in ('a' * 40, 'b' * 40):
        monkeypatch.setattr(subprocess, 'check_output', lambda *a, **kw: sha)
        manifests.append(summarize.manifest(rows, agent, summary))
    assert 'git_sha' not in expected and manifests[0] == manifests[1] == expected
    assert json.loads((ROOT / 'results/manifest.json').read_text()) == expected


def test_raw_run_index_hash_is_current():
    assert raw_runs.OUTPUT.read_text() == raw_runs.render()
    text = (ROOT / 'docs/RAW_RUNS.md').read_text()
    command = text.split('```bash\n', 1)[1].split('\n```', 1)[0]
    out = subprocess.run(['bash', '-o', 'pipefail', '-c', command], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert out.split()[0] == raw_runs.directory_hash('cache/calls')[1]


def test_every_fact_has_value_unit_display_source(ds):
    for k, f in ds['facts'].items():
        assert set(f) == {'value', 'unit', 'display', 'source'} and f['source'], k


def test_page_embeds_data_block_and_every_visible_number_is_in_it():
    block = audit.DATA_BLOCK.search(HTML)
    assert block and {'facts', 'numbers', 'explorer', 'any_pair'} <= set(json.loads(block.group(1)))
    allow = json.loads((ROOT / 'docs/audit_allow.json').read_text())
    assert audit.page_numbers_missing(HTML, allow) == []
    assert audit.page_numbers_missing(HTML.replace('<main>', '<main><p>It took 98765 s</p>', 1), allow)
    assert 'JSON.parse(document.getElementById("data").textContent).explorer' in HTML
    assert '__DATA__' not in HTML


def test_page_javascript_does_no_aggregation_over_rows():
    for js in re.findall(r'<script(?![^>]*application/json)[^>]*>(.*?)</script>', HTML, re.S):
        js = re.sub(r'\.reduce\(function\(s,q\)\{return s\+overlap\([^;]*?\)\}\s*,\s*0\)', '', js)
        assert '.reduce(' not in js and not re.search(r'/\s*[\w.\]\[]+\.length\b|\.length\s*\)?\s*/', js)


def test_stray_number_in_template_is_caught(tmp_path):
    allow = json.loads((ROOT / 'docs/audit_allow.json').read_text())
    for name in ('report.tmpl.md', 'page.tmpl.md', 'readme.tmpl.md'):
        copy = tmp_path / name
        copy.write_text((ROOT / 'docs' / name).read_text() + '\nThe run cost 17 dollars.\n')
        stray, _ = audit.stray_literals(audit.template_literals([str(copy)]), allow)
        assert any("literal '17'" in s for s in stray), name


def test_renderers_read_only_dataset_json(monkeypatch):
    import builtins, io
    from analysis import charts
    reads = []

    def guard(original):
        def opened(path, mode='r', *a, **kw):
            if isinstance(path, (str, bytes, Path)) and not any(c in mode for c in 'wax+'):
                resolved = Path(path).resolve()
                if resolved.is_relative_to(ROOT / 'results'):
                    assert resolved == Path(dataset.PATH), f'renderer read {resolved}'
                    reads.append(resolved)
            return original(path, mode, *a, **kw)
        return opened
    monkeypatch.setattr(builtins, 'open', guard(builtins.open))
    monkeypatch.setattr(io, 'open', guard(io.open))
    charts.build(); report.render()
    assert len(reads) == 2


def test_raw_medians_retain_source_precision():
    import statistics
    from collections import defaultdict
    groups = defaultdict(list)
    for source, config, set_, row in dataset._rows():
        groups[source, config, set_].append(row['sec'])
        if set_ in dataset.ALL_RUN_SETS:
            groups[source, config, 'all runs'].append(row['sec'])
    for row in dataset.read()['rows']:
        assert row['median_s_raw'] == statistics.median(groups[row['source'], row['config'], row['set']])


@pytest.mark.parametrize('raw,expected', [(39.44546416198136, '39.4'), (39.4501, '39.5')])
def test_tooltip_rounds_once(raw, expected):
    v = dict(passes=1, n=1, usd_per_pass=.001, cost_kind='measured', latency_s=dict(median=39.45, median_raw=raw))
    assert f'median {expected} s' in page.tip('haiku-low', v)
