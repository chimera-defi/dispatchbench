"""The one registry of every config that has rows under results/: display name, family, category, source file, one-line description.

Names come from here (analysis.labels.DISP delegates to display()). The page's "Everything we tried" section is built from it
(section()), and analysis.audit fails when a config with rows is missing from it, when an entry has no rows, or when the page does not
show every entry. Add new rows here when a new run lands. Standard library only, no model calls.

Entry: (source, name, category, what). Family comes from the name (Claude: haiku/sonnet; Codex: everything else).
A source is one results file; the same name in two sources is two entries (a pilot haiku-low is not the main-run haiku-low)."""
import html, os, re


SET_LABELS = {"rescue set": "luna-miss set", "rescue arms": "luna-miss pipelines",
              "rescue pipeline": "luna-miss pipeline", "main ladder": "main ladder", "L7 set": "L7 set"}


def set_label(key, capital=False):
    label = SET_LABELS.get(key, key)
    return label[0].upper() + label[1:] if capital else label


# Meanings may interpolate existing dataset facts; prose and tooltips share them.
NOTATION = {
    "low/medium/high": "The effort setting after the model name.",
    "⚡": "Codex priority tier costs {fm_mult} list price at the same model and effort.",
    "-bare": "Codex's system prompt and tool text are trimmed.",
    "→": "A second step in a pipeline.",
    "H": "Haiku at low effort (haiku-low).",
    "→H fail": "Haiku fixes answers only when the problem's worked examples fail.",
    "→H all": "Haiku checks and fixes every answer.",
    "→retry": "The same model tries again if the examples fail.",
    "retry": "The same model tries again if the examples fail.",
    "plan→": "Haiku writes a plan before the named model answers.",
    "†": "An exploratory config added after the main run.",
    "★": "A Winner pick. Star-shaped chart markers identify astra.",
    "~": "Codex cost estimated from tokens and list prices.",
    "–": "No Claude step in this row. In failure grids, the config was not run.",
    "$0": "The Haiku step never ran, or subscription quota covers the Codex call.",
    "≥N%": "The lower {ci_level} bound when every attempt passed.",
    "pass@1": "The share of attempts passing every hidden test on the first answer.",
    "p90": "The time within which {p90_percent} of calls finished.",
    "L1–L7": "Difficulty rungs run from easiest to hardest. The hardest rung uses a separate set.",
    "noshell B1/B2": "Luna prompt variants remove shell context. The latter adds a detailed reasoning summary.",
    "purple dot": "A pipeline using two models.",
    "family dots": "Dot colours distinguish Haiku, Sonnet and Codex.",
    "●": "Haiku's chart marker.",
    "■": "Sonnet's chart marker.",
    "▲": "Luna's chart marker. Triangle direction indicates effort.",
    "◆": "Sol's chart marker.",
    "E/M/H": "Estimated LeetCode difficulty: Easy, Medium or Hard.",
}


SOURCES = {  # source id -> files under results/ that hold its rows
    "main": ["2026-10-22b-function.jsonl"], "agentic": ["2026-10-22b-agentic.jsonl"], "trim": ["2026-10-22b-trim.jsonl"],
    "rescue": ["appendix/luna_rescue.jsonl"], "pilot": ["2026-10-22-pilot.jsonl"], "pilot-agentic": ["2026-10-22-pilot-agentic.jsonl"],
    "harness-bias": ["appendix/harness_bias.jsonl", "appendix/codex_harness.jsonl"]}  # the last two land with the codex-own-harness branch
CATEGORIES = ["main ladder", "exploratory", "fast mode and xhigh", "rescue pipeline", "repo tasks", "trim", "pilot", "harness-bias", "low context"]

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
    ("sol61-high-fast", "sol61-high on Codex priority tier (fast mode). Same model and effort, about twice the price."),
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
add("harness-bias", "harness-bias",
    ("haiku-low / Claude harness", "Harness-bias check: haiku-low on hard problems through our one-shot runner"),
    ("haiku-low / Codex harness", "Harness-bias check: haiku-low in Claude Code (Codex-built runner)"),
    ("luna-low / Claude harness", "Harness-bias check: luna-low through our one-shot runner"),
    ("luna-low / Codex harness", "Harness-bias check: luna-low in Codex CLI (Codex-built runner)"),
    ("sol61-medium / Codex harness", "Harness-bias check: sol61-medium in Codex CLI (Codex-built runner)"))
LOW_CONTEXT = {("main", "luna-low-bare"),
               *(("rescue", c) for c in ("luna-medium-bare", "luna-high-bare", "luna-low-noshell-B1", "luna-low-noshell-B2")),
               *(("trim", f"{model}/{variant}") for model in ("luna", "terra")
                 for variant in ("nofeat", "noshell", "mininst", "noctx", "nodoc")),
               ("pilot", "codex-low-lean"), ("pilot", "codex-bare")}
REGISTRY = {(s, n): {"source": s, "name": n, "category": "low context" if (s, n) in LOW_CONTEXT else c, "what": w} for s, n, c, w in R}
assert len(REGISTRY) == len(R), "duplicate registry entry"


def display(c):
    """Display name of a config: fast mode (priority tier) gets a lightning suffix."""
    if ' / ' in c:
        model, harness = c.split(' / ', 1)
        if harness == 'Claude harness': return model + ' / our one-shot runner'
        if harness == 'Codex harness':
            return model + (' / Claude Code (agent)' if model.startswith('haiku') else ' / Codex CLI (agent)')
    return c[:-5] + " ⚡" if c.endswith("-fast") else c


