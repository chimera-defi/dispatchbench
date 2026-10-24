"""The one registry of every config that has rows under results/: display name, family, category, source file, one-line description.

Names come from here (analysis.labels.DISP delegates to display()). The page's "Everything we tried" section is built from it
(section()), and analysis.audit fails when a config with rows is missing from it, when an entry has no rows, or when the page does not
show every entry. Add new rows here when a new run lands. Standard library only, no model calls.

Entry: (source, name, category, what). Family comes from the name (Claude: haiku/sonnet; Codex: everything else).
A source is one results file; the same name in two sources is two entries (a pilot haiku-low is not the main-run haiku-low)."""
import html, json, os, re, statistics

RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")  # summarize imports labels imports this module: no import of summarize at load time

SOURCES = {  # source id -> (file under results/, how a row is graded)
    "main": "2026-10-22b-function.jsonl", "agentic": "2026-10-22b-agentic.jsonl", "trim": "2026-10-22b-trim.jsonl",
    "rescue": "appendix/luna_rescue.jsonl", "pilot": "2026-10-22-pilot.jsonl", "pilot-agentic": "2026-10-22-pilot-agentic.jsonl",
    "harness-bias": "appendix/harness_bias.jsonl"}
CATEGORIES = ["main ladder", "exploratory", "fast mode and xhigh", "rescue pipeline", "repo tasks", "trim", "pilot", "harness-bias"]

R = []
def add(source, category, *pairs):
    R.extend((source, n, category, w) for n, w in pairs)

add("main", "main ladder",
    ("haiku-low", "Claude Haiku, low effort, tools off"), ("haiku-medium", "Claude Haiku, medium effort"), ("sonnet-medium", "Claude Sonnet, medium effort"),
    ("luna-low", "Codex gpt-6-luna, low effort, stock Codex harness"), ("luna-medium", "Codex gpt-6-luna, medium effort"),
    ("sol61-medium", "Codex gpt-6.1-sol, medium effort"))
add("main", "exploratory",
    ("haiku-high", "Claude Haiku, high effort (added after the main run)"), ("luna-high", "gpt-6-luna, high effort (added after the main run)"),
    ("luna-low-bare", "luna-low with the Codex system prompt and tool features stripped (trim level noshell)"),
    ("luna56-low", "gpt-5.6-luna, low effort"), ("luna56-high", "gpt-5.6-luna, high effort"), ("sol56-high", "gpt-5.6-sol, high effort"),
    ("sol61-high", "gpt-6.1-sol, high effort (default tier)"), ("astra-medium", "gpt-6-astra, medium effort"))
add("main", "fast mode and xhigh",
    ("sol61-high-fast", "sol61-high on the Codex priority tier (fast mode): same model and effort, about twice the price"),
    ("astra-medium-fast", "astra-medium on the Codex priority tier (fast mode)"), ("sol61-xhigh", "gpt-6.1-sol at xhigh effort"))
add("rescue", "rescue pipeline",
    ("luna-low-noshell-B1", "Arm B1: luna-low without shell, nudged to list edge cases and trace the examples first"),
    ("luna-low-noshell-B2", "Arm B2: B1 plus a detailed reasoning summary"), ("luna-low-selftest", "Arm C: luna-low with shell on, told to test its code first"),
    ("luna-medium-bare", "Arm D: luna-medium, stripped harness"), ("luna-high-bare", "Arm D: luna-high, stripped harness"),
    ("luna-low+haiku-low-repair", "Arm E (original run, prompt not kept): luna-low answers, haiku-low reviews and repairs"),
    ("haiku-low-plan+luna-low", "Arm F: haiku-low writes a plan, luna-low builds from it"),
    ("haiku-low-plan+luna-high-bare", "Arm F: haiku-low plans, luna-high (stripped) builds"),
    ("luna-high-bare+haiku-on-fail", "Arm G: luna-high builds; haiku-low repairs only if the statement's examples fail"),
    ("luna-high-bare+retry-on-fail", "Arm G: luna-high builds; luna-high retries only if the examples fail"),
    ("luna-low+haiku-on-fail", "Arm G: luna-low builds; haiku-low repairs only if the examples fail"),
    ("astra-medium+haiku-on-fail", "Arm G: astra-medium builds; haiku-low repairs only if the examples fail"),
    ("sol61-high+haiku-on-fail", "Arm G: sol61-high builds; haiku-low repairs only if the examples fail"),
    ("luna-high-bare+haiku-review-all", "Arm G: luna-high builds; haiku-low reviews every answer"),
    ("luna-low+haiku-review-all", "Arm G: luna-low builds; haiku-low reviews every answer (arm E rerun from committed code)"))
