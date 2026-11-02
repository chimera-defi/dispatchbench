"""Priority findings must not dilute the main ladder or the Winner contract."""
import pytest
from analysis import configs, dataset, page, summarize, terra_priority


def test_only_priority_function_rows_join_main_ladder():
    rows = summarize.function_rows()
    for c, passes in (("terra61-low-fast", 60), ("terra61-high-fast", 58)):
        rr = [r for r in rows if r['config'] == c and r['rung'] != 7]
        assert len(rr) == 60 and sum(r['passed'] for r in rr) == passes
        assert {r['repeat'] for r in rr} == set(range(1, 6))
        assert {r['rung'] for r in rr} == set(range(1, 7))
        assert all(r['_file'] == 'results/' + terra_priority.FAST_FN for r in rr)
        assert all(summarize.fast_mult(r) == 2 for r in rr)
        assert sum(summarize.cost(r) for r in rr) == pytest.approx(2 * sum(summarize.list_cost(r) for r in rr))
    l7 = [r for r in rows if r['_file'] == 'results/' + terra_priority.L7_FAST_FN]
    assert len(l7) == 15 and sum(r['passed'] for r in l7) == 14
    assert {r['problem'] for r in l7 if not r['passed']} == {'p15_paint_erase'}
    assert all(r['config'] == 'terra61-low-fast' and r['rung'] == 7 and summarize.fast_mult(r) == 2 for r in l7)
    assert not any('terra-noise' in r['_file'] or 'terra-followup' in r['_file'] for r in rows)
    assert all(not r['config'].startswith('terra') for r in summarize.agentic_rows())


def test_priority_facts_and_winner_keep_their_distinct_scopes():
    ds = dataset.read()
    F = ds['facts']
    assert F['fastest_nomiss'] == 'terra61-low ⚡' and F['fastest_nomiss_med'] == '6.0'
    assert dataset.WINNER_PICKS['sol61-high-fast'] == 'default'
    html = page.winner_table(ds, dataset.need)
    assert 'terra61-low ⚡ is faster (6.0 s) and ~3× cheaper; 1 L7 miss per tier, both p15' in html
    assert '179/180 vs high 177/180' in F['terra_priority_noise']
    assert '-1.6 to +4.3' in F['terra_priority_noise']
    assert '-14.5 to +8.7' in F['terra_priority_p04']
    for c in ('terra61-low-fast', 'terra61-high-fast'):
        assert (c[:-5], c) in page.FAST_PAIRS
        assert configs.display(c) == c[:-5] + ' ⚡'
        assert not any(r['config'] == c and r['set'] == 'repo tasks' for r in ds['rows'])
        assert any(r['config'] == c and r['set'] == 'L7 set' for r in ds['rows']) == (c == 'terra61-low-fast')
