"""Render the README, full report and page from dataset.json and the unchanged templates.

All numeric facts and table cells are prepared by analysis.dataset; this module only formats markup.
"""
import html, json, os, re
from analysis import charts, configs, dataset, og, page as pagew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
TEMPLATE = os.path.join(ROOT, "docs", "report.tmpl.md")
PAGE_TEMPLATE = os.path.join(ROOT, "docs", "page.tmpl.md")
README = os.path.join(ROOT, "README.md")
README_TEMPLATE = os.path.join(ROOT, "docs", "readme.tmpl.md")
REPORT = os.path.join(ROOT, "docs", "REPORT.md")
PAGE = os.path.join(RES, "report", "page.html")
CHARTS = os.path.join(RES, "report", "charts")
PAGE_DIR = os.path.join(ROOT, "docs", "page")

class Facts(dict):
    def __init__(self, *args, used=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.used = used

    def __getitem__(self, k):
        value = super().__getitem__(k)
        if self.used is not None: self.used.add(k)
        return value

    def get(self, k, default=None):
        return self[k] if k in self else default

    def __missing__(self, k):
        raise KeyError(f"template uses unknown fact {{{{{k}}}}}")

need = dataset.need

def facts(ds):
    return Facts(ds["facts"])

def md_table(head, rows):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(map(str, r)) + " |" for r in rows])

def tables_md(ds):
    tables = {name: md_table(**spec) if isinstance(spec, dict) else spec for name, spec in ds["tables"].items()}
    for key in ("grok_summary", "grok_verdict"):
        if key in ds["facts"]: tables[key] = ds["facts"][key]
    return tables

# ---------- rendering ----------

PLACE = re.compile(r"\{\{([^{}]+)\}\}")


def fill(text, F, T, mode, chart_bodies=None):
    def sub(m):
        k = m.group(1)
        if k.startswith("table:"): return T[k[6:]] if mode == "readme" else to_html(T[k[6:]], dots=k.startswith("table:grok_"))
        if k.startswith("chart:"):
            f, cap = k[6:].split("|", 1)
            if mode == "readme": return f"![{cap}](results/report/charts/{f})"
            body = (chart_bodies if chart_bodies is not None else charts.build())[f].strip()
            body = body.replace(charts.token_style(), "")
            width = re.search(r"viewBox=['\"]0 0 ([\d.]+)", body).group(1)
            return f'<figure><div class="svgscroll" style="--natural-width:{width}px">{body}</div><figcaption>{html.escape(cap)}. <span class="scroll-hint">Scroll sideways on narrow screens.</span></figcaption></figure>'
        return F[k]
    lines = []
    for line in text.split("\n"):
        tag = line.split(" ", 1)[0]
        if tag in ("@readme", "@page"):  # a bare tag is an empty line in that output
            if mode != tag[1:]: continue
            line = line[len(tag) + 1:]
        lines.append(line)
    plain = lambda m: m.group(0) if m.group(1).split(":")[0] in ("table", "chart") else F[m.group(1)]
    return PLACE.sub(sub, PLACE.sub(plain, "\n".join(lines)))  # facts first, so chart captions can hold them


def inline(t):
    """Markdown inline spans to HTML: code, bold, links. Relative links point into the repository, which a reader of the page may not have, so they render as code."""
    out = []; parts = re.split(r"(`[^`]+`)", t)
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append(f"<code>{html.escape(p[1:-1])}</code>"); continue
        if p.startswith("<figure>") or p.startswith("<div") or p.startswith("<h2") or p.startswith("<script") or p.startswith("<p class"):
            out.append(p); continue
        p = html.escape(p, quote=False)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', p)
        p = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: m.group(1) if m.group(1).startswith("<code>") else f"<code>{m.group(1)}</code>" if "/" in m.group(1) or "." in m.group(1) else m.group(1), p)
        out.append(p)
    return "".join(out)


