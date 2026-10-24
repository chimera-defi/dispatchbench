"""The dataset must agree with summary.json and the rescue table, cover every row once, and have unique (config, set) keys."""
import json, os
import pytest
from analysis import configs, dataset, luna_rescue
from analysis.summarize import RES


@pytest.fixture(scope="module")
def ds():
    return dataset.build()


def test_keys_unique_and_registered(ds):
    ks = [(r["config"], r["set"]) for r in ds["rows"]]
    assert len(ks) == len(set(ks))
    assert configs.check_registry(dataset.keys(ds)) == []


def test_matches_summary(ds):
    s = json.load(open(os.path.join(RES, "summary.json")))
    for c, v in {**s["configs"], **(s.get("exploratory") or {})}.items():
        r = dataset.get(ds, c, "main ladder")
        assert r["n"] == v["n"] and abs(r["spend"] - v["usd_total"]) < 1e-3, c


def test_all_runs_pools_only_function_sets(ds):
    all_runs = [r for r in ds["rows"] if r["set"] == "all runs"]
    assert all(r["source"] == "main" for r in all_runs)
    assert len(all_runs) == len({r["config"] for r in ds["rows"] if r["source"] == "main"})
    assert (dataset.get(ds, "haiku-high", "all runs")["passes"],
            dataset.get(ds, "haiku-high", "all runs")["n"]) == (75, 75)
    # Sonnet's calibration 10/10 is included alongside main 60/60 and L7 15/15.
    assert (dataset.get(ds, "sonnet-medium", "all runs")["passes"],
            dataset.get(ds, "sonnet-medium", "all runs")["n"]) == (85, 85)
    for source, set_ in (("agentic", "repo tasks"), ("pilot", "pilot")):
        assert any(r["source"] == source and r["set"] == set_ for r in ds["rows"])


def test_catalog_keeps_every_source_under_its_own_counts(ds):
    catalog = dataset.catalog_rows(ds)
    assert len(catalog) == len(configs.REGISTRY)
    by = {(r["source"], r["config"]): r for r in catalog}
    assert set(by) == set(configs.REGISTRY)
    for source, name, set_, passes, attempts in (
        ("main", "haiku-high", "all runs", 75, 75),
        ("agentic", "haiku-high", "repo tasks", 12, 12),
        ("main", "sonnet-medium", "all runs", 85, 85),
        ("agentic", "sonnet-medium", "repo tasks", 12, 12),
        ("pilot", "sonnet-medium", "pilot", 19, 19),
    ):
        row = by[source, name]
        assert (row["set"], row["passes"], row["n"]) == (set_, passes, attempts)


@pytest.mark.parametrize("value,want", [
    (None, "–"), (0, "$0"), (1, "$1.00"), (12.345, "$12.35"),
    (.002822, "$0.0028"), (.000890, "$0.00089"), (.01234, "$0.012"),
    (.1, "$0.1"), (.001, "$0.001"), (.003, "$0.003"), (.01, "$0.01"),
    (.03, "$0.03"), (.3, "$0.3"), (.0000001234, "$0.00000012"),
])
def test_usd_readable_precision(value, want):
    assert dataset.usd(value) == want


def test_usd_explicit_comparison_precision():
    assert dataset.usd(.000890, sig=3) == "$0.00089"
    assert dataset.usd(.000899, sig=3) == "$0.000899"


def test_matches_rescue_arms(ds):
    for c, a in luna_rescue.arms().items():
        r = dataset.get(ds, c, "rescue arms", "rescue") if (("rescue", c) in configs.REGISTRY) else None
        if r: assert (r["passes"], r["n"]) == (a["passes"], a["n"]), c  # baselines (main-run configs on the rescue problems) have no rescue-arms row yet


def test_rescue_view_uses_measured_arms_and_validated_derived_slices(ds):
    metrics = ("passes", "n", "usd_per_pass", "claude_usd_per_pass", "median_s")
    for name, arm in ds["rescue"].items():
        if ("rescue", name) in configs.REGISTRY:
            row = dataset.get(ds, name, "rescue arms", "rescue")
            assert not arm["derived"]
        elif name.endswith("-fast+haiku-on-fail"):
            row = dataset.get(ds, name.split("+")[0], "rescue set")
            assert arm["derived"]
            assert arm["derived_from"] == arm["metrics_from"]
        else:
            continue
        assert {k: arm[k] for k in metrics} == {k: row[k] for k in metrics}, name


def test_cached_dataset_current(ds):
    assert open(dataset.PATH).read() == dataset.text(ds)


def test_rescue_set_is_derived_and_matches_baselines(ds):
    arms = luna_rescue.arms()
    derived = [r for r in ds["rows"] if r["derived"]]
    assert derived and {r["set"] for r in derived} == {"rescue set"}
    for r in (r for r in derived if r["config"] in arms): assert (r["passes"], r["n"]) == (arms[r["config"]]["passes"], arms[r["config"]]["n"]), r["config"]
    # derived rows never feed the roll-up: all-runs n equals the sum of the non-derived sets
    for a in (r for r in ds["rows"] if r["set"] == "all runs"):
        parts = [r["n"] for r in ds["rows"] if r["id"] == a["id"] and r["set"] != "all runs" and not r["derived"]]
        assert sum(parts) == a["n"], a["id"]
    # every result row is in exactly one non-derived set: set counts are unique per (source, config)
    ks = [(r["source"], r["config"], r["set"]) for r in ds["rows"] if not r["derived"]]
    assert len(ks) == len(set(ks))
