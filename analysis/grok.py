"""Same-problem Grok comparisons, kept separate from the full-ladder results.

Comparison measurements use main + exploratory rows only. Ladder profiles use
the canonical main-ladder rows, including reused calls, and stop at the first miss.
"""
import math
import statistics
from collections import defaultdict

from analysis import configs, summarize


def profile(by_rung):
    """Return the last consecutively perfect rung and the first rung with a miss."""
    cleared = 0
    for rung, (passed, n) in sorted(by_rung.items(), key=lambda item: int(item[0][1:])):
        level = int(rung[1:])
        if passed < n:
            return cleared, level
        if level != cleared + 1:
            break
        cleared = level
    return cleared, None


def measurements(rows):
    passed = sum(r["passed"] for r in rows)
    return {"passes": passed, "n": len(rows), "pass_rate": passed / len(rows),
            "median_s": statistics.median(r["wall_s"] for r in rows),
            "usd_per_pass": summarize.usd(map(summarize.cost, rows), passed, digits=None)}


def build(ds, summary):
    """Persist source scope, measurements, profiles and every compatible equivalent."""
    lane = summary.get("grok", {})
    if not lane:
        return {}
    problems = sorted({p for v in lane.values() for p in v["by_problem"]})
    grouped = defaultdict(list)
    for r in summarize.function_rows():
        if r["phase"] in ("main", "exploratory") and r["problem"] in problems:
            grouped[r["config"]].append(r)
    metrics = {c: measurements(rr) for c, rr in grouped.items()}
    ladder = {r["config"]: r for r in ds["rows"] if r["source"] == "main" and r["set"] == "main ladder"}
    profiles = {c: profile(r["by_rung"]) for c, r in ladder.items()}
    matches = {}
    for c in lane:
        p = profile({g: (v["passed"], v["n"]) for g, v in lane[c]["by_rung"].items()})
        profiles[c] = p
        # An unmissed partial ladder is censored: later success or failure is unknown.
        matches[c] = [other for other in sorted(ladder) if other in metrics and
                      (profiles[other] == p if p[1] is not None else profiles[other][0] >= p[0])]
    return {"problems": problems, "phases": ["main", "exploratory"], "metrics": metrics,
            "profiles": profiles, "matches": matches,
            "repeat_counts": {c: {g: {p: len({r["repeat"] for r in rr if r["problem"] == p})
                                      for p in sorted({r["problem"] for r in rr if r["rung"] == g})}
                                  for g in sorted({r["rung"] for r in rr})}
                              for c, rr in grouped.items() if c in lane or c == "haiku-low"},
            "by_problem": {c: {p: [sum(r["passed"] for r in rr if r["problem"] == p),
                                    sum(r["problem"] == p for r in rr)] for p in problems}
                           for c, rr in grouped.items() if c in lane}}


def prose(comparison, lane):
    """The operator's wording, with numeric claims derived or verified from rows."""
    m = comparison["metrics"]
    existing = {c: v for c, v in m.items() if c not in lane}
    perfect = [v["median_s"] for v in existing.values() if v["passes"] == v["n"]]
    high = m["grok47-high"]
    prices = [m[c]["usd_per_pass"] for c in lane if m[c]["usd_per_pass"] is not None]
    cheap = [v["usd_per_pass"] for c, v in existing.items() if c.startswith(("haiku", "luna"))]
    ceiling = (math.floor(max(cheap) * 1000) + 1) / 1000
    words = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four"}
    stopped = [c for c in lane if comparison["profiles"][c][1] is not None]
    summary = ["Grok is accurate but slow and mid-priced. "
               f"grok47-high passed {high['passes']} of {high['n']} but took {high['median_s']:.0f} s per call at the median. "
               f"Every existing lane at {100 * high['pass_rate']:.0f}% finished in {min(perfect):.1f} to {max(perfect):.1f} s."]
    if stopped:
        misses = {lane[c]["by_rung"][f'L{comparison["profiles"][c][1]}']["n"] -
                  lane[c]["by_rung"][f'L{comparison["profiles"][c][1]}']["passed"] for c in stopped}
        rung_cells = {(comparison["profiles"][c][1], lane[c]["by_rung"][f'L{comparison["profiles"][c][1]}']["passed"],
                       lane[c]["by_rung"][f'L{comparison["profiles"][c][1]}']["n"]) for c in stopped}
        if len(misses) == len(rung_cells) == 1:
            rung, k, n = next(iter(rung_cells))
            names = ", ".join(stopped[:-1]) + " and " + stopped[-1] if len(stopped) > 1 else stopped[0]
            count = words.get(len(stopped), str(len(stopped)))
            missed = next(iter(misses))
            problems = sorted({p for c in stopped for p, (passed, attempts) in comparison["by_problem"][c].items()
                               if passed < attempts})
            summary.append(f"{names} each missed {words.get(missed, str(missed))} call at L{rung} ({k}/{n}) "
                           f"on {', '.join(problems)}, "
                           f"so the pre-registered stop rule fired for all {count}.")
    dear = {configs.family(c) for c, v in existing.items() if v["usd_per_pass"] >= min(prices)} if prices else set()
    summary.append(f"Cost per pass is ${min(prices):.3f} to ${max(prices):.3f}. "
                   f"Claude haiku and the Codex luna lanes are under ${ceiling:.3f}. "
                   + ("Only the Codex astra lanes cost as much." if dear == {"Codex"} and
                      all(c.startswith("astra") for c, v in existing.items() if v["usd_per_pass"] >= min(prices))
                      else "The comparison table shows the existing lanes' prices."))
    pairs = [(c, e) for c, equivalents in comparison["matches"].items() for e in equivalents]
    wins = lambda key, lower: [(c, e) for c, e in pairs if m[c][key] is not None and m[e][key] is not None
                              and (m[c][key] < m[e][key] if lower else m[c][key] > m[e][key])]
    time, price, rate = wins("median_s", True), wins("usd_per_pass", True), wins("pass_rate", False)
    if not time and not price and not rate:
        verdict = "No Grok config beats a closest equivalent on time or price. Pass rate is equal at best."
    else:
        gains = []
        for matches, label in ((time, "is faster than"), (price, "costs less per pass than"), (rate, "has a higher pass rate than")):
            gains += [f"{c} {label} {e}" for c, e in matches]
        verdict = "; ".join(gains) + "."
        absent = [label for matches, label in ((time, "time"), (price, "price"), (rate, "pass rate")) if not matches]
        if absent:
            verdict += " No Grok config beats a listed equivalent on " + " or ".join(absent) + "."
    return summary, verdict


