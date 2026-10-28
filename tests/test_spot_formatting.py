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

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-tip' in attrs:
            self.tips.append(attrs['data-tip'])
        if tag == 'table':
            self.table = []
        if tag == 'tr':
            self.row = []
        if tag in ('td', 'th'):
            self.cell = []

    def handle_data(self, text):
        if self.cell is not None:
            self.cell.append(text)

    def handle_endtag(self, tag):
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
    # Sweep every median column, including partial, hard, repo, pipeline and catalog
    # rows. Each value must match a raw median for that named config/population.
    expected = defaultdict(set)
    for r in ds['rows']:
        for name in (r['config'], r['display']):
            expected[name].add(f"{r['median_s_raw']:.1f}")
    # Same-problem comparison tables and the historical Grok population carry raw
    # medians under their own explicit metrics; they are separate populations.
    for key in ('grok_first', 'grok_comparison'):
        for c, v in ds[key]['metrics'].items():
            expected[c].add(f"{v['median_s']:.1f}")
            expected[configs.display(c)].add(f"{v['median_s']:.1f}")
    seen = set()
    for table in reader.tables:
        if not table or 'median s' not in table[0]:
            continue
        col = table[0].index('median s')
        name_col = table[0].index('comparable lane') if 'comparable lane' in table[0] else 0
        for row in table[1:]:
            if len(row) <= col:
                continue
            name = row[name_col].removesuffix(' †')
            if name in expected:
                assert row[col] in expected[name], (name, row[col], expected[name])
                seen.add(name)
    assert all(configs.display(c) in seen or c in seen for c in sources)
    assert 'median 39.5 s' not in Path(report.PAGE).read_text()


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
