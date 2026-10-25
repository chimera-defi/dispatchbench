"""Appendix: can prompt, harness or routing changes rescue luna-low on the problems it fails most? (exploratory, post hoc)

Rows for arms B-G are in results/appendix/luna_rescue.jsonl; the baselines are the main run's rows (and the exploratory
configs' rows) for the same problems and repeats. Prints a markdown table. Run: python3 -m analysis.luna_rescue"""
import json, os
from analysis.summarize import cost, ROOT, usd, money, function_rows, rescue_rows

PIDS = ["p03_ledger", "p04_taller_within", "p08_recur", "p09_k_machine_schedule", "p10_avoid_count", "p11_best_average", "p12_sheet"]
ARMS = [("luna-low", "luna-low baseline"),
        ("luna-low-noshell-B1", "B1: no shell, plus a \"list edge cases and trace the examples first\" nudge"),
        ("luna-low-noshell-B2", "B2: B1 plus a detailed reasoning summary"),
        ("luna-low-selftest", "C: shell on, told to test its code before answering"),
        ("luna-medium-bare", "D: luna-medium, stripped harness"),
        ("luna-high-bare", "D: luna-high, stripped harness"),
        ("luna-low+haiku-low-repair", "E (original run, prompt not kept): luna-low answer, then haiku-low reviews and repairs it"),
        ("haiku-low-plan+luna-low", "F: haiku-low writes a plan, luna-low builds from it"),
        ("haiku-low-plan+luna-high-bare", "F: haiku-low writes a plan, luna-high (stripped harness) builds from it"),
        ("luna-high-bare+haiku-on-fail", "G: luna-high (stripped) builds; haiku-low repairs only if the statement's examples fail"),
        ("luna-high-bare+retry-on-fail", "G: luna-high (stripped) builds; luna-high retries only if the statement's examples fail"),
        ("luna-low+haiku-on-fail", "G: luna-low builds; haiku-low repairs only if the statement's examples fail"),
        ("luna-high-bare+haiku-review-all", "G: luna-high (stripped) builds; haiku-low reviews every answer, as in E"),
        ("luna-low+haiku-review-all", "G: luna-low builds; haiku-low reviews every answer (arm E rerun from committed code)"),
        ("sol61-high+haiku-on-fail", "G: sol61-high builds; haiku-low repairs only if the statement's examples fail"),
        ("astra-medium+haiku-on-fail", "G: astra-medium builds; haiku-low repairs only if the statement's examples fail"),
        ("haiku-low", "haiku-low"),
        ("haiku-medium", "haiku-medium"),
        ("haiku-high", "haiku-high"),
        ("sonnet-medium", "sonnet-medium"),
        ("sol61-medium", "sol61-medium"),
        ("sol61-high", "sol61-high"),
        ("sol61-high-fast", "sol61-high, fast mode"),
        ("astra-medium", "astra-medium"),
        ("astra-medium-fast", "astra-medium, fast mode"),
        ("sol56-high", "sol56-high"),
        ("luna56-high", "luna56-high"),
        ("luna56-low", "luna56-low")]


def claude_usd(r):
    """The Claude-billed part of a row; Codex calls bill Codex, not Claude."""
    if "haiku_cost_usd" in r: return r["haiku_cost_usd"]
    if "repair_cost_usd" in r: return r["repair_cost_usd"] if "haiku" in r["config"] else 0.0
    return r["cost_usd"] if r.get("cli") == "claude" else 0.0


def arms():
    """Per arm: label, passes, n, $ per pass, median seconds, total $, and its rows."""
    main_rows = function_rows()
    main_rows = [dict(r, cost_usd=cost(r)) for r in main_rows if r["phase"] in ("main", "exploratory", "fastmode") and r["problem"] in PIDS]
    arm_rows = rescue_rows()
    out = {}
    for c, label in ARMS:
        rr = [r for r in main_rows + arm_rows if r["config"] == c and r["problem"] in PIDS and 1 <= r["repeat"] <= 5]
        assert len(rr) == 35, (c, len(rr))
        k = sum(r["passed"] for r in rr); w = sorted(r["wall_s"] for r in rr); total = usd((r.get("cost_usd") for r in rr), digits=None)
        out[c] = {"label": label, "passes": k, "n": len(rr), "usd_per_pass": usd([total], k, digits=None), "median_s": w[17], "usd_total": total, "rows": rr,
                  "claude_usd_per_pass": usd((claude_usd(r) for r in rr), k, digits=None)}
    return out


def table(a):
    L = ["| config | passed | $ per pass | Claude $ per pass | median s |", "|---|---|---|---|---|"]
    for v in a.values():
        L.append(f"| {v['label']} | {v['passes']}/{v['n']} | {money(v['usd_per_pass'])} | {money(v['claude_usd_per_pass'])} | {v['median_s']:.1f} |")
    return "\n".join(L)


def main():
    print(table(arms()))


if __name__ == "__main__":
    main()
