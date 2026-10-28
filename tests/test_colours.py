"""Check the actual report and reject literal colours in all authoring forms."""
import importlib.util
import re
from pathlib import Path
import subprocess
import sys

import pytest

from analysis import report

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_colours', ROOT / 'tools/check_colours.py')
colours = importlib.util.module_from_spec(spec)
spec.loader.exec_module(colours)
sync_spec = importlib.util.spec_from_file_location('sync_design_system', ROOT / 'docs/page/design-system/scripts/sync.py')
sync = importlib.util.module_from_spec(sync_spec)
sync_spec.loader.exec_module(sync)


@pytest.mark.parametrize('value', [
    '#abc', '#abcd', '#123456', '#12345678', 'rgb(1 2 3)', 'rgba(1,2,3,.4)',
    'hsl(20 30% 40%)', 'hwb(20 30% 40%)', 'lab(50 10 20)', 'lch(50 10 20)',
    'oklab(.5 .1 .2)', 'oklch(.5 .1 20)', 'color(display-p3 1 0 0)', 'maroon',
])
def test_literals_rejected_in_css_and_templates(tmp_path, value):
    for name, body in [('page.css', f'.example{{color:{value}}}'),
                       ('template.html', f'<p style="color:{value}">copy</p>'),
                       ('style.html', f'<style>.example{{color:{value}}}</style>'),
                       ('chart.svg', f'<svg><path fill="{value}"/></svg>')]:
        path = tmp_path / name
        path.write_text(body)
        assert colours.check_file(path), (name, value)


def test_colour_checker_cli_fails_for_injected_template(tmp_path):
    template = tmp_path / 'template.html'
    template.write_text('<style>.injected{color:#123456}</style>')
    run = subprocess.run([sys.executable, str(ROOT / 'tools/check_colours.py'), str(template)], capture_output=True, text=True)
    assert run.returncode == 1
    assert '#123456' in run.stdout and str(template) in run.stdout


def test_token_references_and_copy_are_not_colour_literals(tmp_path):
    page = tmp_path / 'page.html'
    page.write_text('''<style>/* color:#123456 */
        a{color:var(--blue);background:color-mix(in srgb,var(--bg) 8%,transparent)}
        </style><p id="feed" style="color:var(--fg);">Red and purple marks.</p>
        <script>const p=document.querySelector('#feed'); // color:#123456
        p.style.color="var(--fg)";</script>''')
    assert not colours.check_file(page)


@pytest.mark.parametrize('body', [
    'node.style.color="red";', 'node.style.backgroundColor="#abc";',
    'const fill="#123456";', 'const fill="oklch(.5 .1 20)";',
])
def test_script_literal_colours_rejected(tmp_path, body):
    path = tmp_path / 'page.js'
    path.write_text(body)
    assert colours.check_file(path)


def test_mask_and_meta_cannot_hide_other_colours(tmp_path):
    path = tmp_path / 'page.html'
    path.write_text('<meta name="theme-color" content="#123456"><style>.x{mask-image:none;color:#abcdef}</style>')
    errors = colours.check_file(path)
    assert any('#123456' in e for e in errors) and any('#abcdef' in e for e in errors)


def test_token_block_is_bounded(tmp_path, monkeypatch):
    path = tmp_path / 'tokens.css'
    monkeypatch.setattr(colours, 'TOKENS', path)
    path.write_text('/* FABLE TOKENS BEGIN */:root{--fg:#123456}/* FABLE TOKENS END */\na{color:#abcdef}')
    errors = colours.check_file(path)
    assert len(errors) == 1 and '#abcdef' in errors[0]
    path.write_text('/* FABLE TOKENS BEGIN */:root{--fg:#123456}')
    assert any('complete FABLE token block' in e for e in colours.check_file(path))


def test_real_page_has_no_colour_literals_outside_tokens(tmp_path):
    assert not colours.check([ROOT / 'docs/page'])
    path = tmp_path / 'page.html'
    path.write_text(report.render()[2])
    assert not colours.check_file(path)


