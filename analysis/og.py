"""Share card: results/report/og.png (1200x630), the hero chart beside the title and the takeaway, drawn by headless Chrome.
Skipped with a message, keeping the committed PNG, when Chrome is missing or fails. Run by `make report`."""
import json, os, shutil, subprocess, sys, tempfile
from html import escape
from analysis import dataset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "report", "og.png")
HERO = os.path.join(ROOT, "results", "report", "charts", "hero.svg")
TITLE = "DispatchBench: which model should a coding task go to?"
MAX_BYTES = 300_000


def takeaway(facts):
    """The one-line takeaway: the three Winner picks, as the page words them."""
    return " ".join(facts[k] for k in ("winner_default", "winner_budget", "winner_speed"))


def card_html(facts):
    svg = open(HERO).read().replace("var(--panel,", "var(--card,").replace("var(--panel)", "#ffffff")
    return f"""<!doctype html><meta charset="utf-8"><style>
:root{{--card:#ffffff;--fg:#1d2321;--muted:#5d6763;--line:#dde2de;--frontier:#7b3fe4}}
*{{box-sizing:border-box}}html,body{{margin:0;width:1200px;height:630px;background:#f6f7f4;color:#1d2321;
font-family:'Hanken Grotesk','Atkinson Hyperlegible',-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;overflow:hidden}}
.card{{display:flex;height:630px;padding:40px 36px 40px 48px;gap:28px;align-items:center}}
.txt{{width:370px;flex:none}}.kick{{font:600 15px/1 monospace;letter-spacing:.08em;text-transform:uppercase;color:#5d6763;margin:0 0 18px}}
h1{{font-size:40px;line-height:1.12;margin:0 0 22px;font-weight:700}}p{{font-size:21px;line-height:1.4;margin:0;color:#1d2321}}
.chart{{flex:none;width:720px;background:#fff;border:1px solid #dde2de;border-radius:10px;padding:8px}}.chart svg{{width:100%;height:auto;display:block}}
</style><div class="card"><div class="txt"><p class="kick">Chimeric Labs</p><h1>{escape(TITLE)}</h1><p>{escape(takeaway(facts))}</p></div>
<div class="chart">{svg}</div></div>"""


def build():
    chrome = next((p for p in (shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser")) if p), None)
    if not chrome:
        print("og.png: Chrome not found; kept the existing file"); return 0
    facts = dataset.read()["facts"]
    with tempfile.TemporaryDirectory() as d:
        src, png = os.path.join(d, "card.html"), os.path.join(d, "og.png")
        open(src, "w").write(card_html(facts))
        r = subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--window-size=1200,630",
                            f"--screenshot={png}", "file://" + src], capture_output=True, text=True, timeout=120)
        if r.returncode or not os.path.exists(png):
            print("og.png: Chrome failed; kept the existing file:", r.stderr.strip()[-200:]); return 0
        data = open(png, "rb").read()
    if len(data) > MAX_BYTES:
        print(f"og.png: {len(data):,} bytes is over {MAX_BYTES:,}; kept the existing file"); return 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True); open(OUT, "wb").write(data)
    print(f"og.png: {len(data):,} bytes -> {os.path.relpath(OUT, ROOT)}"); return 0


if __name__ == "__main__":
    sys.exit(build())
