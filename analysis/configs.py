"""The one registry of every config that has rows under results/: display name, family, category, source file, one-line description.

Names come from here (analysis.labels.DISP delegates to display()). The page's "Everything we tried" section is built from it
(section()), and analysis.audit fails when a config with rows is missing from it, when an active entry has no rows, or when the page does not
show every active entry. Grok declarations activate when their first rows arrive. Standard library only, no model calls.

Entry: (source, name, category, what). Family comes from the name (Claude, Codex or Grok).
A source is one results file; the same name in two sources is two entries (a pilot haiku-low is not the main-run haiku-low)."""
import html, json, os, re


SET_LABELS = {"rescue set": "retest set", "rescue arms": "retest pipelines",
              "rescue pipeline": "retest pipeline", "main ladder": "main ladder", "L7 set": "L7 set"}


def set_label(key, capital=False):
    label = SET_LABELS.get(key, key)
    return label[0].upper() + label[1:] if capital else label


def cell_markup(markup):
    """Keep an estimate prefix and its dollar value on the same line."""
    return re.sub(r"~\s*\$[\d.,]+", lambda m: '<span style="white-space:nowrap">' + m[0] + '</span>', markup)


# Meanings may interpolate existing dataset facts; prose and tooltips share them.
NOTATION = {
    "⚡": "Fast mode: {fm_mult} list price at the same model and effort.",
    "-bare": "Codex's system prompt and tool text are trimmed.",
    "H": "Haiku at low effort (haiku-low).",
    "→H fail": "Haiku fixes answers only when a sample test fails.",
    "→H all": "Haiku checks and fixes every answer.",
    "→retry": "The same model tries again if a sample test fails.",
    "plan→": "Haiku writes a plan before the named model answers.",
    "†": "An exploratory config added after the main run.",
    "✓ pick": "A Winner pick.",
    "~": "Codex cost estimated from tokens and list prices.",
    "–": "No Claude step, unavailable cost, or an unrun failure-grid cell.",
    "$0": "The Haiku step never ran, or subscription quota covers the Codex call.",
    "≥N%": "The lower {ci_level} bound when every attempt passed.",
    "slow-call time": "The time within which {p90_percent} of calls finished.",
}


SOURCES = {  # source id -> files under results/ that hold its rows
    "main": ["2026-10-22b-function.jsonl", "2026-10-26-grok-function.jsonl", "2026-10-28-grok-spectrum-function.jsonl",
             "2026-10-28-terra-function.jsonl", "2026-10-28-devin-function.jsonl", "2026-11-01-hetzner-function.jsonl", "2026-11-02-terra-priority-function.jsonl", "2026-11-02-terra-l7-fast-function.jsonl",
             "2026-11-22-inkling-function.jsonl", "2026-11-22-inkling-retry-function.jsonl", "2026-11-25-agy-function.jsonl", "2026-11-25-devin-flash-function.jsonl", "2026-11-25-inkling-colab-l4-function.jsonl"], "agentic": ["2026-10-22b-agentic.jsonl"], "trim": ["2026-10-22b-trim.jsonl"],
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
    ("sol61-high", "gpt-6.1-sol, high effort (default tier)"), ("astra-medium", "gpt-6-astra, medium effort"),
    ("terra61-low", "gpt-6.1-terra, low effort (added 2026-10-28, operator request; main ladder p01–p12, 5 repeats)"),
    ("terra61-high", "gpt-6.1-terra, high effort (added 2026-10-28, operator request; main ladder p01–p12, 5 repeats)"),
    ("terra56-low", "gpt-5.6-terra, low effort. Extra data: one repeat on p01–p12 (the operator meant gpt-6.1-terra)"),
    ("terra56-high", "gpt-5.6-terra, high effort. Extra data: one repeat on p01–p12 (the operator meant gpt-6.1-terra)"))