def test_site_selectors_map_to_real_report_hooks():
    css = '.frontier{stroke:var(--data-frontier)}.chart .grid{stroke:var(--data-grid)}.cell-most{color:var(--color-accent-200)}.pt-claude{fill:var(--data-claude)}'
    adapted = sync.adapt(css, sync.THEME_SELECTORS)
    assert '.ex-front,path[data-front]' in adapted
    assert '.ex-grid{' in adapted and '.grid .part{' in adapted
    assert '.pt-claude' not in adapted


def test_single_bundle_has_pinned_tokens_and_theme_modes():
    css = (ROOT / 'docs/page/tokens.css').read_text()
    assert css.count(colours.BEGIN) == css.count(colours.END) == 1
    assert '@import' not in css
    for path in sync.FILES[:3]:
        assert 'design-system/' + path in css
    assert 'c56032fca7ccb5a9661c247f0d6160a576c4b637' in css
    assert ':root[data-theme="light"]' in css and ':root[data-theme="dark"]' in css
    assert 'prefers-color-scheme:light' in css


def test_all_mapped_theme_variables_resolve_to_tokens():
    css = (ROOT / 'docs/page/tokens.css').read_text()
    defined = set(re.findall(r'(--[\w-]+)\s*:', css))
    references = set(re.findall(r'var\((--[\w-]+)', css))
    for path in ('components/patterns.css', 'dispatchbench/dispatchbench-theme.css'):
        references.update(re.findall(r'var\((--[\w-]+)', (sync.DS / path).read_text()))
    assert references <= defined, references - defined
    assert {'--font-body', '--font-heading', '--space-1', '--color-neutral-300'} <= defined


def test_sync_extracts_base_tokens_after_font_import():
    source = "@import url('https://fonts.test/css?family=Inter:wght@400;500;600');\n:root{--font-body:Inter;--space-1:2.8px}body{margin:0}"
    roots = [body for selector, body in sync.rules(source) if selector.strip() == ':root']
    assert roots == ['--font-body:Inter;--space-1:2.8px']


def test_inlined_bundle_must_match_the_trusted_token_block(tmp_path):
    path = tmp_path / 'page.html'
    tokens = (ROOT / 'docs/page/tokens.css').read_text()
    path.write_text('<style>' + tokens + '.x{color:var(--fg)}</style>')
    assert not colours.check_file(path)
    path.write_text(path.read_text().replace('--color-bg: #161826', '--color-bg: #123456'))
    assert any('differs from the runtime bundle' in e for e in colours.check_file(path))


def test_theme_text_roles_have_normal_text_contrast():
    # Exercise both explicit modes using the shipped token definitions, including
    # aliases. Browser rendering is an additional check when Chrome can start.
    css = (ROOT / 'docs/page/tokens.css').read_text()
    base = {}
    for selector, body in sync.rules(css):
        if selector.strip() == ':root':
            base.update(re.findall(r'(--[\w-]+)\s*:\s*([^;]+)', body))

    def luminance(value):
        channels = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
        return sum(v * weight for v, weight in zip(linear, (.2126, .7152, .0722)))

    for mode in ('light', 'dark'):
        values = dict(base)
        body = re.search(r':root\[data-theme="' + mode + r'"\]\{([^}]*)\}', css)[1]
        values.update(re.findall(r'(--[\w-]+)\s*:\s*([^;]+)', body))

        def resolve(name):
            value = values[name].strip()
            match = re.fullmatch(r'var\((--[\w-]+)\)', value)
            return resolve(match[1]) if match else luminance(value)

        for role in ('--fg', '--muted', '--accent-text', '--color-link', '--color-kicker', '--color-subtle'):
            for ground in ('--bg', '--panel'):
                low, high = sorted((resolve(role), resolve(ground)))
                assert (high + .05) / (low + .05) >= 4.5, (mode, role, ground)
