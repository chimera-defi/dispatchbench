"""The agentic grader must not let a candidate skip, xfail or remove hidden tests."""
import shutil

import pytest

from bench.agentic import run as A


@pytest.fixture
def task(tmp_path):
    t = tmp_path / 't1'; repo = t / 'repo'
    (repo / 'tests').mkdir(parents=True); (t / 'hidden').mkdir()
    (repo / 'thing.py').write_text('VALUE = False\n')
    (t / 'hidden/test_hidden.py').write_text('from thing import VALUE\ndef test_hidden(): assert VALUE\n')
    return t


@pytest.mark.parametrize('marker', ["skip(reason='skip')", "xfail(reason='xfail')", "xfail(reason='xpass')"])
def test_hidden_skip_and_xfail_are_not_passes(task, marker):
    h = task / 'hidden/test_hidden.py'
    h.write_text('import pytest\n@pytest.mark.' + marker + '\ndef test_hidden(): assert ' + ('True' if 'xpass' in marker else 'False') + '\n')
    result = A.hidden_pytest(str(task / 'repo'), str(task / 'repo'), str(h))
    assert result['ok'] is False and result['expected_ids'] == ['test_hidden.py::test_hidden']


def test_candidate_cannot_remove_expected_hidden_ids(task):
    (task / 'hidden/test_hidden.py').write_text('from thing import VALUE\nif VALUE:\n def test_hidden(): assert True\n')
    (task / 'repo/thing.py').write_text('VALUE = True\n')
    candidate = task.parent / 'candidate'; candidate.mkdir()
    (candidate / 'thing.py').write_text('VALUE = False\n')
    result = A.hidden_pytest(str(candidate), str(task / 'repo'), str(task / 'hidden/test_hidden.py'))
    assert result['ok'] is False and result['collected_ids'] == []
