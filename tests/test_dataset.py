"""The dataset must agree with summary.json and the rescue table, cover every row once, and have unique (source, config, set) keys."""
import json, os
from analysis import configs, dataset, luna_rescue
from analysis.summarize import RES


def test_keys_unique_and_registered():
    ds = dataset.build(); ks = [(r["source"], r["config"], r["set"]) for r in ds["rows"]]
    assert len(ks) == len(set(ks))
    assert configs.check_registry(dataset.keys(ds)) == []


def test_matches_summary():
    ds = dataset.build(); s = json.load(open(os.path.join(RES, "summary.json")))
    for c, v in {**s["configs"], **(s.get("exploratory") or {})}.items():
        r = dataset.get(ds, c, "main ladder")
        assert r["n"] == v["n"] and abs(r["spend"] - v["usd_total"]) < 1e-3, c


def test_matches_rescue_arms():
    ds = dataset.build()
    for c, a in luna_rescue.arms().items():
        r = dataset.get(ds, c, "rescue arms", "rescue") if (("rescue", c) in configs.REGISTRY) else None
        if r: assert (r["passes"], r["n"]) == (a["passes"], a["n"]), c  # baselines (main-run configs on the rescue problems) have no rescue-arms row yet


def test_cached_dataset_current():
    assert open(dataset.PATH).read() == dataset.text(dataset.build())


def test_rescue_set_is_derived_and_matches_baselines():
    ds = dataset.build(); arms = luna_rescue.arms()
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
