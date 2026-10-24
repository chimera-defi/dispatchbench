"""Render the README, full report and page from dataset.json and the unchanged templates.

All numeric facts and table cells are prepared by analysis.dataset; this module only formats markup.
"""
import html, os, re
from analysis import charts, configs, dataset, page as pagew

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
    def __missing__(self, k):
        raise KeyError(f"template uses unknown fact {{{{{k}}}}}")

need = dataset.need

def facts(ds):
    return Facts(ds["facts"])

def md_table(head, rows):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(map(str, r)) + " |" for r in rows])

def tables_md(ds):
    return {name: md_table(**spec) if isinstance(spec, dict) else spec for name, spec in ds["tables"].items()}

# ---------- rendering ----------

PLACE = re.compile(r"\{\{([^{}]+)\}\}")


def fill(text, F, T, mode, chart_bodies=None):
    def sub(m):
        k = m.group(1)
        if k.startswith("table:"): return T[k[6:]] if mode == "readme" else to_html(T[k[6:]])
        if k.startswith("chart:"):
            f, cap = k[6:].split("|", 1)
            if mode == "readme": return f"![{cap}](results/report/charts/{f})"
            body = (chart_bodies if chart_bodies is not None else charts.build())[f].strip()
            width = re.search(r"\bwidth=['\"](\d+)['\"]", body).group(1)
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


def to_html(md):
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
            trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
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


def render():
    """(README text, full report text, page HTML), all rendered from the dataset and the templates."""
    ds = dataset.read(); s = dataset.view(ds)
    F = facts(ds); T = tables_md(ds); chart_bodies = charts.build(ds)
    readme = fill(open(README_TEMPLATE).read(), F, T, "readme", chart_bodies).strip() + "\n"
    up = lambda m: m.group(0) if re.match(r"https?:|#|mailto:", m.group(2)) else f"{m.group(1)}(../{m.group(2)})"
    report = re.sub(r"(\]|!\[[^\]]*\])\(([^)\s]+)\)", up, fill(open(TEMPLATE).read(), F, T, "readme", chart_bodies).strip() + "\n")  # it lives in docs/
    W = pagew.widgets(s, need, ds)
    page_tmpl = open(PAGE_TEMPLATE).read()
    body = fill(page_tmpl, Facts({**F, **{"w_" + k: v for k, v in W.items()}, "w_everything": ""}), T, "page", chart_bodies)  # first pass: the page without the section
    W["everything"] = configs.section(body, ds, ROOT, chart_bodies)  # every registered config, with 'where it appears' read from that first pass
    body = fill(page_tmpl, Facts({**F, **{"w_" + k: v for k, v in W.items()}}), T, "page", chart_bodies)
    shell = open(os.path.join(PAGE_DIR, "shell.html")).read()
    page = shell.replace("__CSS__", open(os.path.join(PAGE_DIR, "style.css")).read().strip()).replace("__BODY__", body).replace("__JS__", open(os.path.join(PAGE_DIR, "sort.js")).read().strip())
    return readme, report, page


def main():
    readme, report, page = render()
    open(README, "w").write(readme); open(REPORT, "w").write(report)
    os.makedirs(os.path.dirname(PAGE), exist_ok=True); open(PAGE, "w").write(page)
    print(f"report -> README.md ({len(readme):,} chars), docs/REPORT.md ({len(report):,} chars), {os.path.relpath(PAGE, ROOT)} ({len(page):,} chars)")


if __name__ == "__main__":
    main()
