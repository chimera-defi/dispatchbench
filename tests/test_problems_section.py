"""R4: the visible problem catalogue keeps sources and real statements."""
from html import unescape
import importlib
from pathlib import Path
import re
from analysis import dataset, page

ROOT = Path(__file__).resolve().parents[1]


def test_problems_are_visible_and_have_original_statements():
    html = (ROOT / 'results/report/page.html').read_text()
    assert '<a href="#problems">' in html.split('</nav>', 1)[0]
    sec = re.search(r'<section id="problems">(.*?)</section>', html, re.S)[1]
    assert html.index('id="results"') < html.index('id="problems"') < html.index('id="grok"')
    assert 'Problems: try them yourself' in sec
    main, hard, *_ = page.set_definitions(dataset.view(dataset.read()))
    for pid in main + hard:
        module = importlib.import_module('bench.problems.' + pid)
        problem = re.search(r'<li class="prow" id="' + pid.split('_', 1)[0] + r'">(.*?)</details>', sec, re.S)[1]
        statement = re.search(r'<pre class="problem-statement"><code>(.*?)</code></pre>', problem, re.S)[1]
        assert unescape(statement) == module.STATEMENT
        assert unescape(re.search(r'<pre class="problem-signature"><code>(.*?)</code></pre>', problem, re.S)[1]) == module.SIGNATURE
        assert 'reference solution (spoiler)' in problem
    pilot = sec.split('<b>Pilot</b>', 1)[1].split('<li class="round">', 1)[0]
    assert pilot.count('https://leetcode.com/problems/') == 6
    # Every problem name and analogue remains outside its Try it disclosure.
    assert sec.index('<li class="prow"') < sec.index('<summary>Try it</summary>')
