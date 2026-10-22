"""Appendix: can prompt, harness or routing changes rescue luna-low on the problems it fails most? (exploratory, post hoc)

Rows for arms B-E are in results/appendix/luna_rescue.jsonl; the baselines are the main run's rows for the same
problems and repeats. Prints a markdown table. Run: python3 -m analysis.luna_rescue"""
import json, os
from analysis.summarize import cost, ROOT

PIDS = ["p03_ledger", "p04_taller_within", "p08_recur", "p09_k_machine_schedule", "p10_avoid_count", "p11_best_average", "p12_sheet"]
ARMS = [("luna-low", "luna-low baseline"),
        ("luna-low-noshell-B1", "B1: no shell, plus a \"list edge cases and trace the examples first\" nudge"),
        ("luna-low-noshell-B2", "B2: B1 plus a detailed reasoning summary"),
        ("luna-low-selftest", "C: shell on, told to test its code before answering"),
        ("luna-medium-bare", "D: luna-medium, stripped harness"),
        ("luna-high-bare", "D: luna-high, stripped harness"),
        ("luna-low+haiku-low-repair", "E: luna-low answer, then haiku-low reviews and repairs it"),
        ("haiku-low-plan+luna-low", "F: haiku-low writes a plan, luna-low builds from it"),
        ("haiku-low-plan+luna-high-bare", "F: haiku-low writes a plan, luna-high (stripped harness) builds from it"),
        ("haiku-low", "haiku-low"),
        ("sonnet-medium", "sonnet-medium")]


def arms():
    """Per arm: label, passes, n, $ per pass, median seconds, total $, and its rows."""
    main_rows = [json.loads(l) for l in open(os.path.join(ROOT, "results", "2026-10-22b-function.jsonl"))]
    main_rows = [dict(r, cost_usd=cost(r)) for r in main_rows if r["phase"] == "main" and r["problem"] in PIDS]
    arm_rows = [json.loads(l) for l in open(os.path.join(ROOT, "results", "appendix", "luna_rescue.jsonl"))]
    out = {}
    for c, label in ARMS:
        rr = [r for r in main_rows + arm_rows if r["config"] == c and r["problem"] in PIDS and 1 <= r["repeat"] <= 5]
        assert len(rr) == 35, (c, len(rr))
        k = sum(r["passed"] for r in rr); w = sorted(r["wall_s"] for r in rr); usd = sum(r["cost_usd"] for r in rr)
        out[c] = {"label": label, "passes": k, "n": len(rr), "usd_per_pass": usd / k, "median_s": w[17], "usd_total": usd, "rows": rr}
    return out


def table(a):
    L = ["| config | passed | $ per pass | median s |", "|---|---|---|---|"]
    for v in a.values():
        L.append(f"| {v['label']} | {v['passes']}/{v['n']} | {v['usd_per_pass']:.5f} | {v['median_s']:.1f} |")
    return "\n".join(L)


def main():
    print(table(arms()))


if __name__ == "__main__":
    main()
