"""Fable's check-tokens.mjs rule for report CSS, HTML, SVG and JavaScript.

Only docs/page/design-system/tokens/*.css and the marked runtime token block
may contain colours. No Node dependency. Run from any directory, or pass paths
for a focused check. Generated report HTML is checked when present.
"""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / 'docs/page/tokens.css'
VENDORED_TOKENS = ROOT / 'docs/page/design-system/tokens'
BEGIN = '/* FABLE TOKENS BEGIN'
END = '/* FABLE TOKENS END */'
NAMED = 'red|green|blue|black|white|gray|grey|orange|yellow|purple|pink|brown|cyan|magenta|teal|navy|maroon|crimson|tomato|coral|gold|silver|lime|olive|indigo|violet|salmon|khaki|ivory|beige'
HEX = r'#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})(?![\w-])'
LITERALS = [
    re.compile(r'(?<![\w\[.])' + HEX),
    re.compile(r'\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(\s*(?!var\(|from\b)[\d.+-]', re.I),
    re.compile(r'\bcolor\(\s*(?!var\(|from\b)[\w-]+\s+[\d.+-]', re.I),
    re.compile(r'(?:color|background(?:-color)?|border(?:-[a-z]+)*|fill|stroke|outline(?:-color)?|box-shadow)\s*:[^;{}]*\b(?:' + NAMED + r')\b', re.I),
]
STYLE_ASSIGNMENT = re.compile(r'''\.style\.(?:color|background\w*|fill|stroke|borderColor)\s*=\s*["'`]([^"'`]+)''')
TOKEN_BLOCK = re.compile(r'/\* FABLE TOKENS BEGIN.*?/\* FABLE TOKENS END \*/', re.S)
COMMENTS = re.compile(r'/\*.*?\*/', re.S)


def mask_comments(text):
    return COMMENTS.sub(lambda m: '\n' * m[0].count('\n'), text)


def css_errors(text):
    text = mask_comments(text)
    # A named token such as var(--blue) is a reference, not a named colour.
    text = re.sub(r'var\(\s*--[\w-]+\s*\)', 'var(--token)', text)
    return [(text.count('\n', 0, m.start()) + 1, m[0])
            for pattern in LITERALS for m in pattern.finditer(text)]


class PageColours(HTMLParser):
    def __init__(self):
        super().__init__()
        self.mode = None
        self.errors = []

    def handle_starttag(self, tag, attrs):
        self.mode = tag if tag in ('style', 'script') else self.mode
        for key, value in attrs:
            if value is None:
                continue
            if key == 'style':
                self.errors.extend((self.getpos()[0] + n - 1, literal) for n, literal in css_errors(value))
            elif key in ('fill', 'stroke', 'color', 'bgcolor', 'stop-color', 'flood-color', 'lighting-color'):
                self.errors.extend((self.getpos()[0], literal) for _, literal in css_errors(key + ':' + value))
            elif tag == 'meta' and key == 'content' and dict(attrs).get('name') == 'theme-color':
                self.errors.extend((self.getpos()[0], literal) for _, literal in css_errors('color:' + value))

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        if tag == self.mode:
            self.mode = None

    def handle_data(self, text):
        errors = css_errors(text) if self.mode == 'style' else js_errors(text) if self.mode == 'script' else []
        self.errors.extend((self.getpos()[0] + n - 1, literal) for n, literal in errors)


def js_errors(text):
    # Mirror the upstream hex/function and style-assignment checks, while keeping
    # selector strings such as querySelector('#feed') out of CSS value scanning.
    text = re.sub(r'(?m)(?<!\S)//[^\n]*', '', mask_comments(text))
    patterns = [re.compile(r'''(?<![\w"'=.\[])''' + HEX),
                re.compile(r'''(?<=["'])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6})(?=["'])'''),
                *LITERALS[1:]]
    errors = [(text.count('\n', 0, m.start()) + 1, m[0]) for pattern in patterns for m in pattern.finditer(text)]
    for match in STYLE_ASSIGNMENT.finditer(text):
        errors.extend((text.count('\n', 0, match.start()) + n, literal)
                      for n, literal in css_errors('color:' + match[1]))
    return errors


def check_file(path):
    path = Path(path).resolve()
    if path.parent == VENDORED_TOKENS.resolve() and path.suffix == '.css':
        return []
    text = path.read_text()
    block_errors = []
    if path == TOKENS.resolve():
        if text.count(BEGIN) != 1 or text.count(END) != 1 or not TOKEN_BLOCK.search(text):
            block_errors.append((1, 'expected exactly one complete FABLE token block'))
        # Preserve line positions for any declarations after the token block.
        text = TOKEN_BLOCK.sub(lambda m: '\n' * m[0].count('\n'), text)
    if path.suffix in ('.html', '.svg'):
        # The integrator may inline the runtime block. Accept only an exact copy
        # of the trusted bundle, never an arbitrary marker in an HTML template.
        blocks = TOKEN_BLOCK.findall(text)
        if blocks:
            trusted = TOKEN_BLOCK.search(TOKENS.read_text())
            if len(blocks) == 1 and trusted and blocks[0] == trusted[0]:
                text = TOKEN_BLOCK.sub(lambda m: '\n' * m[0].count('\n'), text)
            else:
                block_errors.append((1, 'HTML token block differs from the runtime bundle'))
        parser = PageColours()
        parser.feed(text)
        errors = parser.errors
    elif path.suffix in ('.js', '.mjs'):
        errors = js_errors(text)
    else:
        errors = css_errors(text)
    return [f'{path}:{line}: {literal.strip()}' for line, literal in sorted(set(block_errors + errors))]


def files(paths):
    for path in paths:
        if path.is_symlink():
            continue
        if path.is_dir():
            yield from files(sorted(p for p in path.iterdir() if not p.name.startswith('.') and p.name != 'node_modules'))
        elif path.suffix in ('.css', '.html', '.svg', '.js', '.mjs'):
            yield path


def check(paths=None):
    if paths is None:
        paths = [ROOT / 'docs/page']
        page = ROOT / 'results/report/page.html'
        if page.exists():
            paths.append(page)
    return [error for path in files(paths) for error in check_file(path)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*', type=Path)
    args = parser.parse_args()
    errors = check(args.paths or None)
    print('\n'.join(errors) if errors else 'ok: no colour literals outside token files')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
