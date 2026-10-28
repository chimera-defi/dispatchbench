"""The shared site topbar stays first, linked and free of local colour values."""
from html.parser import HTMLParser
from pathlib import Path
import re

import pytest

from analysis import report


ROOT = Path(__file__).resolve().parents[1]
MARKUP = '<div class="ds-topbar"><div><a href="https://chimericlabs.xyz/">← Chimeric Labs</a></div></div>'


class BodyElements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_body = False
        self.elements = []

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        elif self.in_body:
            self.elements.append((tag, dict(attrs)))


@pytest.mark.parametrize("rendered", [False, True], ids=["shell", "report"])
def test_topbar_is_first_and_uses_the_exact_site_markup(rendered):
    html = report.render()[2] if rendered else (ROOT / "docs/page/shell.html").read_text()
    parser = BodyElements()
    parser.feed(html)
    assert parser.elements[:3] == [
        ("div", {"class": "ds-topbar"}),
        ("div", {}),
        ("a", {"href": "https://chimericlabs.xyz/"}),
    ]
    assert html.count(MARKUP) == 1
    assert '<link rel="stylesheet" href="../../docs/page/topbar.css">' not in html
    if rendered:
        css = re.search(r"<style>(.*?)</style>", html, re.S)[1]
        assert (ROOT / "docs/page/topbar.css").read_text().strip() in css
        assert 'href="https://github.com/chimera-defi/dispatchbench"' in html
    else:
        assert "<style>\n__CSS__\n</style>" in html


def test_topbar_css_uses_variables_for_every_colour():
    css = (ROOT / "docs/page/topbar.css").read_text()
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\s*\(", css)
    declarations = re.findall(
        r"(?:^|[;{])\s*(?:color|background(?:-color)?|border-bottom(?:-color)?|outline)\s*:\s*([^;}]+)",
        css,
    )
    assert declarations
    for value in declarations:
        assert "var(--" in value
        # Remove nested variable fallbacks; only border/outline geometry may remain.
        while "var(" in value:
            value = re.sub(r"var\([^()]*\)", "", value)
        assert re.fullmatch(r"(?:\d+(?:\.\d+)?px|solid|\s)*", value), value
