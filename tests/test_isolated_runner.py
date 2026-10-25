import collections
import json

import pytest

from bench import isolated, run
from analysis import summarize






def test_parity_detects_bare_and_effort_drift(monkeypatch):
    row = next(r for r in isolated.plans()['function'] if r['config'] == 'luna-low-bare')
    assert isolated.parity('function', [row], emit=False)
    monkeypatch.setitem(run.TRIM_LEVEL, 'luna-low-bare', 'base')
    assert not isolated.parity('function', [row], emit=False)
    monkeypatch.setitem(run.TRIM_LEVEL, 'luna-low-bare', 'noshell')
    monkeypatch.setitem(run.CONFIGS, 'luna-low-bare', ('codex', 'gpt-6-luna', 'high'))
    assert not isolated.parity('function', [row], emit=False)
    monkeypatch.setitem(run.CONFIGS, 'luna-low-bare', ('codex', 'gpt-6.1-sol', 'low'))
    assert not isolated.parity('function', [row], emit=False)


def test_call_budget_bounds_nested_pipeline_calls():
    seen = []
    budget = isolated.CallBudget(2)
    call = budget.wrap(lambda name: seen.append(name))
    call('plan'); call('build')
    with pytest.raises(isolated.CallLimit):
        call('repair')
    assert seen == ['plan', 'build']






