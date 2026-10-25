"""Before landing: show what this branch removes, so nothing vanishes by accident.

1. Rendered page: visible text lines and table headers in the base page but not in the new one.
2. Merges in base..HEAD: lines one side added that the merge result dropped.

Exits 1 when anything is listed; rerun with --ack once each item is checked as intended.
"""
import argparse, re, subprocess, sys
from html.parser import HTMLParser

PAGE = "results/report/page.html"
SRC = re.compile(r"^(docs/.*\.tmpl\.md|docs/page/.*|analysis/.*\.py|bench/.*\.py|tests/.*\.py|Makefile)$")


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.lines = set(); self.heads = []; self.cur = []; self.th = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"): self.skip += 1
        if tag == "tr": self.th = []
        if tag in ("p", "li", "td", "th", "h1", "h2", "h3", "h4", "summary", "figcaption", "caption", "tr", "br"): self.flush()

    def handle_endtag(self, tag):
        if tag in ("script", "style"): self.skip -= 1
        if tag in ("p", "li", "td", "th", "h1", "h2", "h3", "h4", "summary", "figcaption", "caption"): self.flush()
        if tag == "th" and self.th is not None: self.th.append(self.last)
        if tag == "tr" and self.th: self.heads.append(" | ".join(self.th)); self.th = None

    def handle_data(self, d):
        if not self.skip: self.cur.append(d)

    def flush(self):
        t = " ".join("".join(self.cur).split()); self.cur = []; self.last = t
        if len(t) > 3: self.lines.add(t)


def read(html):
    p = Text(); p.last = ""; p.feed(html); p.flush(); return p


def page_removals(base):
    old, new = read(git("show", f"{base}:{PAGE}")), read(open(PAGE).read())
    gone = sorted(old.lines - new.lines)
    heads = sorted(set(old.heads) - set(new.heads))
    return [f"page text: {t}" for t in gone] + [f"table header: {h}" for h in heads]


def merge_drops(base):
    out = []
    for line in git("log", "--merges", "--format=%H %h", f"{base}..HEAD").splitlines():
        H, h = line.split()
        p1, p2 = git("rev-list", "--parents", "-n1", H).split()[1:3]
        mb = git("merge-base", p1, p2).strip()
        for p in (p1, p2):
            for f in git("diff", "--name-only", mb, p).split():
                if not SRC.match(f): continue
                have = set(git("show", f"{H}:{f}").splitlines())
                for l in git("diff", "-U0", mb, p, "--", f).splitlines():
                    if l.startswith("+") and not l.startswith("+++") and len(l.strip()) > 3 and l[1:] not in have:
                        out.append(f"merge {h} dropped {f}: {l[1:].strip()[:100]}")
    return out


def main():
    a = argparse.ArgumentParser(); a.add_argument("--base", default="fast-mode-main"); a.add_argument("--ack", action="store_true")
    o = a.parse_args()
    items = page_removals(o.base) + merge_drops(o.base)
    for i in items: print(i)
    print(f"landcheck: {len(items)} removal(s) vs {o.base}" + ("; acknowledged" if o.ack and items else ""))
    sys.exit(1 if items and not o.ack else 0)


if __name__ == "__main__":
    main()
