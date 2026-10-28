"""make audit: fail if any committed number disagrees with the data. No model calls, standard library only.

1. results/report/tables.md and results/manifest.json equal what analysis.summarize computes now
   from the graded rows.
2. Every chart in results/report/charts equals what analysis.charts draws from that summary.
3. results/report/luna_rescue.md equals the table analysis.luna_rescue computes from the appendix rows.
4. README.md, docs/REPORT.md, results/report/page.html and results/report/facts_used.json equal what analysis.report renders from the
   template; docs/RAW_RUNS.md equals analysis.raw_runs (except the manifest hash, which carries the commit sha); results/dataset.json
   equals what analysis.dataset builds from the jsonl files (results/report/og.png needs a browser and is not compared).
5. The templates (README, report, page and docs/page/*.html text) hold no digit of their own outside {{facts}}, code spans and link targets,
   except the categories listed with a reason in docs/audit_allow.json (versions, years, deviation and finding ids, the name pass@1).
"""
import html, json, os, re, sys

from analysis import charts, configs, dataset, luna_rescue, raw_runs, report, summarize
from analysis.summarize import ROOT, RES

ALLOW = os.path.join(ROOT, "docs", "audit_allow.json")
NUM = re.compile(r"(?<![\w.\-/^])(\d+(?:[.,]\d+)*)(?!\d|\.\d|[\-‑]\w)")


def same(label, want, path, fails):
    have = open(path).read() if os.path.exists(path) else None
    if have != want:
        fails.append(f"{label}: {os.path.relpath(path, ROOT)} differs from what the data give (run make report)")
    return 1


PAGE_HTML = [os.path.join(ROOT, "docs", "page", f) for f in ("shell.html", "explorer.html")]


def visible(text):
    """The words of an HTML template: scripts, styles, tags and attributes dropped."""
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S)
    return re.sub(r"<[^>]*>", " ", text)


def scan(line):
    """The part of a template line that is the author's own prose, with tokens, code spans and link targets removed."""
    t = re.sub(r"\{\{chart:[^|}]*\|", " ", line)  # keep chart captions in the scan
    t = re.sub(r"\{\{[^{}]*\}\}", " ", t)
    t = re.sub(r"`[^`]*`", " ", t)
    t = re.sub(r"\]\([^)]*\)", "]", t)
    t = re.sub(r"<[^>]*>", " ", t)
    return re.sub(r"^(\s*)\d+\. ", r"\1", t)  # ordered-list markers


def allowed(t, m, allow):
    """Index of the allow entry whose pattern covers the literal at match m, or None."""
    for i, a in enumerate(allow):
        if any(h.start() <= m.start() and m.end() <= h.end() for h in re.finditer(a["regex"], t)): return i


def template_literals(paths=None):
    """(template, line number, literal, scanned line, match) for every number the templates write themselves."""
    out = []
    for path in paths or (report.README_TEMPLATE, report.TEMPLATE, report.PAGE_TEMPLATE, *PAGE_HTML):
        text = open(path).read()
        if path.endswith(".html"): text = visible(text)
        for no, line in enumerate(text.split("\n"), 1):
            t = scan(line)
            out += [(os.path.relpath(path, ROOT), no, m.group(1), t, m) for m in NUM.finditer(t)]
    return out


def stray_literals(literals, allow):
    """(failures, allow entries used): a template digit is a failure unless it sits inside an allowed pattern."""
    used = set(); stray = []
    for path, no, lit, t, m in literals:
        hit = allowed(t, m, allow)
        if hit is not None: used.add(hit)
        else: stray.append(f"{path}:{no}: literal {lit!r} is not a {{{{fact}}}} and matches no category in docs/audit_allow.json")
    return stray, used


DATA_BLOCK = re.compile(r'<script type="application/json" id="data">(.*?)</script>', re.S)


def block_strings(o):
    if isinstance(o, str): yield o
    elif isinstance(o, dict):
        for v in o.values(): yield from block_strings(v)
    elif isinstance(o, list):
        for v in o: yield from block_strings(v)
    elif isinstance(o, (int, float)) and not isinstance(o, bool): yield repr(o)


