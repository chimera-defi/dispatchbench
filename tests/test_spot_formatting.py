"""P4f: verify rendered measurements against unrounded dataset evidence."""
import json
import re
import statistics
import subprocess
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

import pytest

from analysis import configs, dataset, page, report


class Measurements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tips, self.tables = [], []
        self.table = self.row = self.cell = None
        self.table_contexts = []
        self.section = None
        self.details = []
        self.summary = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section':
            self.section = attrs.get('id')
        if tag == 'details':
            self.details.append('')
        if tag == 'summary':
            self.summary = True
        if 'data-tip' in attrs:
            self.tips.append(attrs['data-tip'])
        if tag == 'table':
            self.table = []
            self.table_contexts.append((self.section, tuple(self.details)))
        if tag == 'tr':
            self.row = []
        if tag in ('td', 'th'):
            self.cell = []

    def handle_data(self, text):
        if self.summary:
            self.details[-1] += text
        if self.cell is not None:
            self.cell.append(text)

    def handle_endtag(self, tag):
        if tag == 'summary':
            self.summary = False
        if tag == 'details':
            self.details.pop()
        if tag in ('td', 'th') and self.cell is not None:
            self.row.append(''.join(self.cell).strip())
            self.cell = None
        if tag == 'tr' and self.row is not None:
            self.table.append(self.row)
            self.row = None
        if tag == 'table':
            self.tables.append(self.table)
            self.table = None


def test_raw_medians_retain_source_precision():
    """The added dataset evidence must actually be the raw source median."""
    groups = defaultdict(list)
    for source, config, set_, row in dataset._rows():
        groups[source, config, set_].append(row['sec'])
        if set_ in dataset.ALL_RUN_SETS:
            groups[source, config, 'all runs'].append(row['sec'])
    for row in dataset.read()['rows']:
        assert row['median_s_raw'] == statistics.median(groups[row['source'], row['config'], row['set']])


@pytest.mark.parametrize('raw,expected', [(39.44546416198136, '39.4'), (39.4501, '39.5')])
def test_tooltip_rounds_once_even_when_plot_values_are_equal(raw, expected):
    v = dict(passes=1, n=1, usd_per_pass=.001, cost_kind='measured',
             latency_s=dict(median=39.45, median_raw=raw))
    assert f'median {expected} s' in page.tip('haiku-low', v)


def test_page_tooltips_and_tables_format_dataset_measurements_once():
    ds = dataset.read()
    reader = Measurements()
    reader.feed(Path(report.PAGE).read_text())
    s = dataset.view(ds)
    sources = {**page.every(s), **s['grok']}
    checked = set()
    # All main/partial configurations, both price views and both earlier charts.
    for c, v in sources.items():
        name = configs.display(c)
        tips = [t for t in reader.tips if t.startswith((name + ':', name + ' [main ladder]:', name + ' (exploratory) [main ladder]:'))
                and re.search(r'\bmedian [\d.]+ s', t)]
        if tips:
            checked.add(c)
        for tip in tips:
            assert re.search(r'\bmedian ([\d.]+) s', tip)[1] == f'{dataset.median_seconds(v):.1f}', (c, tip)
            price = re.search(r'(\$[\d.,]+) per pass', tip)[1]
            assert price in {dataset.usd(v['usd_per_pass']), dataset.usd(v['claude_usd_per_pass'])}, (c, tip)
    assert checked == set(page.ORDER) | (set(s['grok']) - set(configs.CHART_HIDDEN))
    for c, name in page.NAME.items():
        v = ds['rescue'][c]
        tips = [t for t in reader.tips if t.startswith(name + ':') and 'Median ' in t]
        assert tips, c
        for tip in tips:
            assert re.search(r'Median ([\d.]+) s', tip)[1] == f'{v["median_s_raw"]:.1f}'
            price = re.search(r'(\$[\d.,]+) per pass', tip)[1]
            assert price in {dataset.usd(v['usd_per_pass']), dataset.usd(v['claude_usd_per_pass'])}
    # The primary table includes every full-ladder config (including Devin).
    result = next(t for t in reader.tables if t[0] == ['config', 'passed', '$ per pass', 'Claude $', 'median s', 'verdict'])
    for c in page.ORDER_ALL:
        v = sources.get(c) or page.devin(s)[c]
        if configs.low_context(c):
            continue
        row = next(r for r in result[1:] if r[0] == configs.display(c))
        assert row[1] == f"{100 * v['pass_at_1']:.0f}% ({v['passes']}/{v['n']})"
        assert row[2].lstrip('~') == dataset.usd(v['usd_per_pass'])
        assert row[4] == f'{dataset.median_seconds(v):.1f}'
    assert 'median 39.5 s' not in Path(report.PAGE).read_text()