ONE_REPEAT = ("terra56-low", "terra56-high")  # gpt-5.6-terra, one repeat on p01-p12: extra data, listed in tables only, never charted
FIRST_GROK_FILE = "results/2026-10-26-grok-function.jsonl"  # the earlier 2-repeat run on p01-p06; history, never edited
GROK_PARTIAL = ("grok47-medium",)  # p01-p06 only (PLAN.md deviation 23): in tables, not on charts
CHART_HIDDEN = ONE_REPEAT + GROK_PARTIAL
GROK_CONFIGS = ("grok47-low", "grok47-medium", "grok47-high", "grok47fast-low")
add("main", "exploratory", *((c,
    f"Grok {'grok-4.7-build-fast' if c.startswith('grok47fast') else 'grok-4.7'}, {c.rsplit('-', 1)[1]} effort; "
    "grok CLI, measured total_cost_usd; exploratory, added 2026-10-26 at operator request; "
    + ("function track p01–p06 (L1–L3) only, not extended (PLAN.md deviation 23); 6 of 12 problems" if c == "grok47-medium" else
       "function track p01–p12 (L1–L6), 2026-10-28 full spectrum: 5 repeats per problem (L2–L3 had been shortened to 2 repeats on 2026-10-26)")) for c in GROK_CONFIGS))
DEVIN_CONFIGS = ("devin16slow-default",)  # free tier, 1 repeat, no token data: never on a $ chart, never in the Winner or frontier
add("main", "exploratory", ("devin16slow-default",
    "Devin swe-1-6-slow (the only model the free tier allows), default effort; devin CLI, no token or cost data; exploratory, added 2026-10-28 at operator request; "
    "function track p01–p12, 1 repeat (PLAN.md deviation 24)"))
DEVIN_FLASH = ("devinflash-medium",)  # free tier, 5 repeats, no token data; SWE-2.1 itself needs Pro (PLAN.md deviation 28)
add("main", "exploratory", ("devinflash-medium",
    "Devin swe-2-flash-medium (free tier; NOT SWE-2.1, which the Free plan refuses), default effort; devin CLI, no token or cost data; exploratory, added 2026-11-25 at operator request; "
    "function track p01–p12, 5 repeats per problem (PLAN.md deviation 28)"))
GEMINI_CONFIGS = ("hydrogen-low", "hydrogen-medium", "hydrogen-high", "gemini38flash-low", "neon-low", "neon-medium", "neon-high")  # agy subscription: tokens reported, no list price, so never on a $ chart, in the Winner or the frontier
AGY_OTHER = ("agy-sonnet46-default", "agy-opus46-default", "agy-gptoss120b-medium")  # other vendors' models through the same agy login: the same quota stopped them too
AGY_CONFIGS = GEMINI_CONFIGS + AGY_OTHER
GEMINI_NOTE = "partial: the account quota for agy ran out, n per cell shown; tokens reported, no dollars"
AGY_NAMES = {"hydrogen": "Google Gemini 4 Hydrogen", "neon": "Google Gemini 4 Neon", "gemini38flash": "Google Gemini 3.8 Flash", "agy-sonnet46": "Claude Sonnet 4.6 (Thinking)", "agy-opus46": "Claude Opus 4.6 (Thinking)", "agy-gptoss120b": "GPT-OSS 120B"}
add("main", "exploratory", *((c, f"{AGY_NAMES[c.rsplit('-', 1)[0]]}, {c.rsplit('-', 1)[1]} setting; Antigravity CLI (agy), headless, "
    "signed-in subscription: reports tokens, no dollars; exploratory, added 2026-11-25 at operator request; function track p01–p12, partial: the run stopped on a 429 quota error (PLAN.md deviation 29)") for c in AGY_CONFIGS))