add("agentic", "repo tasks",
    ("haiku-low", "Repo tasks with tools: Claude Haiku, low"), ("haiku-high", "Repo tasks: Claude Haiku, high"), ("sonnet-medium", "Repo tasks: Claude Sonnet, medium"),
    ("luna-low", "Repo tasks: gpt-6-luna, low"), ("sol61-medium", "Repo tasks: gpt-6.1-sol, medium"), ("sol61-high", "Repo tasks: gpt-6.1-sol, high"),
    ("astra-medium", "Repo tasks: gpt-6-astra, medium"))
add("trim", "trim",
    ("luna/base", "Codex harness floor probe: luna, stock harness"), ("luna/nofeat", "luna, tool features stripped"), ("luna/noshell", "luna, features, shell and base instructions stripped"),
    ("luna/mininst", "luna, minimal instructions (one call)"), ("luna/noctx", "luna, no project context (one call)"), ("luna/nodoc", "luna, no docs (one call)"),
    ("terra/base", "terra, stock harness"), ("terra/nofeat", "terra, tool features stripped"), ("terra/noshell", "terra, features and shell stripped"),
    ("terra/mininst", "terra, minimal instructions (one call)"), ("terra/noctx", "terra, no project context (one call)"), ("terra/nodoc", "terra, no docs (one call)"),
    ("haiku", "haiku-low through the same probe, tools off (reference)"))
add("pilot", "pilot",
    ("haiku-low", "Pilot (well-known problems): Claude Haiku, low"), ("haiku-medium", "Pilot: Claude Haiku, medium"), ("sonnet-low", "Pilot: Claude Sonnet, low"),
    ("sonnet-medium", "Pilot: Claude Sonnet, medium"), ("haiku-low-agent", "Pilot: Haiku low with tools on"), ("sonnet-medium-agent", "Pilot: Sonnet medium with tools on"),
    ("codex-low", "Pilot: gpt-6.1-sol, low, priority tier"), ("codex-medium", "Pilot: gpt-6.1-sol, medium, priority tier"),
    ("codex-low-lean", "Pilot: gpt-6.1-sol low with --ignore-user-config only"), ("codex-bare", "Pilot: gpt-6.1-sol low, stripped harness, priority tier"),
    ("astra-low", "Pilot: gpt-6-astra, low"), ("luna-low", "Pilot: gpt-6-luna, low, priority tier"), ("luna-low-defa", "Pilot: gpt-6-luna low, default tier"),
    ("luna-high-prio", "Pilot: gpt-6-luna high, priority tier"), ("terra56-low-prio", "Pilot: gpt-5.6-terra low, priority tier"),
    ("sol6-low-prio", "Pilot: gpt-6-sol low, priority tier"), ("sol61-low-prio", "Pilot: gpt-6.1-sol low, priority tier"),
    ("sol61-low-defa", "Pilot: gpt-6.1-sol low, default tier (the fast-mode control)"))
add("pilot-agentic", "pilot",
    ("pipeline A", "Pilot repo task: gpt-6.1-sol builds, a reviewer checks"), ("pipeline B", "Pilot repo task: gpt-6-luna builds, a reviewer checks"),
    ("pipeline C", "Pilot repo task: Claude Sonnet builds, no review"))
REGISTRY = {(s, n): {"source": s, "name": n, "category": c, "what": w} for s, n, c, w in R}
assert len(REGISTRY) == len(R), "duplicate registry entry"


def display(c):
    """Display name of a config: fast mode (priority tier) gets a lightning suffix."""
    return c[:-5] + " ⚡" if c.endswith("-fast") else c


def family(name):
    return "Claude" if name.split("-")[0] in ("haiku", "sonnet") or name.startswith("pipeline C") else "Codex"


def _fast(r):
    return json.load(open(os.path.join(RES, "prices.json")))["fast_mode_multiplier"] if str(r.get("service_tier", "")).startswith("priority") else 1