def test_page_table_medians_match_exact_populations():
    ds = dataset.read()
    reader = Measurements()
    reader.feed(Path(report.PAGE).read_text())
    # A config has several distinct populations. Keep source/set in the lookup;
    # never accept another population's median just because the config matches.
    ladder = {r['display']: r for r in ds['rows']
              if r['source'] == 'main' and r['set'] in ('main ladder', 'partial ladder')}
    rescue = {page.SHORT(name): ds['rescue'][c] for c, name in page.HARD}
    schemas = {tuple(v['head']): key for key, v in ds['tables'].items()
               if isinstance(v, dict) and 'median s' in v['head']}
    fast_rows = dataset.summarize.function_rows()
    checked = set()
    catalog_seen = set()
    for table, (section, details) in zip(reader.tables, reader.table_contexts):
        if not table or 'median s' not in table[0]:
            continue
        head = table[0]
        col = head.index('median s')
        is_primary = head == ['config', 'passed', '$ per pass', 'Claude $', 'median s', 'verdict']
        is_catalog = head[0] == 'name'
        key = 'primary' if is_primary else 'catalog' if is_catalog else schemas[tuple(head)]
        checked.add(key)
        group = None
        if is_catalog:
            category = details[-1].split(':')[0]
            category = {'retest pipeline': 'rescue pipeline',
                        'Low context (prompt or tool text trimmed)': 'low context'}.get(category, category)
            candidates = [r for r in dataset.catalog_rows(ds) if r['category'] == category
                          and (r['config'] in configs.GROK_CONFIGS) == (section == 'grok')]
            catalog = {r['display']: r for r in candidates}
            assert len(catalog) == len(candidates), (section, category, candidates)
            seen = set()
        for row in table[1:]:
            if len(row) == 1:
                # The primary table repeats names in separate ladder/retest groups.
                assert is_primary, (key, row)
                group = row[0].split(':')[0]
                continue
            assert len(row) == len(head), (key, row)
            name = row[0].removesuffix(' †')
            population = key
            precision = 1
            if is_catalog:
                v = catalog[name]
                raw = v['median_s_raw']
                population = (v['source'], v['config'], v['set'])
                seen.add(name)
                catalog_seen.add(population)
            elif is_primary:
                if group == 'Retest set':
                    evidence = rescue[name]['metrics_from']
                    v = dataset.get(ds, evidence['config'], evidence['set'], evidence['source'])
                else:
                    assert group in ('Main ladder', 'Devin'), group
                    v = ladder[name]
                raw = v['median_s_raw']
                population = (v['source'], v['config'], v['set'])
            elif key in ('grok_full_reach', 'grok_full_lanes', 'grok_reach', 'grok_equivalent_all'):
                population = 'grok_comparison' if key.startswith('grok_full') else 'grok_first'
                lane = row[head.index('comparable lane')] if 'comparable lane' in head else name
                metrics = {configs.display(c): v for c, v in ds[population]['metrics'].items()}
                raw = metrics[lane]['median_s']  # These metrics retain unrounded medians.
            elif key == 'fastmode':
                labels = {dataset.FM_LABEL[c].format(lo=min(v['repeats']), hi=max(v['repeats'])): c
                          for c, v in ds['report']['fastmode'].items()}
                c = labels[name]
                attempts = [r['wall_s'] for r in fast_rows if r['config'] == c and r['phase'] == 'fastmode']
                assert len(attempts) == ds['report']['fastmode'][c]['n']
                raw = statistics.median(attempts)
                population = ('main', c, 'fastmode')
            elif key in ('equiv', 'equiv_back', 'equiv_all'):
                raw = [ladder[lane]['median_s_raw'] for lane in name.split(' → ')]
                precision = 0
            else:
                # Fail on new table types until their source population is explicit.
                pytest.fail(f'Unmapped median table: {key}')
            values = raw if isinstance(raw, list) else [raw]
            expected = ' → '.join(f'{v:.{precision}f}' for v in values)
            assert row[col] == expected, (key, name, population, row[col], expected)
        if is_catalog:
            assert seen == set(catalog), (section, category, seen, set(catalog))
    assert checked == {'primary', 'catalog', 'grok_full_reach', 'grok_full_lanes',
                       'grok_reach', 'grok_equivalent_all', 'fastmode', 'equiv_all'}
    assert catalog_seen == {(r['source'], r['config'], r['set']) for r in dataset.catalog_rows(ds)}


def test_harness_repeat_cap_fact_has_primary_provenance():
    ds = json.loads(Path(dataset.PATH).read_text())
    fact = ds['facts']['hb_repeat_cap_lines']
    assert fact['value'] == 2 and fact['display'] == 'two' and fact['unit'] == 'count'
    patch = subprocess.check_output(['git', 'show', '--format=', fact['source'], '--', 'bench/codex_harness.py'], text=True)
    added = [line for line in patch.splitlines() if line.startswith('+') and not line.startswith('+++')]
    removed = [line for line in patch.splitlines() if line.startswith('-') and not line.startswith('---')]
    assert len(added) == len(removed) == fact['value']
    html = Path(report.PAGE).read_text()
    assert 'a two-line change' in html and fact['source'] in html
    assert 'designed and wrote it in five turns' not in html