HETZNER_CONFIGS = ("hetzner-qwen36", "hetzner-qwen38")
add("main", "exploratory", *((c,
    "Hetzner " + model + "; OpenAI-compatible streaming API, measured input/output tokens; free experimental tier, no published list price; "
    "exploratory calibration, function track p01–p12, 1 repeat (2026-11-01)")
    for c, model in zip(HETZNER_CONFIGS, ("Qwen/Qwen3.6-35B-A3B-FP8", "Qwen/Qwen3.8-27B"))))
INKLING_CONFIGS = ("inkling2mini-default", "inkling2mini-medium16k", "inkling2mini-low16k", "inkling2mini-default24k")
INKLING_RUNS = {c: w for c, w in zip(INKLING_CONFIGS, (
    "Inkling 2 Mini IQ4_NL GGUF, default effort, 12288-token cap: the frozen primary run on p01–p15",
    "same model, medium effort, 16384-token cap: secondary retry of the tasks the primary run left capped",
    "same model, low effort, 16384-token cap: secondary retry of the tasks still capped",
    "same model, default effort, 24576-token cap: secondary retry of the tasks still capped"))}
add("main", "exploratory", *((c, "Inkling 2 Mini, llama.cpp b12600 on a local CPU (i7-8700); local CPU model, no list price, cost estimated from box-hours; exploratory, "
    + INKLING_RUNS[c]) for c in INKLING_CONFIGS))
INKLING_LADDER = "inkling2mini-ladder"  # the secondary retry ladder as one lane: a task passes if any stage passed it, its time adds the stages' time
add("main", "exploratory", (INKLING_LADDER, "Inkling 2 Mini retry ladder, secondary: the primary run, then medium 16384, low 16384 and default 24576 retries of the tasks it left capped; "
    "a task passes if any stage passed it and its time is the sum over the stages; llama.cpp b12600 on a local CPU, no list price, cost estimated from box-hours; exploratory"))
INKLING_PRIMARY = INKLING_CONFIGS[0]
INKLING_STAGES = INKLING_CONFIGS[1:]  # raw retry stages: shown only through the ladder lane
BOX_EUR_PER_MONTH = 52.17  # Hetzner Oct 2026 invoice, auction box eth2-3 (the i7-8700): EUR 50.47 server plus EUR 1.70 primary IPv4
BOX_HOURS_PER_MONTH = 744  # 31 days
BOX_EUR_PER_HOUR = round(BOX_EUR_PER_MONTH / BOX_HOURS_PER_MONTH, 4)  # 0.0701
EUR_USD = 1.0939  # ECB euro foreign exchange reference rate, 2026-11-23 (https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml)
EUR_USD_DATE = "2026-11-23"
BOX_USD_PER_HOUR = BOX_EUR_PER_HOUR * EUR_USD  # about 0.0767
BOX_NOTE = f"Estimated from box-hours: wall time at ${BOX_USD_PER_HOUR:.4f} an hour, from the eth2-3 bill."
# Colab L4 lane: the same model on a GPU, one lane of its own. Not in INKLING_CONFIGS: that tuple is the CPU retry ladder and is priced from box-hours.
COLAB_CONFIG = "inkling2mini-colab-l4"
COLAB_CLI = "llama.cpp-cuda"  # distinct from the CPU lane's "llama.cpp", which marks box-hour pricing
COLAB_COST_KIND = "colab-units"
COLAB_UNITS_PER_HOUR = 2.33  # `colab usage` while the L4 ran, 2026-11-25
COLAB_USD_PER_UNIT = 9.99 / 100  # pay-as-you-go list price, third-party reported, not verified on Google's page
COLAB_NOTE = (f"Estimated from compute units: wall time x {COLAB_UNITS_PER_HOUR} units an hour x ${COLAB_USD_PER_UNIT:.4f} a unit. The list price is third-party reported and unverified; "
              "the units here came bundled in a Google AI plan, so the real marginal cost was zero until they run out.")