def _rows():
    """{(source, name): [(passed, usd or None, seconds)]} from every results file. Warmup rows are not counted."""
    from analysis.summarize import PRICES, cost, load
    out = {}
    def put(src, name, ok, usd, sec): out.setdefault((src, name), []).append((bool(ok), usd, sec))
    for src in ("main", "agentic", "trim", "pilot"):
        for r in load(os.path.join(RES, SOURCES[src])):
            if r.get("phase") == "warmup": continue
            c = r.get("cost_usd") if str(r.get("model", "")).startswith("claude") else cost(r); c = c * _fast(r) if c is not None and src == "pilot" else c
            put(src, r["config"], r.get("passed", r.get("hidden_pass")), c, r["wall_s"])
    for r in load(os.path.join(RES, SOURCES["rescue"])):
        put("rescue", r["config"], r["passed"], r.get("cost_usd"), r["wall_s"])
    for r in load(os.path.join(RES, SOURCES["pilot-agentic"])):
        c = r.get("builder_cost_usd")
        if c is None and r["builder_kind"] == "codex":
            p = PRICES[r["builder"]]; c = ((r["builder_in"] - r["builder_cached"]) * p["input"] + r["builder_cached"] * p["cached_input"] + r["builder_out"] * p["output"]) / 1e6
        rv = (r.get("review") or {}).get("cost_usd") or 0
        put("pilot-agentic", f"pipeline {r['pipeline']}", r["hidden_pass"], None if c is None else c + rv, r["builder_wall_s"])
    for r in load(os.path.join(RES, SOURCES["harness-bias"])):
        put("harness-bias", r.get("config") or r.get("harness"), r.get("passed"), r.get("cost_usd"), r.get("wall_s") or 0)
    return out


def stats():
    """One dict per registry entry with its rows: pass x/n, $ per pass, median seconds, spend."""
    rows = _rows(); out = []
    for key, rr in rows.items():
        e = dict(REGISTRY.get(key, {"source": key[0], "name": key[1], "category": "?", "what": "(not in analysis/configs.py)"}))
        k = sum(p for p, _, _ in rr); known = [u for _, u, _ in rr if u is not None]
        e.update(passes=k, n=len(rr), spend=sum(known), unknown_usd=len(rr) - len(known), median_s=statistics.median(s for _, _, s in rr),
                 usd_per_pass=(sum(known) / k if k and not len(known) < len(rr) else None), file="results/" + SOURCES[key[0]], family=family(key[1]))
        out.append(e)
    return out


def check_registry():
    """Failures: a config with rows but no entry, or an entry with no rows."""
    have = set(_rows()); fails = [f"configs: {s}/{n} has rows in results/{SOURCES[s]} but is not in analysis/configs.py" for s, n in sorted(have - set(REGISTRY))]
    return fails + [f"configs: registry entry {s}/{n} has no rows" for s, n in sorted(set(REGISTRY) - have)]


def _seen(text, name):
    return re.search(r"(?<![\w/+→-])" + re.escape(display(name)) + r"(?![\w/]|-\w)", text) is not None


def where(e, rest):
    """Where the page shows this entry outside the section: the page text is searched for its display name, but only main, agentic and
    rescue entries can match (pilot and trim names collide with main-run names, so they are never claimed as shown elsewhere)."""
    if e["source"] in ("main", "agentic") and _seen(rest, e["name"]): return "charts and tables"
    if e["source"] == "rescue":
        from analysis import page  # lazy: page imports labels, which imports this module
        shown = page.NAME.get(e["name"])
        if shown and shown in rest: return "charts and tables"
    return "only here"


def money(v):
    return "–" if v is None else f"${v:,.2f}" if v >= 1 else f"${v:.4f}"


def section(rest):
    """The collapsible "Everything we tried" block. rest = the page's HTML without this block, used for the 'where' column."""
    st = stats(); by = {}
    for e in st: by.setdefault(e["category"], []).append(e)
    head = "".join(f"<th>{h}</th>" for h in ("name", "what it was", "pass", "$ per pass", "median s", "spend", "where it appears"))
    out = ["<details><summary>Everything we tried</summary>", "<p class=\"small\">Every config with rows in results/, grouped by kind. Codex $ are list-price proxies; ~ = some rows have no cost. "
           "Source file per group is in the first row's tooltip.</p>"]
    for cat in CATEGORIES:
        es = by.pop(cat, [])
        if not es: continue
        tot = sum(e["spend"] for e in es)
        out.append(f"<details><summary>{html.escape(cat)}: {len(es)} configs, {money(tot)} spent</summary><div class=\"tablewrap\"><table class=\"sortable\"><thead><tr>{head}</tr></thead><tbody>")
        for e in es:
            wh = where(e, rest); tilde = "~" if e["unknown_usd"] else ""
            out.append(f"<tr><td title=\"{html.escape(e['file'])}\">{html.escape(display(e['name']))}</td><td>{html.escape(e['what'])}</td><td>{e['passes']}/{e['n']}</td>"
                       f"<td>{tilde}{money(e['usd_per_pass'])}</td><td>{e['median_s']:.1f}</td><td>{tilde}{money(e['spend'])}</td><td>{wh}</td></tr>")
        out.append("</tbody></table></div></details>")
    out += [f"<details><summary>unregistered</summary><p>{html.escape(display(e['name']))} ({e['source']})</p></details>" for es in by.values() for e in es]
    return "\n".join(out + ["</details>"])