def family(name):
    return "Claude" if name.split("-")[0] in ("haiku", "sonnet") or name.startswith("pipeline C") else "Codex"


# Page names of the rescue-set rows (arms and baselines), shared by every chart and table.
RESCUE_NAMES = {c: display(c) for c in ("luna-low", "luna-high-bare", "haiku-low", "haiku-medium", "haiku-high", "sonnet-medium", "sol61-medium",
                                   "sol61-high", "sol61-high-fast", "astra-medium", "astra-medium-fast", "sol56-high", "luna56-high", "luna56-low")}
for builder in ("sol61-high", "astra-medium", "luna-low", "luna-high-bare"):
    RESCUE_NAMES[builder + "+haiku-on-fail"] = display(builder) + " → Haiku if samples fail"
    if builder + "-fast" in RESCUE_NAMES:
        RESCUE_NAMES[builder + "-fast+haiku-on-fail"] = display(builder + "-fast") + " → Haiku if samples fail"
RESCUE_NAMES.update({"haiku-low-plan+luna-low": "Haiku plan → luna-low", "haiku-low-plan+luna-high-bare": "Haiku plan → luna-high-bare",
             "luna-high-bare+retry-on-fail": "luna-high-bare → retry if samples fail",
             "luna-low+haiku-review-all": "luna-low → Haiku fixes all", "luna-high-bare+haiku-review-all": "luna-high-bare → Haiku fixes all"})


def entry(source, name):
    """Registry entry plus derived fields: id, display, family, files."""
    e = REGISTRY[(source, name)]
    return dict(e, id=f"{source}/{name}", display=display(name), family=family(name), files=["results/" + f for f in SOURCES[source]])


def check_registry(keys):
    """keys = {(source, name)} that have rows (dataset.keys()). Failures: rows but no entry, or an entry with no rows."""
    fails = [f"configs: {s}/{n} has rows in results/ but is not in analysis/configs.py" for s, n in sorted(set(keys) - set(REGISTRY))]
    return fails + [f"configs: registry entry {s}/{n} has no rows" for s, n in sorted(set(REGISTRY) - set(keys))]


def _seen(text, name):
    return re.search(r"(?<![\w/+→-])" + re.escape(display(name)) + r"(?![\w/]|-\w)", text) is not None


def where(e, rest, chart_bodies):
    """Where the page shows this config outside the section, decided by source: main-run names are searched in the page text, repo-task
    names in the agentic chart, rescue arms by their page label. Pilot, trim and harness-bias configs are never claimed elsewhere."""
    if e["source"] == "main" and _seen(rest, e["config"]): return "charts and tables"
    if e["source"] == "agentic":
        return "repo-task chart" if e["config"] in (chart_bodies.get("agentic.svg") or "") else "only here"
    if e["source"] == "rescue":
        from analysis import page  # lazy: page imports labels, which imports this module
        shown = page.NAME.get(e["config"])
        if shown and shown in rest: return "charts and tables"
    return "only here"


def section(rest, ds, root, chart_bodies=None):
    """The collapsible "Everything we tried" block, one row per registry entry from the dataset catalog. rest = the page HTML without
    this block, used for the 'where it appears' column."""
    from analysis.dataset import catalog_rows, usd as money
    chart_bodies = chart_bodies or {}
    by = {}
    for r in catalog_rows(ds):
        by.setdefault(r["category"], []).append(r)
    head = "".join(f"<th>{h}</th>" for h in ("name", "what it was", "pass", "$ per pass", "median s", "spend", "where it appears"))
    out = ["<details><summary>Everything we tried</summary>", "<ul class=\"tight small\"><li>Every config with rows in results/, grouped by kind.</li>"
           "<li>Each row combines that config's runs within its category.</li>"
           "<li>Codex $ are list-price estimates. ~ here means some rows have no cost.</li>"
           "<li>Hover over a name for its source file.</li></ul>"]
    for cat in CATEGORIES:
        es = by.pop(cat, [])
        if not es: continue
        label = "Low context (prompt or tool text trimmed)" if cat == "low context" else set_label(cat)
        out.append(f"<details><summary>{html.escape(label)}: {ds['categories'][cat]['n_configs']} configs, {money(ds['categories'][cat]['spend'])} spent</summary><div class=\"tablewrap\"><table class=\"sortable\"><thead><tr>{head}</tr></thead><tbody>")
        for e in es:
            tilde = "~" if e["unknown_usd"] else ""
            out.append(f"<tr><td title=\"{html.escape(', '.join(e['files']))}\">{html.escape(e['display'])}</td><td>{html.escape(e['what'])}</td><td>{e['passes']}/{e['n']}</td>"
                       f"<td>{tilde}{money(e['usd_per_pass'])}</td><td>{e['median_s']:.1f}</td><td>{tilde}{money(e['spend'])}</td><td>{where(e, rest, chart_bodies)}</td></tr>")
        out.append("</tbody></table></div></details>")
    out += [f"<details><summary>unregistered</summary><p>{html.escape(r['display'])} ({r['source']})</p></details>" for es in by.values() for r in es]
    return "\n".join(out + ["</details>"])


LC = {"p01_overlap_minutes": "Medium", "p02_squash": "Easy", "p03_ledger": "Medium", "p04_taller_within": "Medium",
      "p05_pass_route": "Medium", "p06_calc": "Hard", "p07_weighted_distance_sums": "Hard", "p08_recur": "Medium",
      "p09_k_machine_schedule": "Hard", "p10_avoid_count": "Hard", "p11_best_average": "Hard", "p12_sheet": "Hard",
      "p13_xor_ring": "Hard", "p14_bounce_board": "Hard", "p15_paint_erase": "Hard"}