COLAB_UNITS_BEFORE, COLAB_UNITS_AFTER = 80.00, 76.70  # `colab usage` balance around setup, debugging and the run (3.30 units in all)
COLAB_USD_PER_HOUR = COLAB_UNITS_PER_HOUR * COLAB_USD_PER_UNIT  # about 0.233
ESTIMATED_COST_KINDS = ("box-hours", COLAB_COST_KIND)  # priced from a rate, not metered: no Codex spend, not in spend totals
add("main", "exploratory", (COLAB_CONFIG, "Inkling 2 Mini, Colab L4 (23 GB), llama.cpp b12600 CUDA 12.8, same IQ4_NL GGUF as the CPU lane, -ngl 99, default effort, 12288-token cap, one repeat; "
    "cost estimated from Colab compute units, no list price paid; exploratory"))


def colab_usd(wall_s):
    return wall_s / 3600 * COLAB_USD_PER_HOUR


def est_usd(r):
    """Estimated dollars of a row priced from a rate: Colab compute units for the Colab lane, box-hours for the CPU lanes."""
    return colab_usd(r["wall_s"]) if r["config"] == COLAB_CONFIG else r["wall_s"] / 3600 * BOX_USD_PER_HOUR


INKLING_SHOWN = (INKLING_PRIMARY, INKLING_LADDER)  # the two Inkling lanes that join tables and charts, like the Hetzner lanes
FREE_TIER_CONFIGS = DEVIN_CONFIGS + DEVIN_FLASH + AGY_CONFIGS + HETZNER_CONFIGS + INKLING_CONFIGS + (INKLING_LADDER, COLAB_CONFIG)  # Inkling's box-hour estimate is not a list price: it is priced only in the explorer. Others: no published $ comparison: off all $ charts, Winner and frontier
CHART_HIDDEN = CHART_HIDDEN + FREE_TIER_CONFIGS
HETZNER_NOTE = "exploratory calibration, 1 repeat, free tier, measured tokens"
DEVIN_NOTE = "1 repeat, free tier, no token data"
DEVIN_FLASH_NOTE = "5 repeats, free tier, no token data"
DEVIN_GROUP = "Devin (free tier, 1 repeat)"  # legend group, table group heading and grid column title
DEVIN_UPGRADE_ERROR = "Error: Upgrade to Pro to access this model (https://devin.ai/pricing)"  # verbatim from PLAN.md deviation 24
DEVIN_STAGE2_MIN = 9  # PLAN.md deviation 24: stage 2 (repeats 2-5) runs only if stage 1 passes at least 9 of 12
add("main", "fast mode and xhigh",
    ("sol61-high-fast", "sol61-high on Codex priority tier (fast mode). Same model and effort, about twice the price."),
    ("astra-medium-fast", "astra-medium on the Codex priority tier (fast mode)"),
    ("terra61-low-fast", "terra61-low on the Codex priority tier (fast mode); exploratory, main ladder and L7"),
    ("terra61-high-fast", "terra61-high on the Codex priority tier (fast mode); exploratory, main ladder only"), ("sol61-xhigh", "gpt-6.1-sol at xhigh effort"))
