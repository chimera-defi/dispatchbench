"""Exercise the pending Grok lane without changing any graded results files."""
import copy
import hashlib
import json
import re
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

import pytest

from analysis import charts, configs, dataset, grok, page, report, summarize


class GrokScope(HTMLParser):
    """Count every config occurrence, including attributes and embedded chart/script data."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.elements = []
        self.counts = defaultdict(Counter)

    def check(self, text):
        for config in re.findall(r"grok47[a-z-]*", text):
            section = next((attrs.get("id") for tag, attrs in reversed(self.elements) if tag == "section"), None)
            assert section in {"grok", "fail", "pareto"}, (config, section)
            self.counts[config][section] += 1

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID: self.elements.append((tag, dict(attrs)))
        self.check(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.elements) - 1, -1, -1):
            if self.elements[i][0] == tag:
                del self.elements[i:]
                break

    def handle_data(self, text):
        self.check(text)

    def handle_comment(self, text):
        self.check(text)


@pytest.mark.parametrize("section", ["grok", "fail", "pareto"])
@pytest.mark.parametrize("row", [
    '<tr><td>grok47-low</td></tr>',
    '<tr data-config="grok47-high"><td>Grok</td></tr>',
])
def test_grok_scope_rejects_rows_after_allowed_section(section, row):
    allowed = f'<section id="{section}"><div><table>{row}</table></div></section>'
    GrokScope().feed(allowed)
    for outside in (f'<table>{row}</table>', f'<section id="notes"><table>{row}</table></section>'):
        with pytest.raises(AssertionError):
            GrokScope().feed(allowed + outside)


def test_grok_scope_report_svgs():
    """Grok config names belong on the two report figures and nowhere else in results/report/charts."""
    note = "Grok: black hexagons"
    for path in Path(charts.OUT).glob("*.svg"):
        text = path.read_text()
        found = set(re.findall(r"grok47[a-z-]*", text))
        if path.name in {"pareto.svg", "cost_time.svg"}:
            assert found - set(configs.GROK_PARTIAL) == set(configs.GROK_CONFIGS) - set(configs.GROK_PARTIAL), path.name
            # grok47-medium is named only in the note saying it is not plotted.
            assert text.count("grok47-medium") == 1 and "grok47-medium (p01–p06 only) is not plotted" in text
            assert note in text
        elif path.name == "hero.svg":
            # I: the OG source now shares the explorer's default view, including
            # measured partial runs. Every Grok config is labelled in its title.
            assert found == set(configs.GROK_CONFIGS)
            assert 'class="ex-point"' in text and 'default cost versus pass view' in text
        else:
            assert not found, path.name


def test_grok_scope_generated_page():
    html = Path(report.PAGE).read_text()
    scope = GrokScope()
    scope.feed(html)
    scope.close()
    assert not scope.elements
    assert set(scope.counts) == set(configs.GROK_CONFIGS)
    assert all(set(counts) == {"grok", "fail", "pareto"} for counts in scope.counts.values())
    inventory = html.split('<summary>Everything we tried</summary>')[-1]
    assert 'Grok: <a href="#grok">see the Grok section</a>' in inventory
    assert not any(c in inventory for c in configs.GROK_CONFIGS)
    # Recreate the leaked inventory group on the actual page, after #grok and #fail.
    leaked = ('<details><summary>exploratory: 4 configs</summary><table>'
              '<tr><td>grok47-low</td></tr></table></details>')
    with pytest.raises(AssertionError, match="grok47-low"):
        GrokScope().feed(html.replace('<section class="notes" id="notes">',
                                      '<section class="notes" id="notes">' + leaked))


def test_grok_reach_counts_and_note_follow_source_rows():
    ds = dataset.read()
    source = [json.loads(line) for line in (Path(summarize.RES) / "2026-10-26-grok-function.jsonl").read_text().splitlines()]
    table = ds["tables"]["grok_reach"]
    for cells in table["rows"]:
        rendered = dict(zip(table["head"], cells))
        rows = [r for r in source if r["config"] == rendered["config"]]
        for rung in (1, 2, 3):
            rr = [r for r in rows if r["rung"] == rung]
            assert rendered[f"L{rung}"] == f'{sum(r["passed"] for r in rr)}/{len(rr)}'
    misses = [r for r in source if not r["passed"]]
    assert len(misses) == 3
    assert {(r["problem"], r["rung"]) for r in misses} == {("p06_calc", 3)}
    note = ds["facts"]["grok_reach_note"]
    assert "on p06_calc" in note
    assert "on p06_calc" not in ds["facts"]["grok_summary"]
    assert "(18, 21, 24)" in note and "from 5 to 2 repeats partway through L2" in note
    assert "30 = 6 problems × 5 repeats" in note and "read the rung reached, not the total" in note
    changed = copy.deepcopy(ds["grok_first"])
    for c in configs.GROK_CONFIGS:
        changed["metrics"][c]["n"] = 36
        for rung in changed["repeat_counts"][c].values():
            for p in rung: rung[p] *= 2
    note = grok.reach_note(changed, ds["report"]["grok_first"])
    assert "(36)" in note and "from 10 to 4 repeats" in note


def test_function_rows_loads_separate_grok_file(tmp_path, monkeypatch):
    monkeypatch.setattr(summarize, "RES", str(tmp_path))
    for name, config in zip(configs.SOURCES["main"], ("haiku-low", "grok47-low")):
        (tmp_path / name).write_text(json.dumps({"config": config, "phase": "main"}) + "\n")
    rows = summarize.function_rows()
    assert {r["config"] for r in rows} == {"haiku-low", "grok47-low"}
    assert all(r["phase"] == "main" for r in rows)
    assert next(r for r in rows if r["config"] == "grok47-low")["_file"].endswith("2026-10-26-grok-function.jsonl")


@pytest.mark.parametrize("model", ["grok-4.7", "grok-4.7-build-fast"])
@pytest.mark.parametrize("field", ["cost_usd", "total_cost_usd"])
def test_grok_cost_is_measured_without_a_price_entry(model, field):
    row = {"cli": "grok", "model": model, "config": "grok47fast-low", field: 0.123456,
           "in_tok": 999999, "cached_tok": 0, "out_tok": 999999}
    assert model not in summarize.PRICES
    assert summarize.cost(row) == summarize.cost_uncached(row) == 0.123456
    row.pop(field)
    assert summarize.cost(row) is None


def test_declared_configs_activate_only_with_rows_and_keep_registry_strict():
    existing = set(configs.REGISTRY)
    assert configs.check_registry(existing) == []
    grok_keys = {("main", c) for c in configs.GROK_CONFIGS}
    assert grok_keys <= set(configs.DECLARED)
    assert not grok_keys & set(configs.active_registry(set()))
    assert grok_keys <= set(configs.active_registry(grok_keys))
    missing = next(iter(existing))
    assert configs.check_registry(existing - {missing}) == [
        f"configs: registry entry {missing[0]}/{missing[1]} has no rows"]
    assert configs.family("grok47fast-low") == "Grok"
    assert page.FAM("grok47-low") == charts.FAMILY("grok47-low")
    assert page.FAM("grok47-low") != page.FAM("luna-low")


def test_first_half_rows_render_without_changing_full_ladder(monkeypatch):
    original = [r for r in summarize.function_rows() if r["config"] not in configs.GROK_CONFIGS]
    source = [r for r in original if r["config"] == "haiku-low" and r["phase"] == "main" and r["rung"] <= 3]
    assert len(source) == 30
    rows = []
    for c in configs.GROK_CONFIGS:
        for r in source:
            grok = copy.deepcopy(r)
            grok.update(config=c, cli="grok", model="grok-4.7-build-fast" if c.startswith("grok47fast") else "grok-4.7",
                        effort=c.rsplit("-", 1)[1], phase="main", cli_version="test-grok",
                        ts="2026-10-26T10:00:00Z", key=c + r["key"], cost_usd=0.123456, _file=configs.FIRST_GROK_FILE,
                        passed=c != "grok47-high", outcome="wrong" if c == "grok47-high" else "pass")
            rows.append(grok)
    baseline = dataset.read()
    monkeypatch.setattr(summarize, "function_rows", lambda: original + rows)
    # A fresh report process activates definitions from the newly arrived rows.
    monkeypatch.setattr(configs, "REGISTRY", configs.active_registry({("main", r["config"]) for r in original + rows}))
    summary, tables, manifest = summarize.build()
    ds = dataset.build(summary)
    assert configs.check_registry(dataset.keys(ds)) == []
    assert set(summary["grok"]) == set(configs.GROK_CONFIGS)
    for block in ("configs", "exploratory", "paired", "pareto"):
        assert ds["report"][block] == baseline["report"][block]
    assert not any(c in configs.GROK_CONFIGS for problem in summary["failures"].values() for c in problem["cells"])
    got, base_charts = charts.build(ds), charts.build(baseline)
    assert got.keys() == base_charts.keys()
    for name, body in got.items():
        if name in {"pareto.svg", "cost_time.svg"}:
            assert body != base_charts[name]
            assert "grok47-low" in body and "grok47-high" not in body
            assert "Grok: black hexagons, 6 of 12 problems" in body and "not a like-for-like" not in body
        elif name == "hero.svg":
            assert body != base_charts[name]
            assert "grok47-low" in body and "grok47-high" not in body
            assert 'class="ex-point"' in body
        else:
            assert body == base_charts[name], name
    assert "## Grok (first half, 6 of 12 problems)" in tables
    for c in configs.GROK_CONFIGS:
        assert c in manifest["configs"]
        assert c not in page.ORDER
        assert not any(r["config"] == c and r["set"] in ("main ladder", "rescue set") for r in ds["rows"])
        partial = dataset.get(ds, c, "partial ladder")
        assert partial["n"] == 30 and partial["groups"] == 6
        assert partial["family"] == "Grok" and partial["cost_kind"] == "measured"
        assert partial["spend_grok"] == pytest.approx(30 * 0.123456)
        assert partial["spend_codex"] == partial["spend_claude"] == 0
        assert partial["usd_saved_per_pass"] in (0, None)
        assert set(partial["by_rung"]) == {"L1", "L2", "L3"}
    assert dataset.get(ds, "grok47-high", "partial ladder")["usd_per_pass"] is None
    monkeypatch.setattr(dataset, "read", lambda: ds)
    readme, full, html = report.render()
    assert "## Grok\n" in full and "6 of 12 problems" in full
    assert '<section id="grok">' in html and "6 of 12 problems" in html
    assert "A dash means no attempt, not a failure." in html and "CLI-reported cost; list price not used" in html
    assert all(c in html for c in configs.GROK_CONFIGS)
    scope = GrokScope()
    scope.feed(html)
    assert set(scope.counts) == set(configs.GROK_CONFIGS)
    assert all({"grok", "fail"} <= set(counts) <= {"grok", "fail", "pareto"} for counts in scope.counts.values())
    assert "pareto" in scope.counts["grok47-low"]
    # I: even a config with no passing call appears in the set toggles and
    # unavailable-cost explanation; it must still stay off the dollar plot.
    assert "pareto" in scope.counts["grok47-high"]
    explorer_plot = html.split('id="ex-chart"', 1)[1].split('</div>', 1)[0]
    assert "grok47-high" not in explorer_plot
    assert "Grok" not in "\n".join(l for l in readme.splitlines() if not l.startswith("Total spend, by kind"))  # README shows only the Winner table and the by-kind spend line
    spend = lambda s: "\n".join(l for l in s.splitlines() if "Grok $" not in l)  # the by-kind spend line names Grok's CLI-reported spend
    assert "Grok" not in spend(full.split("## Grok\n")[0])
    assert "Grok" not in full.split("## Can luna")[1]


def test_ladder_profile_stops_at_first_miss_even_if_later_rungs_pass():
    assert grok.profile({"L1": [10, 10], "L2": [10, 10], "L3": [9, 10], "L4": [10, 10]}) == (2, 3)
    assert grok.profile({"L1": [10, 10], "L2": [4, 4], "L3": [4, 4]}) == (3, None)


def test_repository_metrics_keep_failures_costs_and_same_task_scope(tmp_path, monkeypatch):
    def row(c, task, rep, wall, price, passed=True):
        return dict(config=c, cli="grok" if c.startswith("grok") else "claude", task=task,
                    repeat=rep, wall_s=wall, cost_usd=price, turns=rep * 2,
                    hidden_pass=passed, visible_pass=True)
    rows = [row(c, f"t{task}", rep, rep * 100, 0.2,
                not (c == "grok47-low" and task == 4 and rep == 2))
            for c in ("grok47-low", "grok47-high") for task in range(1, 5) for rep in (1, 2)]
    (tmp_path / "2026-10-27-grok-agentic.jsonl").write_text("\n".join(map(json.dumps, rows)))
    baseline = [row("haiku-low", f"t{task}", rep, 25, 0.05) for task in range(1, 5) for rep in (1, 2, 3)]
    baseline.append(row("haiku-low", "outside", 1, 99999, 99999))
    monkeypatch.setattr(summarize, "RES", str(tmp_path))
    monkeypatch.setattr(summarize, "agentic_rows", lambda: baseline)
    comparison = grok.repository_comparison()
    low, high, claude = (comparison["metrics"][c] for c in ("grok47-low", "grok47-high", "haiku-low"))
    assert (low["passes"], low["n"], low["median_s"], low["median_turns"]) == (7, 8, 150, 3)
    assert low["usd_per_pass"] == pytest.approx(1.6 / 7)
    assert high["passes"] == high["n"] == 8
    assert claude["passes"] == claude["n"] == 12 and claude["median_s"] == 25
    assert comparison["total_usd"] == pytest.approx(3.2)
    rendered = grok.repository_section(lambda v: f"${v:.3f}" if v is not None else "–")
    assert "### Repository tasks" in rendered
    assert "7/8" in rendered and "6.00×" in rendered
    assert "a usable fallback" in rendered and "grok47-high 8/8 complete (8/8 hidden)" in rendered
    assert "Claude is faster and cheaper." in rendered
    assert "haiku-low 12/12" in rendered
    assert "not directly comparable" in rendered
    (tmp_path / "2026-10-27-grok-agentic.jsonl").write_text("\n".join(map(json.dumps, rows[:-1])))
    with pytest.raises(AssertionError, match="all 16 preregistered runs"):
        grok.repository_comparison()


def test_comparison_filters_phases_and_prices_codex_fast_tokens(monkeypatch):
    def row(config, phase, rung=1, passed=True, sec=10, cli="codex", measured=None):
        return dict(config=config, phase=phase, problem=f"p0{rung}", rung=rung, repeat=1, passed=passed,
                    wall_s=sec, cli=cli, model="gpt-6-astra", cost_usd=measured,
                    in_tok=1000, cached_tok=500, out_tok=100)
    rows = [row("grok47-high", "main", g, cli="grok", measured=0.1) for g in (1, 2, 3)]
    rows += [row(c, "exploratory", g) for c in ("astra-medium", "astra-medium-fast") for g in (1, 2, 3)]
    rows += [row("astra-medium", phase, sec=999, passed=False) for phase in
             ("warmup", "calibration", "fastmode", "escalation", "hard")]
    rows += [dict(row("astra-medium", "main"), problem="outside-window", wall_s=999)]
    monkeypatch.setattr(summarize, "function_rows", lambda: rows)
    ladder = {f"L{g}": [10, 10] for g in range(1, 7)}
    ds = {"rows": [dict(source="main", set="main ladder", config=c, by_rung=ladder)
                   for c in ("astra-medium", "astra-medium-fast")]}
    lane = {"grok47-high": dict(by_problem={f"p0{g}": 1 for g in (1, 2, 3)},
                              by_rung={f"L{g}": dict(passed=1, n=1) for g in (1, 2, 3)})}
    comparison = grok.build(ds, {"grok": lane})
    normal = comparison["metrics"]["astra-medium"]
    fast = comparison["metrics"]["astra-medium-fast"]
    expected = (500 * summarize.PRICES["gpt-6-astra"]["input"] +
                500 * summarize.PRICES["gpt-6-astra"]["cached_input"] +
                100 * summarize.PRICES["gpt-6-astra"]["output"]) / 1e6
    assert normal["passes"] == normal["n"] == 3 and normal["median_s"] == 10
    assert normal["usd_per_pass"] == pytest.approx(expected)
    assert fast["usd_per_pass"] == pytest.approx(2 * expected)
    assert comparison["metrics"]["grok47-high"]["usd_per_pass"] == pytest.approx(0.1)
    assert comparison["matches"]["grok47-high"] == ["astra-medium", "astra-medium-fast"]


# Fact inventory frozen from main 33afeca, before the readability pass.
# Every original table row retains its config, numbers and profile together.
OLD_GROK_ROWS = """
| grok47-low | L2 | 10/10 | 10/10 | 3/4 | 23/24 | 26.5 | $0.054 | 6 problems | $1.24 |
| grok47-medium | L2 | 10/10 | 7/7 | 3/4 | 20/21 | 32.6 | $0.066 | 6 problems | $1.33 |
| grok47-high | L3 (not run further) | 10/10 | 4/4 | 4/4 | 18/18 | 41.0 | $0.072 | 6 problems | $1.29 |
| grok47fast-low | L2 | 10/10 | 10/10 | 3/4 | 23/24 | 19.4 | $0.11 | 6 problems | $2.56 |
| grok47-low | Claude | haiku-medium | L2 | L3 | 29/30 | 10.6 | $0.0011 | 2.5× | 50.1× |
| grok47-low | Codex | luna-high | L2 | L3 | 24/25 | 9.0 | $0.00092 | 2.9× | 58.7× |
| grok47-medium | Claude | haiku-medium | L2 | L3 | 29/30 | 10.6 | $0.0011 | 3.1× | 61.8× |
| grok47-medium | Codex | luna-high | L2 | L3 | 24/25 | 9.0 | $0.00092 | 3.6× | 72.3× |
| grok47-high | Codex | astra-medium | L6 | none | 30/30 | 12.7 | $0.064 | 3.2× | 1.1× |
| grok47-high | Codex | astra-medium ⚡ | L6 | none | 30/30 | 6.9 | $0.13 | 6.0× | 0.6× |
| grok47-high | Claude | haiku-high | L6 | none | 30/30 | 11.8 | $0.0022 | 3.5× | 33.1× |
| grok47-high | Claude | haiku-low | L4 | L5 | 30/30 | 8.2 | $0.00066 | 5.0× | 109.3× |
| grok47-high | Codex | sol56-high | L6 | none | 30/30 | 10.0 | $0.032 | 4.1× | 2.3× |
| grok47-high | Codex | sol61-high | L6 | none | 30/30 | 16.9 | $0.015 | 2.4× | 4.7× |
| grok47-high | Codex | sol61-high ⚡ | L6 | none | 20/20 | 9.8 | $0.026 | 4.2× | 2.8× |
| grok47-high | Codex | sol61-medium | L5 | L6 | 30/30 | 15.4 | $0.012 | 2.7× | 5.9× |
| grok47-high | Claude | sonnet-medium | L6 | none | 30/30 | 9.5 | $0.010 | 4.3× | 7.2× |
| grok47fast-low | Claude | haiku-medium | L2 | L3 | 29/30 | 10.6 | $0.0011 | 1.8× | 103.4× |
| grok47fast-low | Codex | luna-high | L2 | L3 | 24/25 | 9.0 | $0.00092 | 2.2× | 121.1× |
| grok47-high | 8/8 complete (8/8 hidden) | 442.1 | $0.54 | 9 |
| grok47-low | 8/8 complete (8/8 hidden) | 98.9 | $0.19 | 5 |
| astra-medium | 12/12 complete (12/12 hidden) | 65.6 | $0.45 | 1 |
| haiku-high | 12/12 complete (12/12 hidden) | 58.4 | $0.012 | 10 |
| haiku-low | 12/12 complete (12/12 hidden) | 28.3 | $0.0051 | 5 |
| luna-low | 7/12 complete (12/12 hidden) (under audit) | 24.1 | $0.0056 | 1 |
| sol61-high | 12/12 complete (12/12 hidden) | 117.9 | $0.097 | 1 |
| sol61-medium | 12/12 complete (12/12 hidden) | 84.5 | $0.079 | 1 |
| sonnet-medium | 12/12 complete (12/12 hidden) | 27.7 | $0.054 | 3 |
| grok47-high | astra-medium | 6.74× | 1.20× |
| grok47-high | haiku-high | 7.57× | 44.34× |
| grok47-high | haiku-low | 15.63× | 105.53× |
| grok47-high | luna-low | 18.33× | 95.85× |
| grok47-high | sol61-high | 3.75× | 5.50× |
| grok47-high | sol61-medium | 5.23× | 6.74× |
| grok47-high | sonnet-medium | 15.94× | 9.97× |
| grok47-low | astra-medium | 1.51× | 0.42× |
| grok47-low | haiku-high | 1.69× | 15.55× |
| grok47-low | haiku-low | 3.50× | 37.01× |
| grok47-low | luna-low | 4.10× | 33.62× |
| grok47-low | sol61-high | 0.84× | 1.93× |
| grok47-low | sol61-medium | 1.17× | 2.36× |
| grok47-low | sonnet-medium | 3.57× | 3.50× |
""".strip().splitlines()

# Every original prose claim, including scope, caveats and source names.
OLD_GROK_CLAIMS = (
    # Scoped to the first run by the claims audit (F14): the old text read as the verdict.
    ('In the first run (p01–p06 only), Grok was accurate but slow and mid-priced. grok47-high passed 18 of 18 but took 41 s per call at the '
     'median. Every existing lane at 100% finished in 6.9 to 16.9 s.'),
    ('In this first run, grok47-low, grok47-medium and grok47fast-low each missed one call at L3 (3/4), so the '
     'pre-registered stop rule fired for all three; the full run above supersedes it.'),
    ('In this first run, cost per pass was $0.054 to $0.111. Claude haiku and the Codex luna lanes are under $0.003. Only the '
     'Codex astra lanes cost as much.'),
    ('Totals differ (18, 21, 24) because the run was shortened from 5 to 2 repeats partway through L2 and '
     'extra repeats already run were kept; the earlier full-coverage lanes have 30 = 6 problems × 5 '
     'repeats; read the rung reached, not the total.'),
    # Reworded in plain language; same rule: match on rungs cleared and the first rung with a miss.
    ('A lane is comparable when it clears the same rungs and first misses at the same rung on the '
     '12-problem main ladder. If a Grok config never missed through L3, every lane that clears through L3 '
     'counts, with its later results shown.'),
    ('Same-problem comparisons use p01–p06 (6 of 12 problems), main + exploratory phases only. Warmup, '
     'calibration, fastmode, escalation and hard phases are excluded. In this first run Grok was run only '
     'through L3, so cleared L3 is a floor here; the full-ladder runs above go to L6 (only grok47-medium '
     'stays on p01–p06). CLI-reported cost; list price not used for Grok. Codex dollars '
     'use tokens × list price with the fast-mode multiplier.'),
    ('grok47-high is cheaper per pass than astra-medium ⚡ (fast mode, 2× list price) on functions (0.55×). '
     'grok47-low is cheaper per pass than plain astra-medium on repo tasks (0.42×) while 1.5× slower. '
     'grok47-low takes 0.84× as long as sol61-high on repo tasks. '
     'No Grok config beats a comparable function lane on pass rate. '
     'No Grok config beats a comparable function lane on time.'),
    ('4 tasks (t1_discount, t2_cache_bugs, t3_config_refs, t4_retry_queue); Grok: 2 repeats per task and '
     'config, 4 parallel lanes, tools on, no web or subagents, 1,500 s timeout; all 16 runs retained with '
     'no performance stop rule. Existing lanes: 3 repeats per task; clean-home Codex replacements are used '
     'where available. Hidden tests run after the agent exits.'),
    ('Grok is a usable fallback for these small repo tasks when Codex is out, though Claude is faster and '
     'cheaper: grok47-low 8/8 complete (8/8 hidden) at 98.9 s median, compared with today’s Claude fallback lanes '
     '(haiku-high 12/12 complete (12/12 hidden), haiku-low 12/12 complete (12/12 hidden), sonnet-medium 12/12 complete (12/12 hidden)) at 27.7–58.4 s median.'),
    ('Grok total measured spend: $5.78 of the $15 budget. Grok and Claude costs are CLI-reported; Codex '
     'costs are token-price proxies. Multiples use median wall time and total cost per passing attempt, '
     'respectively. Turns use each CLI’s convention and are not directly comparable across CLIs. This is a '
     'small exploratory sample on a shared host, not a general repo-work guarantee. Sources: '
     '`results/2026-10-22b-agentic.jsonl`, `results/2026-10-25-isolated-agentic.jsonl`, '
     '`results/2026-10-27-grok-agentic.jsonl`.'),
)


# Digests include every byte outside Grok. Re-pinned 2026-10-28 after Grok-only changes outside the section: the shared
# #results/#grok table CSS, the Grok marker shape, the speed chart axis and Grok columns in the fail grid.
# Re-pinned 2026-10-28: everything outside the Grok section changed with the Terra rows (tables, charts, Interesting, equivalents).
# Re-pinned 2026-10-28 for Commit A: Devin rows (tables, fail grid, rung chart, heatmap, catalog), the share-card meta tags in
# the page head, and the relabelled pareto chart labels. The Grok repository-tasks subsection is unchanged.
# E: the page digest also covers the embedded data block, the rule labels and the rule note; REPORT.md carries the rule labels, the rule note, the audit footnote and tokenised figures.
# F: re-pinned for the claims fixes (one repo-task rule, spend by kind, pilot repricing, bucket labels, CI bars, wording rows).
# G: re-pinned for the t1 regrade line and table (repo-task section, outside the Grok section).
# F2: re-pinned after reviewing auxiliary spend, task/run wording, catalog pass rules and the repricing counts; Grok bytes unchanged.
# I: re-pinned for the v6 explorer and Fable theme; old plot data and visible
# facts are separately compared with main 3561692 in test_pareto_explorer.py.
# S1-S4: theme, topbar, explorer fixes
# S5: inline tokens/topbar CSS
# P4: P4a_prose - Winner copy and section chrome only; Grok section bytes unchanged.
# P4: P4b_chart — chart-first explorer, phone frontier labels and dataset finding; Grok bytes unchanged.
# P4: P4c_ds + P4d integration
# P4: P4e zoom fix
# P4: P4f spot-check - raw-median presentation and harness-build provenance.
# Grok HTML changes only one catalog cell: <td>39.5</td> -> <td>39.4</td>.
OLD_NON_GROK_DIGESTS = {
    'results/report/page.html': 'd674652c18859510be9863b322944c1c79fadb4183c576ac5ef492145747cc05',
    'docs/REPORT.md': 'de2e362eb61a9240b1cd23e4bc03a83f38001ff5d54353e941315f4effd97507',
}


def grok_section(text, html=False):
    start, end = ('<section id="grok">', '</section>') if html else ('## Grok\n', '\n## Can luna')
    before, rest = text.split(start, 1)
    section, after = rest.split(end, 1)
    return section, before + after


class GrokText(HTMLParser):
    """Read actual cell text through inline markup and retain row associations."""
    def __init__(self):
        super().__init__()
        self.text, self.rows = [], []
        self.row, self.cell = None, None

    def handle_starttag(self, tag, attrs):
        if tag == "tr": self.row = []
        if tag == "td": self.cell = []

    def handle_endtag(self, tag):
        if tag == "td":
            self.row.append("".join(self.cell).strip())
            self.cell = None
        if tag == "tr" and self.row:
            self.rows.append(tuple(self.row))
            self.row = None
        if tag in {"p", "li", "h3", "td", "tr", "summary"}: self.text.append(" ")

    def handle_data(self, text):
        self.text.append(text)
        if self.cell is not None: self.cell.append(text)


def test_grok_fact_retention():
    """All old numbers/configs stay attached to their rows; every claim survives."""
    full, html = (Path(p).read_text() for p in (report.REPORT, report.PAGE))
    md_section, _ = grok_section(full)
    html_section, _ = grok_section(html, html=True)
    parsed = GrokText()
    parsed.feed(html_section)
    md_rows = {tuple(cell.strip() for cell in line.strip('|').split('|'))
               for line in md_section.splitlines() if line.startswith('|')}
    for old_row in OLD_GROK_ROWS:
        cells = tuple(cell.strip() for cell in old_row.strip('|').split('|'))
        assert cells in md_rows, f"Missing original Markdown fact row: {old_row}"
        assert cells in parsed.rows, f"Missing original HTML fact row: {old_row}"

    # Punctuation may split a sentence. Each underlying claim must still occur.
    normalize = lambda text: re.sub(r"[^\w$%×/–.-]+", " ", re.sub(r"(?m)^- ", "", text).lower()).strip(' .')
    texts = [normalize(md_section.replace('`', '')), normalize(''.join(parsed.text))]
    claims = list(OLD_GROK_CLAIMS)
    claims.append('The function misses were on p06_calc.')
    fallback = claims.pop(8)
    fallback_claim, comparison = fallback.split(': ', 1)
    grok_result, claude_result = comparison.split(', compared with ', 1)
    claims.extend([*fallback_claim.split(', though '), grok_result,
                   claude_result.replace(' at ', ' took ', 1)])
    for claim in claims:
        for text in texts:
            assert normalize(claim.replace('`', '')) in text, f"Missing original claim: {claim}"

    # The three operator paragraphs stay verbatim, immediately after the bullets.
    operator_words = '\n\n'.join(OLD_GROK_CLAIMS[:3])
    assert dataset.read()['facts']['grok_summary'].split('\n\n') == list(OLD_GROK_CLAIMS[:3])
    assert md_section.index(operator_words) < md_section.index('\n- ')  # the summary comes before the bullets
    assert report.to_html(operator_words) in html_section
    assert html_section.index(report.to_html(operator_words)) < html_section.index('<ul>')


def test_grok_readability_scope_is_local():
    for filename, digest in OLD_NON_GROK_DIGESTS.items():
        _, outside = grok_section(Path(report.ROOT, filename).read_text(), html=filename.endswith('.html'))
        assert hashlib.sha256(outside.encode()).hexdigest() == digest, filename


def test_grok_closest_tables_keep_one_lane_per_family_and_expand_all():
    ds = dataset.read()
    expected = {(c, family, other)
                for c in ('grok47-low', 'grok47-medium', 'grok47fast-low')
                for family, other in (('Claude', 'haiku-medium'), ('Codex', 'luna-high'))}
    expected.update({('grok47-high', 'Claude', 'haiku-high'), ('grok47-high', 'Codex', 'sol61-high')})
    rows = ds['tables']['grok_equivalent']['rows']
    assert {(c, family, lane) for c, family, lane, *_ in rows} == expected
    assert len(rows) == len({(row[0], row[1]) for row in rows}) == 8
    assert len(ds['tables']['grok_equivalent_all']['rows']) == 15
    repo = grok.repository_section(dataset.usd)
    compact, expanded = repo.split('<details><summary>All comparable lanes</summary>', 1)
    compact_rows = [line for line in compact.splitlines() if line.startswith('| grok')]
    assert compact.rstrip().endswith(grok.SELECTION_NOTE)
    assert len(compact_rows) == 4
    assert len({tuple(row.split('|')[1:3]) for row in compact_rows}) == 4
    assert '| grok47-high | Claude | haiku-high |' in compact
    assert '| grok47-high | Codex | sol61-high |' in compact
    assert '| grok47-low | Claude | haiku-high |' in compact
    assert '| grok47-low | Codex | sol61-medium |' in compact
    assert len([line for line in expanded.split('</details>', 1)[0].splitlines()
                if line.startswith('| grok')]) == 14
    page_section, _ = grok_section(Path(report.PAGE).read_text(), html=True)
    assert page_section.count('<summary>All comparable lanes</summary>') == 2
    parsed = GrokText()
    parsed.feed(page_section)
    assert ''.join(parsed.text).count(grok.SELECTION_NOTE) == 2
    assert '/ equivalent' not in page_section
    assert not re.search(r'<details\b[^>]*\bopen\b', page_section)


def test_grok_summary_cost_wins_follow_measurements(monkeypatch):
    ds = dataset.read()
    comparison = copy.deepcopy(ds['grok_first'])
    repository = grok.repository_comparison()
    lane = ds['report']['grok_first']
    monkeypatch.setattr(grok, 'repository_comparison', lambda: repository)
    _, verdict = grok.prose(comparison, lane)
    summary = grok.at_a_glance(comparison, lane, repository)
    assert 'grok47-high is cheaper per pass than astra-medium ⚡ (fast mode, 2× list price) on functions (0.55×).' in verdict
    assert 'grok47-low is cheaper per pass than plain astra-medium on repo tasks (0.42×) while 1.5× slower.' in verdict
    assert 'Codex dollars are list-price proxies.' in verdict
    assert 'grok47-low takes 0.84× as long as sol61-high on repo tasks.' in verdict
    assert 'Per the routing rule, Claude Haiku stays the first fallback when Codex is out. These runs show Grok is usable after that on small repo tasks.' in summary
    comparison['metrics']['grok47-high']['usd_per_pass'] *= 100
    repository['metrics']['grok47-low']['usd_per_pass'] *= 100
    _, changed = grok.prose(comparison, lane)
    assert '(0.55×)' not in changed and '(0.42×)' not in changed
    assert 'No cost edge in these comparisons.' in changed

    # New wins on lanes that were never hard-coded must appear too.
    comparison['metrics']['haiku-medium']['usd_per_pass'] = 100
    comparison['metrics']['haiku-medium']['median_s'] = 1000
    repository['metrics']['sonnet-medium']['usd_per_pass'] = 100
    repository['metrics']['sonnet-medium']['median_s'] = 1000
    _, changed = grok.prose(comparison, lane)
    assert 'grok47-medium is cheaper per pass than haiku-medium on functions' in changed
    assert 'grok47-medium takes 0.03× as long as haiku-medium on functions' in changed
    assert 'grok47-high is cheaper per pass than sonnet-medium on repo tasks' in changed
    assert 'grok47-high takes 0.44× as long as sonnet-medium on repo tasks' in changed
    costs, times = grok.edge_prose(comparison, repository)
    assert costs and times
    assert all(edge in changed for edge in costs + times)


def test_grok_ranges_cover_all_perfect_lanes_and_follow_measurements():
    ds = dataset.read()
    comparison = copy.deepcopy(ds['grok_first'])
    repository = grok.repository_comparison()
    lane = ds['report']['grok_first']
    summary = grok.at_a_glance(comparison, lane, repository)
    assert 'grok47-low, grok47-medium and grok47fast-low (cleared through L2)' in summary
    assert 'grok47-low, grok47-medium and grok47fast-low cleared L1–L2. Each first missed at L3.' in summary
    assert 'grok47-high cleared L1–L3. It was not run further.' in summary
    assert 'Across all Codex 100% lanes, Grok takes 2.4–6.0× as long and costs 0.6–5.9× as much per pass' in summary
    assert 'Across all Claude 100% lanes, Grok takes 3.5–5.0× as long and costs 7.2–109.3× as much per pass' in summary
    assert 'Across all Codex 100% lanes, Grok takes 0.8–1.5× as long and costs 0.4–2.4× as much per pass' in summary
    # An unselected perfect lane still determines the range; an imperfect lane does not.
    repository['metrics']['astra-medium']['median_s'] *= 0.1
    repository['metrics']['luna-low']['median_s'] = 0.001
    changed = grok.at_a_glance(comparison, lane, repository)
    assert 'Across all Codex 100% lanes, Grok takes 0.8–15.1× as long' in changed


def test_full_spectrum_headline_counts_come_from_the_data():
    """grok47-high 57/60 and terra61-low 60/60, read from the graded rows and from the built page."""
    rows = summarize.function_rows()
    tally = lambda c: (sum(r["passed"] for r in rows if r["config"] == c), sum(1 for r in rows if r["config"] == c))
    assert tally("grok47-high") == (57, 60) and tally("terra61-low") == (60, 60)
    ds = dataset.read()
    assert (ds["report"]["grok"]["grok47-high"]["passes"], ds["report"]["grok"]["grok47-high"]["n"]) == (57, 60)
    terra = dataset.get(ds, "terra61-low", "main ladder")
    assert (terra["passes"], terra["n"]) == (60, 60)
    page_text = Path(report.PAGE).read_text()
    assert all(x in page_text for x in ("57/60", "53/60", "51/60", "60/60", "58/60"))
