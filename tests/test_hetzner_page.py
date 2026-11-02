"""Measured Hetzner calibration stays visible, with no invented dollar comparison."""
import importlib.util
import json
from pathlib import Path
import re
import statistics

import pytest

from analysis import charts, configs, dataset, page

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def ds():
    return dataset.read()


@pytest.mark.parametrize("config,passes", [("hetzner-qwen36", 10), ("hetzner-qwen38", 9)])
def test_measured_usage_and_thin_coverage_survive(config, passes, ds):
    raw = [json.loads(line) for line in (ROOT / "results/2026-11-01-hetzner-function.jsonl").read_text().splitlines()]
    rr = [r for r in raw if r["config"] == config]
    row = dataset.get(ds, config, "partial ladder")
    assert row["category"] == "exploratory" and row["family"] == "Hetzner"
    assert row["n"] == len(rr) == 12 and row["passes"] == passes
    assert all(r["phase"] == "calibration" and r["repeat"] == 1 for r in rr)
    assert row["median_s_raw"] == statistics.median(r["wall_s"] for r in rr)
    assert row["tokens_in_mean"] == round(statistics.mean(r["in_tok"] for r in rr)) > 0
    assert row["tokens_out_mean"] == round(statistics.mean(r["out_tok"] for r in rr)) > 0
    assert row["cost_kind"] == "free-tier" and row["usd_per_pass"] is None
    token_row = next(r for r in ds["tables"]["tokens"]["rows"] if r[0] == config + " †")
    assert token_row[1] == dataset.n(row["tokens_in_mean"])
    assert token_row[3] == dataset.n(row["tokens_out_mean"])
    assert token_row[-1] == "free tier"
    assert dataset.n(sum(r["in_tok"] for r in rr)) in ds["facts"]["hetzner_lead"]
    table_row = next(r for r in ds["tables"]["hetzner_summary"]["rows"] if r[0] == config)
    assert table_row[2:] == [f"{passes}/12", f"{row['median_s_raw']:.1f}", dataset.n(sum(r["out_tok"] for r in rr))]


def test_hetzner_visible_with_one_repeat_and_free_tier_label(ds):
    html = (ROOT / "results/report/page.html").read_text()
    s = dataset.view(ds)
    rung_rows, _ = charts.rung_rows(s, ds)
    for c in configs.HETZNER_CONFIGS:
        assert c in page.grid(s) and c in charts.heatmap(s) and c in rung_rows
        result = re.search(r"<tr[^>]*>(?:(?!</tr>).)*" + c + r"(?:(?!</tr>).)*</tr>", html, re.S)[0]
        assert "free tier" in result and "$0" not in result and "†" in result
        assert set(rung_rows[c]) == {f"L{i}" for i in range(1, 7)}
        assert all(n == 2 for _, n in rung_rows[c].values())
    assert html.count('id="hetzner"') == 1
    assert '<a class="hlink" href="#hetzner"' in html
    assert html.index('id="hetzner"') > html.index('<section id="grok">')
    assert "first-attempt rows are not in the repo cache" in html
    assert "21 of 23 calls" in html and "HTTP 504" in html
    assert "341.5 s" in html and "820.6 s" in html and "1800 s wall cap" in html


def test_no_hetzner_dollar_plot_winner_or_frontier(ds):
    s = dataset.view(ds)
    assert not set(configs.HETZNER_CONFIGS) & set(s["pareto"])
    assert not set(configs.HETZNER_CONFIGS) & set(dataset.WINNER_PICKS)
    for draw in (page.pass_cost, page.speed_cost):
        for free in (False, True):
            rendered, frontier = draw(s, free=free)
            assert all(c not in rendered and c not in frontier for c in configs.HETZNER_CONFIGS)
    for name, body in charts.build(ds).items():
        if name in ("pass_by_rung.svg", "heatmap.svg"):
            assert all(c in body for c in configs.HETZNER_CONFIGS)
        else:
            assert all(c not in body for c in configs.HETZNER_CONFIGS), name
    for st in ds["explorer"]["sets"]:
        for views in st["views"].values():
            for name in dataset.EXPLORER_VIEWS:
                view = views[name]
                for key, membership in view["membership"].items():
                    if any(c in key for c in configs.HETZNER_CONFIGS):
                        assert not membership["eligible"] and not membership["on_frontier"]


def test_hetzner_colour_contrast_and_distinct_palette():
    spec = importlib.util.spec_from_file_location("contrast", ROOT / "tools/check_contrast.py")
    contrast = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(contrast)
    css = (ROOT / "docs/page/tokens.css").read_text()
    checked = list(contrast.check_hetzner(css))
    assert len(checked) == 8 and all(ratio >= minimum for _, ratio, minimum in checked)
    for mode in ("light", "dark"):
        for automatic in (False, True):
            values = contrast.theme_values(css, mode, automatic=automatic)
            bg = contrast.rgb("--bg", values, None)
            mine = contrast.rgb("--hetzner", values, bg)
            for family in ("--claude", "--sonnet", "--codex", "--codex56", "--grok", "--devin"):
                assert mine != contrast.rgb(family, values, bg)


def test_existing_grok_summary_is_byte_identical_before_restored_findings():
    import hashlib
    html = (ROOT / "results/report/page.html").read_text()
    body = re.search(r'<section id="grok">.*?</section>', html, re.S)[0]
    original, restored = body.split('<details class="small"><summary>Grok comparisons and methods</summary>', 1)
    assert hashlib.sha256((original + '</section>').encode()).hexdigest() == "9fcb9868f2abc0cbde44f46607fc6447466c17aa7eabab271d38c049f6558fda"
    assert 'id="closest-lanes-by-pass-rate"' in restored and 'id="devin"' in restored


def test_any_pair_explorer_is_open_at_load():
    html = (ROOT / "results/report/page.html").read_text()
    assert '<details open><summary>Explore tokens, reasoning, and latency</summary>' in html
    assert 'id="xfig"' in html
