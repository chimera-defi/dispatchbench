"""Keyboard sorting enhancement and its single-file report bundle."""
import json
import re
import subprocess
from pathlib import Path

from analysis import configs

ROOT = Path(__file__).resolve().parents[1]


def test_sortable_headers_runtime():
    result = subprocess.run(
        ['node', 'tests/sort_runtime.cjs'], cwd=ROOT,
        text=True, capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_built_page_inlines_sorting_script_and_styles():
    html = (ROOT / 'results/report/page.html').read_text()
    script = (ROOT / 'docs/page/sort.js').read_text().strip().replace(
        '__RESCUE_SET_LABEL__', json.dumps(configs.set_label('rescue set')))
    assert script in [block.strip() for block in re.findall(r'<script>(.*?)</script>', html, re.S)]
    css = (ROOT / 'docs/page/style.css').read_text().strip()
    assert any(css in style for style in re.findall(r'<style>(.*?)</style>', html, re.S))