def config_cell(cell):
    """A cell that is exactly a config name gets the same family dot as in the Results table."""
    name = html.unescape(re.sub(r"<[^>]+>", "", cell)).strip()
    known = {configs.display(c): c for c in [*pagew.GROK_ORDER, *pagew.ORDER]}
    return pagew.dot(pagew.FAM(known[name]), known[name].startswith("grok")) + cell if name in known else cell


def to_html(md, dots=False):
    """Enough markdown for this one template: headings, paragraphs, lists, tables, fenced code, blockquotes and raw HTML blocks."""
    L = md.split("\n"); i = 0; out = []
    while i < len(L):
        line = L[i]
        if not line.strip(): i += 1; continue
        if line.startswith("<"):  # raw HTML block (figures, page-only markup) runs to the next blank line
            j = i
            while j < len(L) and L[j].strip(): j += 1
            out.append("\n".join(L[i:j])); i = j; continue
        if line.startswith("```"):
            j = i + 1
            while not L[j].startswith("```"): j += 1
            out.append("<pre><code>" + html.escape("\n".join(L[i + 1:j])) + "</code></pre>"); i = j + 1; continue
        m = re.match(r"(#{1,3}) (.*)", line)
        if m:
            lv = len(m.group(1)); txt = m.group(2); hid = re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>|`", "", txt.lower())).strip("-")
            out.append(f"<h{lv} id=\"{hid}\">{inline(txt)}</h{lv}>"); i += 1; continue
        if line.startswith("|"):
            j = i
            while j < len(L) and L[j].startswith("|"): j += 1
            cells = [[c.strip() for c in r.strip().strip("|").split(" | ")] for r in L[i:j]]
            head, body = cells[0], cells[2:]
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            trs = "".join("<tr>" + "".join(f"<td>{(config_cell if dots else str)(configs.cell_markup(inline(c)))}</td>" for c in r) + "</tr>" for r in body)
            out.append(f"<div class=\"tablewrap\"><table class=\"sortable\"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>"); i = j; continue
        if line.startswith("> "):
            j = i; buf = []
            while j < len(L) and L[j].startswith(">"): buf.append(L[j][1:].strip()); j += 1
            out.append(f"<div class=\"rule\">{inline(' '.join(buf))}</div>"); i = j; continue
        if re.match(r"(- |\d+\. )", line):
            tag = "ol" if line[0].isdigit() else "ul"; items = []; j = i
            while j < len(L) and L[j].strip():
                if re.match(r"(- |\d+\. )", L[j]): items.append(re.sub(r"^(- |\d+\. )", "", L[j]))
                else: items[-1] += " " + L[j].strip()
                j += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(t)}</li>" for t in items) + f"</{tag}>"); i = j; continue
        j = i; buf = []
        while j < len(L) and L[j].strip() and not re.match(r"(#|\||- |\d+\. |```|> |<)", L[j]): buf.append(L[j]); j += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>"); i = j
    return "\n".join(out)


