"""Colour tokens: no literals outside the token block, family colours distinct, text contrast."""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from analysis import report
from tools import check_contrast as contrast

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_colours', ROOT / 'tools/check_colours.py')
colours = importlib.util.module_from_spec(spec)
spec.loader.exec_module(colours)


@pytest.mark.parametrize('mode', ['light', 'dark'])
@pytest.mark.parametrize('automatic', [False, True])
def test_family_tokens_are_pairwise_distinct(mode, automatic):
    values = contrast.theme_values((ROOT / 'docs/page/tokens.css').read_text(), mode, automatic=automatic)
    tokens = ('claude', 'sonnet', 'codex', 'codex56', 'grok', 'devin', 'hetzner', 'pipeline')
    resolved = [contrast.rgb('--' + t, values, None) for t in tokens]
    assert len(set(resolved)) == len(tokens), dict(zip(tokens, resolved))


@pytest.mark.parametrize('value', ['#abc', '#12345678', 'rgba(1,2,3,.4)', 'hsl(20 30% 40%)', 'oklch(.5 .1 20)', 'maroon'])
def test_literals_rejected(tmp_path, value):
    for name, body in [('page.css', f'.x{{color:{value}}}'), ('t.html', f'<p style="color:{value}">c</p>'),
                       ('c.svg', f'<svg><path fill="{value}"/></svg>')]:
        path = tmp_path / name
        path.write_text(body)
        assert colours.check_file(path), (name, value)


def test_checker_cli_fails_for_injected_template(tmp_path):
    template = tmp_path / 'template.html'
    template.write_text('<style>.injected{color:#123456}</style>')
    run = subprocess.run([sys.executable, str(ROOT / 'tools/check_colours.py'), str(template)], capture_output=True, text=True)
    assert run.returncode == 1 and '#123456' in run.stdout


def test_real_page_has_no_colour_literals_outside_tokens(tmp_path):
    assert not colours.check([ROOT / 'docs/page'])
    path = tmp_path / 'page.html'
    path.write_text(report.render()[2])
    assert not colours.check_file(path)


def test_accessibility_pairs_meet_contrast():
    css = (ROOT / 'docs/page/tokens.css').read_text()
    results = list(contrast.check(css))
    assert len(results) == 24
    for name, ratio, minimum in results:
        assert ratio >= minimum, (name, ratio, minimum)
    broken = css.replace('--color-input-ink:#000000', '--color-input-ink:var(--color-text)')
    assert any(ratio < minimum for _, ratio, minimum in contrast.check(broken))
