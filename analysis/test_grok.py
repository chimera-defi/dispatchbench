"""Exercise the pending Grok lane without changing any graded results files."""
import copy

import pytest

from analysis import charts, configs, dataset, page, report, summarize


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
                        effort=c.rsplit("-", 1)[1], phase="exploratory", cli_version="test-grok",
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
    assert "Grok (first half)" in full and "6 of 12 problems" in full
    assert "Grok (first half)" in html and "6 of 12 problems" in html
    assert "L4–L6 were not run" in html and "CLI-reported cost; list price not used" in html
    assert all(c in html for c in configs.GROK_CONFIGS)
    assert "Grok (first half)" not in readme  # README currently shows only the Winner table.