add("rescue", "rescue pipeline",
    ("luna-low-noshell-B1", "Arm B1: luna-low without shell, nudged to list edge cases and trace the sample tests first"),
    ("luna-low-noshell-B2", "Arm B2: B1 plus a detailed reasoning summary"), ("luna-low-selftest", "Arm C: luna-low with shell on, told to test its code first"),
    ("luna-medium-bare", "Arm D: luna-medium, stripped harness"), ("luna-high-bare", "Arm D: luna-high, stripped harness"),
    ("luna-low+haiku-low-repair", "Arm E (original run, prompt not kept): luna-low answers, haiku-low reviews and repairs"),
    ("haiku-low-plan+luna-low", "Arm F: haiku-low writes a plan, luna-low builds from it"),
    ("haiku-low-plan+luna-high-bare", "Arm F: haiku-low plans, luna-high (stripped) builds"),
    ("luna-high-bare+haiku-on-fail", "Arm G: luna-high builds; haiku-low repairs only if a sample test fails"),
    ("luna-high-bare+retry-on-fail", "Arm G: luna-high builds; luna-high retries only if a sample test fails"),
    ("luna-low+haiku-on-fail", "Arm G: luna-low builds; haiku-low repairs only if a sample test fails"),
    ("astra-medium+haiku-on-fail", "Arm G: astra-medium builds; haiku-low repairs only if a sample test fails"),
    ("sol61-high+haiku-on-fail", "Arm G: sol61-high builds; haiku-low repairs only if a sample test fails"),
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
    ("haiku-low / Claude harness", "Harness-bias check: haiku-low on hard problems on Claude's one-shot bench"),
    ("haiku-low / Codex harness", "Harness-bias check: haiku-low in Claude Code (Codex's bench)"),
    ("luna-low / Claude harness", "Harness-bias check: luna-low on Claude's one-shot bench"),
    ("luna-low / Codex harness", "Harness-bias check: luna-low in Codex CLI (Codex's bench)"),
    ("sol61-medium / Codex harness", "Harness-bias check: sol61-medium in Codex CLI (Codex's bench)"))
LOW_CONTEXT = {("main", "luna-low-bare"),
               *(("rescue", c) for c in ("luna-medium-bare", "luna-high-bare", "luna-low-noshell-B1", "luna-low-noshell-B2")),
               *(("trim", f"{model}/{variant}") for model in ("luna", "terra")
                 for variant in ("nofeat", "noshell", "mininst", "noctx", "nodoc")),
               ("pilot", "codex-low-lean"), ("pilot", "codex-bare")}
DECLARED = {(s, n): {"source": s, "name": n, "category": "low context" if (s, n) in LOW_CONTEXT else c, "what": w} for s, n, c, w in R}
assert len(DECLARED) == len(R), "duplicate registry entry"


def active_registry(keys):
    """Declare the parallel Grok lane ahead of its rows; the active catalog contains observed entries only."""
    return {key: e for key, e in DECLARED.items() if key not in {("main", c) for c in GROK_CONFIGS} or key in keys}


def _main_keys():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    keys = set()
    for name in SOURCES["main"]:
        path = os.path.join(root, "results", name)
        if os.path.exists(path):
            with open(path) as rows:
                keys.update(("main", json.loads(line)["config"]) for line in rows)
    return keys


REGISTRY = active_registry(_main_keys())


def display(c):
    """Display name of a config: fast mode (priority tier) gets a lightning suffix."""
    pilot_names = {"codex-low": "sol61-low-prio (pilot first run)",
                   "codex-medium": "sol61-medium-prio",
                   "codex-low-lean": "sol61-low-prio-lean",
                   "codex-bare": "sol61-low-prio-bare"}
    if c in pilot_names: return pilot_names[c]
    if c == COLAB_CONFIG: return "Inkling 2 Mini, Colab L4"
    if c in globals().get("RESCUE_NAMES", {}): return RESCUE_NAMES[c]
    if ' / ' in c:
        model, harness = c.split(' / ', 1)
        if harness == 'Claude harness': return model + " / Claude's bench"
        if harness == 'Codex harness':
            return model + (" / Codex's bench (Claude Code)" if model.startswith('haiku') else " / Codex's bench (Codex CLI)")
    return c[:-5] + " ⚡" if c.endswith("-fast") else c


def low_context(config, source="main"):
    """Use the registry category when grouping trimmed-context variants."""
    return REGISTRY.get((source, config), {}).get("category") == "low context"


