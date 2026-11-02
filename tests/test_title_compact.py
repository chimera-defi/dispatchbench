from html.parser import HTMLParser
from pathlib import Path


class HeadingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self.inside_heading = False
        self.first_svg_seen = False

    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            self.headings.append({'text': '', 'br': False, 'before_svg': not self.first_svg_seen})
            self.inside_heading = True
        elif tag == 'svg':
            self.first_svg_seen = True
        elif tag == 'br' and self.inside_heading:
            self.headings[-1]['br'] = True

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.inside_heading = False

    def handle_data(self, data):
        if self.inside_heading:
            self.headings[-1]['text'] += data


def test_rendered_title_is_compact_and_precedes_first_svg():
    parser = HeadingParser()
    parser.feed((Path(__file__).resolve().parents[1] / 'results/report/page.html').read_text())
    assert len(parser.headings) == 1
    heading = parser.headings[0]
    assert len(heading['text']) <= 60
    assert not heading['br']
    assert heading['text'] == 'DispatchBench: which model should a coding task go to?'
    assert parser.first_svg_seen and heading['before_svg']
