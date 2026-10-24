"""make audit: fail if any committed number disagrees with the data. No model calls, standard library only.

1. results/summary.json, results/report/tables.md and results/manifest.json equal what analysis.summarize computes now
   from the graded rows.
2. Every chart in results/report/charts equals what analysis.charts draws from that summary.
3. results/report/luna_rescue.md equals the table analysis.luna_rescue computes from the appendix rows.
4. README.md, docs/REPORT.md and results/report/page.html equal what analysis.report renders from the template.
5. The templates (README and page) hold no number of its own outside {{facts}}, code spans and link targets, except the constants listed
   with a reason in docs/audit_allow.json. Each allowed literal must still occur on a line containing its context.
"""
import html, json, os, re, sys

from analysis import charts, configs, dataset, luna_rescue, report, summarize
from analysis.summarize import ROOT, RES

ALLOW = os.path.join(ROOT, "docs", "audit_allow.json")
NUM = re.compile(r"(?<![\w.\-/^])(\d+(?:[.,]\d+)*)(?!\d|\.\d|[\-‑]\w)")


def same(label, want, path, fails):
    have = open(path).read() if os.path.exists(path) else None
    if have != want:
        fails.append(f"{label}: {os.path.relpath(path, ROOT)} differs from what the data give (run make report)")
    return 1


def template_literals():
    """(template, line number, literal, line) for every number the templates write themselves."""
    out = []
    for path in (report.README_TEMPLATE, report.TEMPLATE, report.PAGE_TEMPLATE):
        for no, line in enumerate(open(path).read().split("\n"), 1):
            t = re.sub(r"\{\{chart:[^|}]*\|", " ", line)  # keep chart captions in the scan
            t = re.sub(r"\{\{[^{}]*\}\}", " ", t)
            t = re.sub(r"`[^`]*`", " ", t)
            t = re.sub(r"\]\([^)]*\)", "]", t)
            t = re.sub(r"<[^>]*>", " ", t)
            t = re.sub(r"^(\s*)\d+\. ", r"\1", t)  # ordered-list markers
            out += [(os.path.relpath(path, ROOT), no, m.group(1), line) for m in NUM.finditer(t)]
    return out


def main():
    fails = []; checked = 0
    s, tab, man = summarize.build()
    ds = dataset.build(s)
    checked += same("summary", json.dumps(s, indent=1), os.path.join(RES, "summary.json"), fails)
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
    readme, full, page = report.render()
    checked += same("readme", readme, report.README, fails)
    checked += same("report", full, report.REPORT, fails)
    checked += same("page", page, report.PAGE, fails)

    checked += same("dataset", dataset.text(ds), dataset.PATH, fails)  # the cached table equals what the rows give
    fails += configs.check_registry(dataset.keys(ds))  # every config with rows is registered, and every entry has rows
    for e in ds["rows"]:  # ... and the page shows every one of them, with the dataset's numbers, in the "Everything we tried" section
        if e["set"] != "all runs": continue
        cell = f">{html.escape(e['display'])}</td><td>{html.escape(e['what'])}</td><td>{e['passes']}/{e['n']}</td>"
        if cell not in page: fails.append(f"page: {e['id']} is missing from the page's Everything we tried section, or its pass count differs from the dataset")
    checked += 1

    allow = json.load(open(ALLOW))
    used = set(); stray = []
    for path, no, lit, line in template_literals():
        hit = [i for i, a in enumerate(allow) if lit in a["literals"] and a["context"] in line]
        if hit: used.update(hit)
        else: stray.append(f"{path}:{no}: literal {lit!r} is not a {{{{fact}}}} and not in docs/audit_allow.json")
    fails += stray
    fails += [f"docs/audit_allow.json: entry {a['context']!r} no longer matches the template" for i, a in enumerate(allow) if i not in used]

    print(f"audit: {checked} generated files compared, {len(template_literals())} template literals checked against {len(allow)} allowed constants")
    if fails:
        print("\n".join("FAIL " + f for f in fails)); sys.exit(1)
    print("audit: OK, every committed number matches the data")


if __name__ == "__main__":
    main()
