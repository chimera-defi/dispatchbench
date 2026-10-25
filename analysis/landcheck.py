"""Before landing: show what this branch removes, so nothing vanishes by accident.

1. Rendered page: visible text lines and table headers in the base page but not in the new one.
2. Merges in base..HEAD: lines one side added that the merge result dropped.
3. Page integrity: facts the base page rendered that this page no longer renders,
   and placeholders in otherwise numeric table columns.

Exits 1 for unacknowledged findings. --ack acknowledges removals; intentional
page findings need individual reasons in docs/landcheck_allow.json.
"""
import argparse, json, re, subprocess, sys
from html.parser import HTMLParser
from pathlib import Path

PAGE = "results/report/page.html"
USED = "results/report/facts_used.json"
ALLOW = "docs/landcheck_allow.json"
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


class Tables(HTMLParser):
    """Read rendered cells, including inline spans, without counting group headers as data."""
    def __init__(self):
        super().__init__()
        self.tables = []; self.section = "page"; self.table = None; self.row = None; self.cell = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section": self.section = attrs.get("id", "page")
        if tag == "table":
            self.table = dict(section=self.section, rows=[]); self.tables.append(self.table)
        if self.table is None: return
        if tag == "tr": self.row = []
        if tag in ("td", "th") and self.row is not None:
            self.cell = dict(tag=tag, text=[], span=int(attrs.get("colspan", 1)))

    def handle_data(self, data):
        if self.cell is not None: self.cell["text"].append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.cell["text"] = " ".join("".join(self.cell["text"]).split())
            self.row.append(self.cell); self.cell = None
        if tag == "tr" and self.row is not None:
            self.table["rows"].append(self.row); self.row = None
        if tag == "table": self.table = None


def placeholder_cells(html):
    parser = Tables(); parser.feed(html)
    out = []
    numeric = re.compile(r"[~≈≥≤<>+$€£\d.,%×:/→–−\-\s()\[\]]+(?:\s*s)?")
    for table in parser.tables:
        rows = table["rows"]
        heads = next(([c["text"] for c in row] for row in rows
                      if row and all(c["tag"] == "th" and c["span"] == 1 for c in row)), [])
        data = [row for row in rows if row and any(c["tag"] == "td" for c in row)
                and all(c["span"] == 1 for c in row)]
        for col in range(max(map(len, data), default=0)):
            values = [row[col]["text"] for row in data if len(row) > col]
            if not any(re.search(r"\d", v) and numeric.fullmatch(v) for v in values): continue
            for row in data:
                if len(row) <= col or row[col]["text"].casefold() not in ("–", "n/a", "all", ""): continue
                head = heads[col] if col < len(heads) else f"column {col + 1}"
                out.append(f"{table['section']} | {' / '.join(heads)} | {row[0]['text']} | {head}: {row[col]['text']!r}")
    return sorted(set(out))


def page_integrity(base="fast-mode-main"):
    """Dropped facts: rendered on base, no longer rendered here (a fact lost in a rewrite)."""
    from analysis import report
    used = set()
    rendered = report.render(used_facts=used)[2]
    built = Path(PAGE).read_text()
    shown = git("show", f"{base}:{USED}")
    # No list on base (first landing with this guard): say so rather than report a silent zero.
    dropped = sorted(set(json.loads(shown)) - used) if shown else None
    return dropped, placeholder_cells(built), built == rendered


def page_findings(base="fast-mode-main"):
    dropped, cells, current = page_integrity(base)
    allow = json.loads(Path(ALLOW).read_text())
    items = [] if current else ["page differs from current render; rebuild before landcheck"]
    if dropped is None:  # first landing with this guard: say so rather than report a silent zero
        print(f"landcheck: dropped-facts check SKIPPED: {base} has no {USED}"); dropped = []
    for kind, found in (("dropped_facts", dropped), ("placeholder_cells", cells)):
        reasons = allow.get(kind, {})
        items += [f"{kind}: {key}" for key in found if not isinstance(reasons.get(key), str) or not reasons[key].strip()]
    return items


def main():
    a = argparse.ArgumentParser(); a.add_argument("--base", default="fast-mode-main"); a.add_argument("--ack", action="store_true")
    o = a.parse_args()
    integrity = page_findings(o.base)
    items = page_removals(o.base) + merge_drops(o.base)
    for i in items: print(i)
    print(f"landcheck: {len(items)} removal(s) vs {o.base}" + ("; acknowledged" if o.ack and items else ""))
    for i in integrity: print(i)
    print(f"landcheck: {len(integrity)} unacknowledged page-integrity finding(s)")
    sys.exit(1 if integrity or (items and not o.ack) else 0)


if __name__ == "__main__":
    main()