def page_numbers_missing(page, allow):
    """Numbers in the page's visible text (scripts, styles, SVG, tags and attributes dropped) that are not in its embedded data block
    and not in an allowed category (versions, years, deviation and finding ids, pass@1)."""
    m = DATA_BLOCK.search(page)
    if not m: return ["page has no embedded data block"]
    have = {x.group(1) for s in block_strings(json.loads(m.group(1))) for x in NUM.finditer(s)}
    text = DATA_BLOCK.sub(" ", page)
    text = re.sub(r"<(script|style|svg|title)\b.*?</\1>", " ", text, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]*>", " ", text))
    out = set()
    for line in text.split("\n"):
        t = re.sub(r"^(\s*)\d+\. ", r"\1", line)
        for x in NUM.finditer(t):
            if x.group(1) not in have and allowed(t, x, allow) is None: out.add(x.group(1))
    return [f"page: number {n} is visible but not in the embedded data block" for n in sorted(out)]


def main():
    fails = []; checked = 0
    s, tab, man = summarize.build()
    ds = dataset.build(s)
    checked += same("tables", tab, os.path.join(RES, "report", "tables.md"), fails)
    have_manifest = os.path.join(RES, "manifest.json")
    if os.path.exists(have_manifest):
        current = json.load(open(have_manifest)); current.pop("git_sha", None); man.pop("git_sha", None)
        checked += 1
        if json.dumps(current, indent=1) != json.dumps(man, indent=1):
            fails.append("manifest: results/manifest.json differs from what the data give (run make report)")
    else:
        checked += same("manifest", json.dumps(man, indent=1), have_manifest, fails)
    for name, body in charts.build(ds).items():
        if body: checked += same("chart", body, os.path.join(charts.OUT, name), fails)
    checked += same("luna rescue", luna_rescue.table(luna_rescue.arms()) + "\n", os.path.join(RES, "report", "luna_rescue.md"), fails)
    used = set()
    readme, full, page = report.render(used_facts=used)
    checked += same("facts used", json.dumps(sorted(used), indent=0) + "\n", dataset.FACTS_USED, fails)
    checked += same("readme", readme, report.README, fails)
    checked += same("report", full, report.REPORT, fails)
    checked += same("page", page, report.PAGE, fails)

    # RAW_RUNS.md hashes manifest.json, which carries the commit sha; mask that one hash so the check holds across commits.
    mask = lambda t: re.sub(r"(results/manifest\.json\]\([^)]*\) \| `)[0-9a-f]{64}", r"\1-", t)
    raw = raw_runs.OUTPUT.read_text() if raw_runs.OUTPUT.exists() else ""
    if mask(raw) != mask(raw_runs.render()): fails.append("raw runs: docs/RAW_RUNS.md differs from what the data give (run make report)")
    checked += 1
    checked += same("dataset", dataset.text(ds), dataset.PATH, fails)  # the cached table equals what the rows give
    fails += configs.check_registry(dataset.keys(ds))  # every config with rows is registered, and every entry has rows
    # Tooltip wrappers preserve the original catalog cell text and values.
    catalog_page = re.sub(r'<(abbr|tspan) class="notation-use"[^>]*>(.*?)</\1>', r'\2', page)
    for e in dataset.catalog_rows(ds):  # ... and the page shows every registry entry with its dataset numbers
        mark = (f"{e['task_complete']}/{e['n']} complete ({e['hidden_pass']}/{e['n']} hidden)"
                if e["rule"] == dataset.RULE_COMPLETE else f"{e['passes']}/{e['n']}")
        cell = f">{html.escape(e['display'])}</td><td>{html.escape(e['what'])}</td><td>{mark}</td>"
        if cell not in catalog_page: fails.append(f"page: {e['id']} is missing from the page's Everything we tried section, or its pass count differs from the dataset")
    checked += 1

    allow = json.load(open(ALLOW))
    literals = template_literals()
    stray, used = stray_literals(literals, allow)
    fails += stray
    fails += [f"docs/audit_allow.json: category {a['name']!r} no longer matches the templates" for i, a in enumerate(allow) if i not in used]

    fails += page_numbers_missing(page, allow)
    print(f"audit: {checked} generated files compared, {len(literals)} template literals checked, {len(literals) - len(stray)} in {len(allow)} allowed categories")
    if fails:
        print("\n".join("FAIL " + f for f in fails)); sys.exit(1)
    print("audit: OK, every committed number matches the data")


if __name__ == "__main__":
    main()