def data_block(ds, s, used, T, page_tmpl, chart_bodies, W):
    """The page's embedded data: a projection of dataset.json holding every fact, row, table cell and chart label the page shows,
    plus the explorer's points. The script reads numbers from here; the page's visible numbers must all be found in it (audit)."""
    tables = sorted(set(re.findall(r"\{\{table:([^}]+)\}\}", page_tmpl)))
    keep = ("id", "config", "set", "rule", "passes", "n", "pass_rate", "ci95", "usd_per_pass", "median_s", "task_complete")
    block = {"facts": {k: ds["facts"].get(k) if hasattr(ds["facts"], "get") else ds["facts"][k] for k in sorted(used) if k in ds["facts"]},
             "rows": [{k: r[k] for k in keep if k in r} for r in ds["rows"]],
             "tables": {k: T[k] for k in tables if k in T},
             "charts": {name: [html.unescape(x) for x in re.findall(r"<text[^>]*>([^<]*)</text>", body)] for name, body in sorted(chart_bodies.items()) if name in re.findall(r"\{\{chart:([^|]+)\|", page_tmpl)},
             "widgets": {k: nodes for k, v in sorted(W.items()) if (nodes := [html.unescape(x).strip() for x in re.findall(r">([^<>]+)<", v) if re.search(r"\d", x)])},
             "explorer": pagew.explorer_data(s)}
    return json.dumps(block, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")


def render(used_facts=None):
    """(README text, full report text, page HTML), all rendered from the dataset and the templates."""
    ds = dataset.read(); s = dataset.view(ds)
    if used_facts is None: used_facts = set()  # the page always tracks the facts it shows: they go into its data block
    F = facts(ds); T = tables_md(ds); chart_bodies = charts.build(ds)
    F.update(set_label=configs.set_label("rescue set"), set_label_title=configs.set_label("rescue set", capital=True))
    readme = fill(open(README_TEMPLATE).read(), F, T, "readme", chart_bodies).strip() + "\n"
    up = lambda m: m.group(0) if re.match(r"https?:|#|mailto:", m.group(2)) else f"{m.group(1)}(../{m.group(2)})"
    report = re.sub(r"(\]|!\[[^\]]*\])\(([^)\s]+)\)", up, fill(open(TEMPLATE).read(), F, T, "readme", chart_bodies).strip() + "\n")  # it lives in docs/
    page_tmpl = open(PAGE_TEMPLATE).read()
    # Track page dependencies only: README/report facts and unused widgets do not count.
    ds["facts"] = Facts(ds["facts"], used=used_facts)
    s["facts"] = ds["facts"]
    F = Facts(F, used=used_facts)
    chart_names = set(re.findall(r"\{\{chart:([^|]+)\|", page_tmpl))
    chart_bodies = charts.build(ds, names=chart_names)
    widget_names = {k[2:] for k in PLACE.findall(page_tmpl) if k.startswith("w_")}
    W = pagew.widgets(s, need, ds, names=widget_names)
    body = fill(page_tmpl, Facts({**F, **{"w_" + k: v for k, v in W.items()}, "w_everything": ""}, used=used_facts), T, "page", chart_bodies)  # first pass: the page without the section
    W["everything"] = configs.section(body, ds, ROOT, chart_bodies)  # every registered config, with 'where it appears' read from that first pass
    W["grok_catalog"] = configs.section(body, ds, ROOT, chart_bodies, grok_only=True)
    body = fill(page_tmpl, Facts({**F, **{"w_" + k: v for k, v in W.items()}}, used=used_facts), T, "page", chart_bodies)
    body = pagew.notation_tooltips(body, ds)
    shell = open(os.path.join(PAGE_DIR, "shell.html")).read()
    script = open(os.path.join(PAGE_DIR, "sort.js")).read().strip().replace("__RESCUE_SET_LABEL__", json.dumps(configs.set_label("rescue set")))
    block = data_block(ds, s, used_facts, T, page_tmpl, chart_bodies, W)
    page = shell.replace("__CSS__", open(os.path.join(PAGE_DIR, "style.css")).read().strip()).replace("__OG_DESC__", html.escape(og.takeaway(ds["facts"]))).replace("__BODY__", body.replace("__DATA__", block)).replace("__JS__", script)
    return readme, report, page


def main():
    used = set()
    readme, report, page = render(used_facts=used)
    # The facts the page renders; landcheck flags any that a later branch stops rendering.
    open(dataset.FACTS_USED, "w").write(json.dumps(sorted(used), indent=0) + "\n")
    open(README, "w").write(readme); open(REPORT, "w").write(report)
    os.makedirs(os.path.dirname(PAGE), exist_ok=True); open(PAGE, "w").write(page)
    print(f"report -> README.md ({len(readme):,} chars), docs/REPORT.md ({len(report):,} chars), {os.path.relpath(PAGE, ROOT)} ({len(page):,} chars)")


if __name__ == "__main__":
    main()
