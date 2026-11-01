"""R6: public anchors remain stable and every title exposes a permalink."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re

from analysis import page

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ['winner', 'pareto', 'results', 'problems', 'grok', 'method', 'fail',
            'tokens', 'pipes', 'fair', 'conclusion', 'limits', 'extras', 'notes',
            'interesting', 'equiv']
PILOTS = ['pilot-fizz-buzz', 'pilot-course-schedule-ii', 'pilot-candy',
          'pilot-reconstruct-itinerary', 'pilot-minimum-window-substring', 'pilot-wildcard-matching']


class Node:
    def __init__(self, tag='', attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children, self.text = [], ''

    def descendants(self):
        for child in self.children:
            yield child
            yield from child.descendants()


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.root = self.current = Node()
        self.feed(text)
        self.nodes = list(self.root.descendants())

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.current = node

    def handle_endtag(self, tag):
        node = self.current
        while node.parent:
            if node.tag == tag:
                self.current = node.parent
                break
            node = node.parent

    def handle_data(self, text):
        node = self.current
        while node:
            node.text += text
            node = node.parent


def document():
    return Document((ROOT / 'results/report/page.html').read_text())


def assert_link(node):
    links = [n for n in node.descendants() if 'hlink' in n.attrs.get('class', '').split()]
    matching = [n for n in links if n.attrs.get('href') == '#' + node.attrs['id']]
    assert len(matching) == 1, node.attrs
    assert matching[0].tag == 'a' and matching[0].text == '#'
    assert matching[0].attrs['aria-label'].startswith('Link to this section: ')
    assert matching[0].attrs.get('tabindex') != '-1'


def test_sections_and_problem_ids_are_unique_and_pinned():
    doc = document()
    ids = [n.attrs['id'] for n in doc.nodes if 'id' in n.attrs]
    assert [i for i, count in Counter(ids).items() if count > 1] == []
    assert [n.attrs.get('id') for n in doc.nodes if n.tag == 'section'] == SECTIONS
    problems = next(n for n in doc.nodes if n.attrs.get('id') == 'problems')
    entries = [n for n in problems.descendants() if n.tag == 'li' and
               (n.attrs.get('class') == 'prow' or n.attrs.get('id', '').startswith('pilot-'))]
    assert [n.attrs['id'] for n in entries] == PILOTS + [f'p{i:02}' for i in range(1, 16)]
    for entry in entries:
        assert_link(entry)
        if entry.attrs['id'].startswith('pilot-'):
            continue
        details = next(n for n in entry.children if n.tag == 'details')
        assert details.attrs['id'] == entry.attrs['id'] + '-try'
        assert 'open' not in details.attrs
        # Existing descriptive R4 links continue to resolve inside each row.
        assert any(n.attrs.get('id', '').startswith(entry.attrs['id'] + '_') for n in entry.descendants())


def test_all_body_headings_expose_a_permalink():
    doc = document()
    def in_grok(n):  # #grok is kept byte-identical; its section id is the link
        while n:
            if n.attrs.get('id') == 'grok': return True
            n = n.parent
        return False
    for heading in (n for n in doc.nodes if n.tag in {'h2', 'h3'} and not in_grok(n)):
        assert heading.attrs.get('id'), heading.text
        assert re.fullmatch(r'[a-z][a-z0-9_-]*', heading.attrs['id'])
        assert_link(heading)
    assert any(n.attrs.get('aria-live') == 'polite' for n in doc.nodes)


def test_generated_heading_ids_are_ascii_unique_and_deterministic():
    source = ('<section id="cafe"><h2>Café &amp; tea!</h2><h3>Café &amp; tea!</h3>'
              '<h3 id="existing">Kept</h3><h3>existing</h3><h3>🧪</h3></section>')
    linked = page.deep_links(source)
    assert linked == page.deep_links(source)
    assert linked == page.deep_links(linked)
    headings = [n for n in Document(linked).nodes if n.tag in {'h2', 'h3'}]
    assert [n.attrs['id'] for n in headings] == ['cafe-tea', 'cafe-tea-2', 'existing', 'existing-2', 'heading']
    for heading in headings:
        assert_link(heading)


def test_heading_annotation_preserves_script_templates():
    source = "<h2>Visible</h2><script>const title='<h3>Runtime title</h3>';</script>"
    linked = page.deep_links(source)
    assert linked.split('<script>', 1)[1] == source.split('<script>', 1)[1]


def test_explorer_detail_headings_keep_generated_links_after_interaction():
    from analysis import dataset
    import json
    import subprocess

    source = (ROOT / 'tests/pareto_runtime.cjs').read_text().split('const h=context.harness,exp=payload.explorer', 1)[0]
    source += "\nprocess.stdout.write(element('ex-detail').innerHTML);"
    result = subprocess.run(['node', '-e', source], input=json.dumps({'explorer': page.explorer_data(dataset.view(dataset.read()))}),
                            capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, result.stderr
    heading = next(n for n in Document(result.stdout).nodes if n.tag == 'h3')
    assert heading.attrs.get('id')
    assert_link(heading)


def test_grok_section_bytes_unchanged():
    # deep_links() skips #grok: raw bytes equal the pre-R6 section (and HEAD before R).
    import hashlib
    from analysis.test_grok import grok_section

    section, _ = grok_section((ROOT / 'results/report/page.html').read_text(), html=True)
    assert hashlib.sha256(section.encode()).hexdigest() == 'f33bea01f967bd26db464a3b796632976e797bd802cfad2a0f0341d461f04be4'


def test_deep_links_in_chrome():
    # The browser harness is not optional: a sandbox without Chrome must fail here, not skip.
    import subprocess
    result = subprocess.run(['node', 'tests/deeplink_runtime.cjs'], text=True, capture_output=True, cwd=ROOT, timeout=300)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'deep links:' in result.stdout
