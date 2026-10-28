"""The deployed report is copied as a single HTML file."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit

import pytest

ROOT = Path(__file__).resolve().parents[1]


class PageAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.relative_urls = []
        self.relative_stylesheets = []
        self.styles = []
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "style":
            self.in_style = True
        for key in ("src", "href"):
            value = attrs.get(key, "")
            if value.startswith(("./", "../")):
                self.relative_urls.append(value)
        if tag == "link" and "stylesheet" in attrs.get("rel", "").lower().split():
            href = attrs.get("href", "")
            if not urlsplit(href).scheme and not href.startswith("//"):
                self.relative_stylesheets.append(href)

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False

    def handle_data(self, text):
        if self.in_style:
            self.styles.append(text)


@pytest.fixture(scope="module")
def assets():
    parser = PageAssets()
    parser.feed((ROOT / "results/report/page.html").read_text())
    return parser


def test_page_has_no_relative_asset_urls(assets):
    assert not assets.relative_stylesheets
    assert not assets.relative_urls


def test_page_inlines_tokens_topbar_and_styles_in_order(assets):
    css = "".join(assets.styles).strip()
    expected = "\n".join((ROOT / "docs/page" / name).read_text().strip()
                         for name in ("tokens.css", "topbar.css", "style.css"))
    assert css == expected
    assert re.search(r"\.ds-topbar\s*\{", css)
    for name in ("--color-surface", "--color-neutral-300", "--accent"):
        assert re.search(re.escape(name) + r"\s*:", css), name
