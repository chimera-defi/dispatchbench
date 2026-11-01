"""R1: first-choice font families must be requested by the deployed page."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def test_first_choice_fonts_are_loaded():
    html = (ROOT / 'results/report/page.html').read_text()
    class Links(HTMLParser):
        def __init__(self):
            super().__init__(); self.urls = []
        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == 'link' and a.get('rel') == 'stylesheet':
                self.urls.append(a.get('href', ''))
    links = Links(); links.feed(html)
    requested = {family.split(':')[0] for url in links.urls
                 if urlsplit(url).hostname == 'fonts.googleapis.com'
                 for family in parse_qs(urlsplit(url).query).get('family', [])}
    for token in ('body', 'heading', 'mono'):
        family = re.findall(r'--font-' + token + r'\s*:\s*([^,;]+)', html)[-1].strip('" ')
        if family not in {'system-ui', 'ui-monospace', 'monospace', 'sans-serif', 'serif'}:
            assert family in requested, (token, family, requested)
    assert {'Inter', 'JetBrains Mono'} <= requested