def reach_note(comparison, lane):
    """Describe the documented repeat reduction with counts from the retained rows."""
    repeats = comparison["repeat_counts"]
    counts = [n for c in lane for rung in repeats[c].values() for n in rung.values()]
    original, shortened = max(counts), min(counts)
    totals = ", ".join(map(str, sorted({comparison["metrics"][c]["n"] for c in lane})))
    baseline = [n for rung in repeats["haiku-low"].values() for n in rung.values()]
    earlier = f"the earlier full-coverage lanes have {sum(baseline)} = {len(baseline)} problems × {baseline[0]} repeats"
    if original == shortened:
        return f"Totals ({totals}) use {original} repeats per problem; {earlier}; read the rung reached, not the total."
    changed = min(int(g) for c in lane for g, rung in repeats[c].items() if min(rung.values()) < original)
    return (f"Totals differ ({totals}) because the run was shortened from {original} to {shortened} repeats "
            f"partway through L{changed} and extra repeats already run were kept; {earlier}; "
            "read the rung reached, not the total.")


def tables(comparison, lane, money):
    m, profiles = comparison["metrics"], comparison["profiles"]
    spec = lambda head, rows: {"head": head, "rows": rows}
    reach = []
    equivalent = []
    rungs = sorted({g for v in lane.values() for g in v["by_rung"]}, key=lambda g: int(g[1:]))
    for c, v in lane.items():
        cleared, miss = profiles[c]
        reach.append([c, f"L{cleared}" + (" (not run further)" if miss is None else ""),
                      *[f'{v["by_rung"][g]["passed"]}/{v["by_rung"][g]["n"]}' if g in v["by_rung"] else "–" for g in rungs],
                      f'{m[c]["passes"]}/{m[c]["n"]}', f'{m[c]["median_s"]:.1f}', money(m[c]["usd_per_pass"]),
                      f'{len(v["by_problem"])} problems', money(v["usd_total"])])
        for e in comparison["matches"][c]:
            other = m[e]
            ec, em = profiles[e]
            ratio = lambda key: "–" if m[c][key] is None or not other[key] else f'{m[c][key] / other[key]:.1f}×'
            equivalent.append([c, configs.family(e), configs.display(e), f"L{ec}", f"L{em}" if em else "none",
                               f'{other["passes"]}/{other["n"]}', f'{other["median_s"]:.1f}', money(other["usd_per_pass"]),
                               ratio("median_s"), ratio("usd_per_pass")])
        if not comparison["matches"][c]:
            equivalent.append([c, "–", "no matching profile"] + ["–"] * 7)
    return {"grok_reach": spec(["config", "cleared through", *rungs, "passes", "median s", "$ per pass", "coverage", "total $"], reach),
            "grok_equivalent": spec(["Grok config", "family", "closest equivalent", "cleared through", "first miss",
                                     "same-problem passes", "median s", "$ per pass", "Grok time / equivalent", "Grok cost / equivalent"], equivalent)}