def family(name):
    if name.startswith("grok"): return "Grok"
    if name.startswith("devin"): return "Devin"
    if name.startswith("hetzner"): return "Hetzner"
    if name.startswith(("hydrogen", "gemini", "neon")): return "Gemini"
    if name.startswith("agy-"): return "Antigravity"
    if name.startswith("inkling"): return "Inkling"
    return "Claude" if name.split("-")[0] in ("haiku", "sonnet") or name.startswith("pipeline C") else "Codex"


# Page names of the rescue-set rows (arms and baselines), shared by every chart and table.
RESCUE_NAMES = {c: display(c) for c in ("luna-low", "luna-high-bare", "haiku-low", "haiku-medium", "haiku-high", "sonnet-medium", "sol61-medium",
                                   "sol61-high", "sol61-high-fast", "astra-medium", "astra-medium-fast", "sol56-high", "luna56-high", "luna56-low")}
for builder in ("sol61-high", "astra-medium", "luna-low", "luna-high-bare"):
    RESCUE_NAMES[builder + "+haiku-on-fail"] = display(builder) + "→H fail"
    if builder + "-fast" in RESCUE_NAMES:
        RESCUE_NAMES[builder + "-fast+haiku-on-fail"] = display(builder + "-fast") + "→H fail"
RESCUE_NAMES.update({"haiku-low-plan+luna-low": "plan→luna-low", "haiku-low-plan+luna-high-bare": "plan→luna-high-bare",
             "luna-high-bare+retry-on-fail": "luna-high-bare→retry",
             "luna-low+haiku-review-all": "luna-low→H all", "luna-high-bare+haiku-review-all": "luna-high-bare→H all"})


PLAIN_PIPELINE_DUPLICATES = tuple(builder + "+haiku-on-fail" for builder in (
    "sol61-high", "astra-medium", "sol61-high-fast", "astra-medium-fast"))


def entry(source, name):
    """Registry entry plus derived fields: id, display, family, files."""
    e = REGISTRY[(source, name)]
    return dict(e, id=f"{source}/{name}", display=display(name), family=family(name), files=["results/" + f for f in SOURCES[source]])


def check_registry(keys):
    """keys = {(source, name)} that have rows (dataset.keys()). Failures: rows but no entry, or an active entry with no rows."""
    fails = [f"configs: {s}/{n} has rows in results/ but is not in analysis/configs.py" for s, n in sorted(set(keys) - set(REGISTRY))]
    return fails + [f"configs: registry entry {s}/{n} has no rows" for s, n in sorted(set(REGISTRY) - set(keys))]


def _seen(text, name):
    return re.search(r"(?<![\w/+→-])" + re.escape(display(name)) + r"(?![\w/]|-\w)", text) is not None


def where(e, rest, chart_bodies):
    """Where the page shows this config outside the section, decided by source: main-run names are searched in the page text, repo-task
    names in the repo-task chart, rescue arms by their page label. Pilot, trim and harness-bias configs are never claimed elsewhere."""
    if e["config"] in INKLING_CONFIGS + (INKLING_LADDER, COLAB_CONFIG): return "Inkling section (#inkling), charts and tables"  # its own section; the config names are not in the page text
    if e["source"] == "main" and _seen(rest, e["config"]): return "charts and tables"
    if e["source"] == "agentic":
        repo = re.search(r'<div class="compact-bars" id="repo-chart">.*?</details>', rest, re.S)  # the page's repo-task bars and table
        shown = e["config"] in (chart_bodies.get("agentic.svg") or "") or (repo is not None and _seen(repo[0], e["config"]))
        return "repo-task chart" if shown else "only here"
    if e["source"] == "rescue":
        from analysis import page  # lazy: page imports labels, which imports this module
        shown = page.NAME.get(e["config"])
        if shown and shown in rest: return "charts and tables"
    return "only here"


