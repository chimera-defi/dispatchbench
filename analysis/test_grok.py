"""Exercise the pending Grok lane without changing any graded results files."""
import copy
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
            assert section in {"grok", "fail"}, (config, section)
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


@pytest.mark.parametrize("section", ["grok", "fail"])
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


def test_grok_scope_generated_page():
    html = Path(report.PAGE).read_text()
    scope = GrokScope()
    scope.feed(html)
    scope.close()
    assert not scope.elements
    assert set(scope.counts) == set(configs.GROK_CONFIGS)
    assert all(set(counts) == {"grok", "fail"} for counts in scope.counts.values())
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
    assert "on p06_calc" in ds["facts"]["grok_summary"]
    note = ds["facts"]["grok_reach_note"]
    assert "(18, 21, 24)" in note and "from 5 to 2 repeats partway through L2" in note
    assert "30 = 6 problems × 5 repeats" in note and "read the rung reached, not the total" in note
    changed = copy.deepcopy(ds["grok_comparison"])
    for c in configs.GROK_CONFIGS:
        changed["metrics"][c]["n"] = 36
        for rung in changed["repeat_counts"][c].values():
            for p in rung: rung[p] *= 2
    note = grok.reach_note(changed, ds["report"]["grok"])
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
                        ts="2026-10-26T10:00:00Z", key=c + r["key"], cost_usd=0.123456,
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
    assert charts.build(ds) == charts.build(baseline)
    assert "Grok (first half)" in tables
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
    assert "L4–L6 were not run" in html and "CLI-reported cost; list price not used" in html
    assert all(c in html for c in configs.GROK_CONFIGS)
    scope = GrokScope()
    scope.feed(html)
    assert set(scope.counts) == set(configs.GROK_CONFIGS)
    assert all(set(counts) == {"grok", "fail"} for counts in scope.counts.values())
    assert "Grok" not in readme  # README currently shows only the Winner table.
    assert "Grok" not in full.split("## Grok\n")[0]
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
    assert "a usable fallback" in rendered and "grok47-high passed 8/8" in rendered
    assert "though Claude is faster and cheaper" in rendered
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
