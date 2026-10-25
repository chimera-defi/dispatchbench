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
    # The stopped comparison must not replace any additional cells, even complete ones.
    for selected, original in (
        (summarize.function_rows(), summarize._sourced(summarize.FUNC)),
        (summarize.rescue_rows(), summarize.load('results/appendix/luna_rescue.jsonl')),
        (summarize.harness_rows(), summarize.load('results/appendix/harness_bias.jsonl')),
    ):
        retained = [r for r in selected if r.get('codex_home') != 'isolated']
        replaced = {(r['config'], r.get('phase')) for r in selected if r.get('codex_home') == 'isolated'}
        assert retained == [r for r in original if (r['config'], r.get('phase')) not in replaced]






def test_generic_selection_prefers_function_cells_and_tracks(monkeypatch):
    original = summarize.load
    function = [dict(r, codex_home='isolated', wall_s=123.0)
                for r in original(summarize.FUNC)
                if (r['config'], r['phase']) == ('astra-medium-fast', 'hard')]
    rescue = [dict(r, codex_home='isolated', wall_s=234.0)
              for r in original('results/appendix/luna_rescue.jsonl') if r['arm'] == 'F']
    harness = [dict(r, codex_home='isolated', wall_s=345.0)
               for r in original('results/appendix/harness_bias.jsonl')
               if r['config'] == 'luna-low' and r['harness'] == 'claude-one-shot']
    overrides = {'function': function, 'rescue': rescue, 'harness_bias': harness}
    def loaded(path):
        for track, rows in overrides.items():
            if str(path).endswith(f'2026-10-25-isolated-{track}.jsonl'): return rows
        return original(path)
    monkeypatch.setattr(summarize, 'load', loaded)
    selected = summarize.selected_rows(summarize._sourced(summarize.FUNC), ('function',),
                                       ('config', 'phase'), ('problem', 'repeat'))
    assert sum(r['wall_s'] == 123.0 for r in selected) == 15
    assert len(selected) == len(original(summarize.FUNC))
    selected_rescue = summarize.selected_rows(original('results/appendix/luna_rescue.jsonl'), ('rescue',),
                                              ('config', 'arm'), ('problem', 'repeat'))
    assert len(selected_rescue) == len(original('results/appendix/luna_rescue.jsonl'))
    assert sum(r['wall_s'] == 234.0 for r in selected_rescue) == 70
    selected_bias = summarize.selected_rows(original('results/appendix/harness_bias.jsonl'), ('harness_bias',),
                                            ('config', 'phase', 'harness'), ('problem', 'repeat'))
    assert sum(r['wall_s'] == 345.0 for r in selected_bias) == 60
    table = dataset._rows()
    assert not any(r['sec'] == 234.0 for src, c, st, r in table if src == 'rescue')
    assert not any(r['sec'] == 345.0 for src, c, st, r in table if src == 'harness-bias')
    from analysis import luna_rescue
    assert luna_rescue.arms()['haiku-low-plan+luna-low']['median_s'] != 234.0


def test_generic_selection_rejects_wrong_identity_or_incomplete_cell(monkeypatch):
    import pytest
    original = summarize.load
    cell = [dict(r, codex_home='isolated') for r in original(summarize.FUNC)
            if (r['config'], r['phase']) == ('astra-medium-fast', 'hard')]
    monkeypatch.setattr(summarize, 'load', lambda path: cell
                        if str(path).endswith('isolated-function.jsonl') else original(path))
    select = lambda: summarize.selected_rows(summarize._sourced(summarize.FUNC), ('function',),
                                             ('config', 'phase'), ('problem', 'repeat'))
    select()
    cell.pop()
    with pytest.raises(AssertionError, match='replacement coverage'):
        select()
    cell.clear()
    cell.append(dict(config='invented', phase='main', problem='p01', repeat=1, cli='codex', codex_home='isolated'))
    with pytest.raises(AssertionError, match='replacement coverage'):
        select()
