import collections

from analysis import dataset, summarize


def test_isolated_cells_replace_old_rows_everywhere():
    summary, _, _ = summarize.build()
    assert summary['configs']['luna-low']['passes'] == 44
    rows = dataset._rows()
    for source, config, set_, filename, attempts in (
        ('main', 'luna-low', 'main ladder', '2026-10-25-isolated-main.jsonl', 60),
        ('main', 'sol61-high', 'L7 set', '2026-10-25-isolated-hard.jsonl', 15),
        *(( 'agentic', c, 'repo tasks', '2026-10-25-isolated-agentic.jsonl', 12)
          for c in ('luna-low', 'sol61-medium', 'sol61-high', 'astra-medium')),
    ):
        selected = [r for src, c, st, r in rows if (src, c, st) == (source, config, set_)]
        raw = [r for r in summarize.load('results/' + filename) if r['config'] == config]
        assert len(selected) == len(raw) == attempts
        assert sum(r['ok'] for r in selected) == sum(r.get('passed', r.get('hidden_pass')) for r in raw)
        assert sum(r['sec'] for r in selected) == sum(r['wall_s'] for r in raw)
        assert sum(r['in'] for r in selected) == sum(r['in_tok'] for r in raw)
        assert sum(r['usd'] for r in selected) == sum(summarize.cost(r) for r in raw)


def test_isolated_selection_preserves_unreplaced_cells():
    old = summarize.load(summarize.FUNC)
    selected = summarize.function_rows()
    retained = lambda rows: collections.Counter(r['key'] for r in rows
        if (r['config'], r['phase']) not in {('luna-low', 'main'), ('sol61-high', 'hard')})
    assert retained(old) == retained(selected)


def test_isolated_selection_rejects_incomplete_replacement(monkeypatch):
    import pytest
    original = summarize.load
    monkeypatch.setattr(summarize, 'load', lambda path: original(path)[:-1]
        if str(path).endswith('2026-10-25-isolated-main.jsonl') else original(path))
    with pytest.raises(AssertionError, match='replacement coverage'):
        summarize.function_rows()
