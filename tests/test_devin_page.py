"""Devin on the page: its colour is legible on every theme, its row reads 6/12, and it never reaches a $ view."""
import re
from pathlib import Path

from analysis import configs, dataset, page

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "docs/page/style.css").read_text()
BACKGROUNDS = {"light": ("#ffffff", "#f6f7f4"), "dark": ("#1b2220", "#141917")}


def luminance(hex_):
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda v: v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + .05) / (lo + .05)


def test_devin_colour_has_3_to_1_contrast_on_light_and_dark_backgrounds():
    light = re.search(r"--devin:(#[0-9a-f]{6})", CSS)[1]
    darks = re.findall(r"--devin:(#[0-9a-f]{6})", CSS)[1:]
    assert darks, "dark theme must set its own --devin"
    for bg in BACKGROUNDS["light"]: assert contrast(light, bg) >= 3, (light, bg)
    for dark in darks:
        for bg in BACKGROUNDS["dark"]: assert contrast(dark, bg) >= 3, (dark, bg)


def test_devin_colour_is_distinct_from_every_other_family_colour():
    mine = re.search(r"--devin:(#[0-9a-f]{6})", CSS)[1]
    others = {m[0]: m[1] for m in re.findall(r"--(\w+):(#[0-9a-f]{6})", CSS.split("@media")[0]) if m[0] not in ("devin", "bg", "panel", "fg", "muted", "line")}
    for name, val in others.items():
        assert mine != val, name


def test_devin_row_shows_6_of_12_and_stays_off_dollar_views():
    html = (ROOT / "results/report/page.html").read_text()
    row = re.search(r"<tr[^>]*>(?:(?!</tr>).)*devin16slow-default(?:(?!</tr>).)*</tr>", html, re.S)[0]
    assert "6/12" in re.sub(r"<[^>]+>", "", row)
    assert "1 repeat, free tier, no token data" in html
    s = dataset.view(dataset.read())
    assert "devin16slow-default" not in s["pareto"]
    for fn in (page.pass_cost, page.speed_cost):
        for free in (False, True):
            _, fr = fn(s, free=free)
            assert "devin16slow-default" not in fr
    pts = page.ladder_points(s, True, "pass", "main")
    assert all(p["c"] not in configs.DEVIN_CONFIGS for p in pts)