def section(rest, ds, root, chart_bodies=None, grok_only=False, entries=None):
    """Render selected catalog entries; rest supplies the 'where it appears' column."""
    from analysis.dataset import catalog_rows, median_seconds, usd as money, price_text
    chart_bodies = chart_bodies or {}
    by = {}
    grok_categories = set()
    for r in (catalog_rows(ds) if entries is None else entries):
        if r["config"] in GROK_CONFIGS: grok_categories.add(r["category"])
        if grok_only is not None and (r["config"] in GROK_CONFIGS) != grok_only: continue
        by.setdefault(r["category"], []).append(r)
    out = ["<details><summary>Evidence by config</summary>",
           '<p>Rows pool recorded runs; scores can differ from the main ladder.</p>',
           '<p>Archived runs: <a href="https://github.com/chimera-defi/dispatchbench/blob/main/docs/RAW_RUNS.md">raw results and provenance</a>.</p>']
    for cat in CATEGORIES:
        if grok_only is False and cat in grok_categories:
            out.append('<p>Grok: <a href="#grok">see the Grok section</a></p>')
        es = by.pop(cat, [])
        if not es: continue
        complete = all(e["rule"] == "task_complete" for e in es)
        head = "".join(f"<th>{h}</th>" for h in ("name", "task complete (hidden in brackets)" if complete else "pass",
                                               "$ per complete task" if complete else "$ per pass", "median s", "spend", "where it appears"))
        label = "Low context (prompt or tool text trimmed)" if cat == "low context" else set_label(cat)
        totals = {"n_configs": len(es), "spend": sum(e["spend"] for e in es if e["cost_kind"] not in ESTIMATED_COST_KINDS)}
        out.append(f"<details><summary>{html.escape(label)}: {totals['n_configs']} configs, {'~' if any(e['cost_kind'] == 'proxy' for e in es) else ''}{money(totals['spend'])} spent</summary><div class=\"tablewrap\"><table class=\"sortable\"><thead><tr>{head}</tr></thead><tbody>")
        for e in es:
            spend = None if e["unknown_usd"] else e["spend"]
            proxy = "~" if e["cost_kind"] == "proxy" else ""
            mark = (f"{e['task_complete']}/{e['n']} complete ({e['hidden_pass']}/{e['n']} hidden)"
                    if e["rule"] == "task_complete" else f"{e['passes']}/{e['n']}")
            out.append(f"<tr><td title=\"{html.escape(', '.join(e['files']))}\">{html.escape(e['display'])}</td><td>{mark}</td>"
                       f"<td>{cell_markup((proxy if e['usd_per_pass'] is not None else '') + price_text(e, e['usd_per_pass']))}</td><td>{median_seconds(e):.1f}</td><td>{cell_markup((proxy if spend is not None else '') + price_text(e, spend))}</td><td>{where(e, rest, chart_bodies)}</td></tr>")
        out.append("</tbody></table></div></details>")
    out += [f"<details><summary>unregistered</summary><p>{html.escape(r['display'])} ({r['source']})</p></details>" for es in by.values() for r in es]
    if not grok_only:
        out.append('<p class="small">Category totals cover the rows listed here.</p>')
    return "\n".join(out + ["</details>"])


LC = {"p01_overlap_minutes": "Medium", "p02_squash": "Easy", "p03_ledger": "Medium", "p04_taller_within": "Medium",
      "p05_pass_route": "Medium", "p06_calc": "Hard", "p07_weighted_distance_sums": "Hard", "p08_recur": "Medium",
      "p09_k_machine_schedule": "Hard", "p10_avoid_count": "Hard", "p11_best_average": "Hard", "p12_sheet": "Hard",
      "p13_xor_ring": "Hard", "p14_bounce_board": "Hard", "p15_paint_erase": "Hard"}


# Explorer and static speed-chart rules, read by analysis.page and written into dataset.json design.explorer
TIE_ABS_S, TIE_REL = 0.5, 0.05  # a speed change below both 0.5 s and 5% is a tie
PASS_FLOORS = (0.75, 0.9)       # the explorer's "frontier over pass rate >=" choices; the last is the pre-registered MIN_PASS
