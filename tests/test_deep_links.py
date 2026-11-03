"""R6: public anchors remain stable and every title exposes a permalink."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import os
import re

from analysis import page

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ['winner', 'pareto', 'results', 'problems', 'grok', 'method', 'fail',
            'tokens', 'pipes', 'fair', 'conclusion', 'limits', 'extras', 'notes',
            'interesting', 'equiv']


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


def assert_link(node, identifier=None):
    links = [n for n in node.descendants() if 'hlink' in n.attrs.get('class', '').split()]
    matching = [n for n in links if n.attrs.get('href') == '#' + (identifier or node.attrs['id'])]
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
    assert [n.attrs['id'] for n in entries] == [f'p{i:02}' for i in range(1, 16)]
    for entry in entries:
        assert_link(entry)
        if entry.attrs['id'].startswith('pilot-'):
            continue
        details = next(n for n in entry.children if n.tag == 'details')
        assert details.attrs['id'] == entry.attrs['id'] + '-try'
        assert 'open' not in details.attrs
        # Existing descriptive R4 links continue to resolve inside each row.
        assert any(n.attrs.get('id', '').startswith(entry.attrs['id'] + '_') for n in entry.descendants())


def test_generated_heading_ids_are_ascii_unique_and_deterministic():
    source = ('<section id="cafe"><h2>Café &amp; tea!</h2><h3>Café &amp; tea!</h3>'
              '<h3 id="existing">Kept</h3><h3>existing</h3><h3>🧪</h3></section>')
    linked = page.deep_links(source)
    assert linked == page.deep_links(source)
    assert linked == page.deep_links(linked)
    headings = [n for n in Document(linked).nodes if n.tag in {'h2', 'h3'}]
    assert 'id' not in headings[0].attrs
    assert_link(headings[0], 'cafe')
    assert [n.attrs['id'] for n in headings[1:]] == ['cafe-tea', 'existing', 'existing-2', 'heading']
    for heading in headings[1:]:
        assert_link(heading)


def test_section_titles_target_the_section_without_generated_ids():
    for section in (n for n in document().nodes if n.tag == 'section'):
        heading = next(n for n in section.descendants() if n.tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'})
        assert heading.attrs.get('id') == ('grok-and-devin' if section.attrs['id'] == 'grok' else None)
        assert not re.search(r'-\d+$', heading.attrs.get('id', ''))
        assert_link(heading, section.attrs['id'])
    assert 'accuracyone' not in (ROOT / 'results/report/page.html').read_text()


def test_wrapped_section_titles_and_slug_words_stay_separate():
    source = ('<section id="pareto"><header><h2><span>Cost vs accuracy</span>'
              '<span>One chart</span></h2></header>'
              '<h3><span>Cost vs accuracy</span><span>One chart</span></h3></section>'
              '<section id="other"><header><h4 id="pinned">Other</h4></header></section>')
    linked = page.deep_links(source)
    assert linked == page.deep_links(linked)
    headings = [n for n in Document(linked).nodes if n.tag in {'h2', 'h3', 'h4'}]
    assert 'id' not in headings[0].attrs
    assert_link(headings[0], 'pareto')
    assert headings[1].attrs['id'] == 'cost-vs-accuracy-one-chart'
    assert_link(headings[1])
    assert headings[2].attrs['id'] == 'pinned'
    assert_link(headings[2], 'other')


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


def test_config_hash_resolves_embedded_rows_before_rebuilding_detail():
    from analysis import dataset
    import json
    import subprocess

    source = (ROOT / 'tests/pareto_runtime.cjs').read_text().split('const h=context.harness,exp=payload.explorer', 1)[0]
    source = source.replace('window:{addEventListener(){}},console',
                            "window:{location:{hash:'#config-sonnet-low'},addEventListener(){}},console")
    source += """
const h=context.harness;
assert.equal(h.st.set,'pilot');assert(element('ex-detail').innerHTML.includes('id="config-sonnet-low"'));
for(const [id,set] of [['config-sonnet-medium','main'],['config-sonnet-low','pilot'],['config-sonnet-medium','main']]){
 assert(root.resolveConfigHash(id));assert.equal(h.st.set,set);
 assert(element('ex-detail').innerHTML.includes('id="'+id+'"'));
 assert.equal(element('ex-set').value,set);
}
h.st.off.add(h.st.sel);h.st.facets.add('family:Claude');h.st.prereg=true;h.st.minPass=1;
assert(root.resolveConfigHash('config-sonnet-low'));
assert(element('ex-chart').innerHTML.includes(h.st.sel));
assert(element('ex-detail').innerHTML.includes('id="config-sonnet-low"'));
const before=element('ex-detail').innerHTML;
assert.equal(root.resolveConfigHash('config-does-not-exist'),false);
assert.equal(element('ex-detail').innerHTML,before);
"""
    result = subprocess.run(['node', '-e', source], input=json.dumps({'explorer': page.explorer_data(dataset.view(dataset.read()))}),
                            capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0, result.stderr




def _playwright_node_path():
    """NODE_PATH that resolves `playwright`: the caller's, else a node_modules in the repo, else the newest npx cache."""
    import glob
    found = [os.environ.get('NODE_PATH', ''), os.path.join(ROOT, 'node_modules')]
    found += sorted(glob.glob(os.path.expanduser('~/.npm/_npx/*/node_modules')),
                    key=lambda d: os.path.getmtime(d), reverse=True)
    return os.pathsep.join(d for d in found if d and (d == found[0] or os.path.isdir(os.path.join(d, 'playwright'))))


def test_all_body_headings_and_deep_links_in_chrome():
    # The browser harness is not optional: a sandbox without Chrome must fail here, not skip.
    import subprocess
    result = subprocess.run(['node', 'tests/deeplink_runtime.cjs'], text=True, capture_output=True, cwd=ROOT, timeout=300,
                            env={**os.environ, 'NODE_PATH': _playwright_node_path()})
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'deep links:' in result.stdout
