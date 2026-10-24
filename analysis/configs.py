"""Complete, read-only inventory of result configurations and their recorded trials.

A raw config/arm has one display name and one registry entry, even when it was
run on several sets. Measurements stay separate by experiment: never pool L7,
pilot, warmup, or rescue attempts with the main ladder. Quality/command audits
register names for coverage but are not additional benchmark attempts.
"""
from collections import defaultdict
from pathlib import Path
import statistics

from analysis.labels import DISP
from analysis.summarize import RES, cost, load, pilot_block, usd

CATEGORIES = (
    "Main ladder", "L7", "Rescue / pipelines", "Pilot", "Trim probes",
    "Harness bias / appendix arms", "Repo tasks", "Fast mode / priority variants",
)


RESCUE_NAMES = {c: DISP(c) for c in ("luna-low", "luna-high-bare", "haiku-low", "haiku-medium", "haiku-high", "sonnet-medium", "sol61-medium",
                                   "sol61-high", "sol61-high-fast", "astra-medium", "astra-medium-fast", "sol56-high", "luna56-high", "luna56-low")}
for builder in ("sol61-high", "astra-medium", "luna-low", "luna-high-bare"):
    RESCUE_NAMES[builder + "+haiku-on-fail"] = DISP(builder) + " → Haiku if samples fail"
    if builder + "-fast" in RESCUE_NAMES:
        RESCUE_NAMES[builder + "-fast+haiku-on-fail"] = DISP(builder + "-fast") + " → Haiku if samples fail"
RESCUE_NAMES.update({"haiku-low-plan+luna-low": "Haiku plan → luna-low", "haiku-low-plan+luna-high-bare": "Haiku plan → luna-high-bare",
             "luna-high-bare+retry-on-fail": "luna-high-bare → retry if samples fail",
             "luna-low+haiku-review-all": "luna-low → Haiku fixes all", "luna-high-bare+haiku-review-all": "luna-high-bare → Haiku fixes all"})


def display_name(c):
    return RESCUE_NAMES.get(c, DISP(c))


def category(path, r):
    if "pilot-agentic" in path.name:
        return "Pilot", "pilot repo tasks"
    if "pilot" in path.name:
        return "Pilot", "pilot"
    if "trim" in path.name:
        return "Trim probes", "trim probes"
    if "luna_rescue" in path.name:
        return ("Rescue / pipelines" if "+" in r["config"] else "Harness bias / appendix arms"), "rescue"
    if "agentic" in path.name:
        return "Repo tasks", "repo tasks"
    phase = r.get("phase")
    if phase in ("main", "exploratory", "escalation"):
        return "Main ladder", "main ladder"
    if phase == "hard":
        return "L7", "L7"
    if phase == "fastmode":
        # summarize.build reuses this original rescue sample as part of the
        # full sol61-high-fast ladder; count the recorded trials once here too.
        if r["config"] == "sol61-high-fast":
            return "Main ladder", "main ladder"
        return "Fast mode / priority variants", "separate rescue control"
    return "Harness bias / appendix arms", phase or "other"


def registry():
    """One entry per recorded config, with per-experiment metrics (None = absent)."""
    entries = {}
    samples = defaultdict(list)
    seen = set()
    pilot = pilot_block()  # uses the existing, priority-corrected pilot pricing
    for path in sorted(Path(RES).rglob("*.jsonl")):
        for r in load(path):
            c = r.get("config")
            if c is None and "pilot-agentic" in path.name:
                c = "pilot-repo-" + r["pipeline"]
            if c is None:
                continue
            entry = entries.setdefault(c, dict(config=c, name=display_name(c), categories=set(), measurements=[]))
            if "passed" not in r and "hidden_pass" not in r:
                continue  # quality and shell-command analyses describe existing trials
            group, context = category(path, r)
            if c.endswith(("-fast", "-prio")) or "priority" in (r.get("service_tier") or ""):
                group = "Fast mode / priority variants"
            entry["categories"].add(group)
            # Escalation and trim-floor exports can repeat a cached trial.
            key = (c, context, r.get("key"))
            if key[-1] is not None:
                if key in seen:
                    continue
                seen.add(key)
            passed = r.get("hidden_pass", r.get("passed"))
            wall = r.get("wall_s")
            if "pilot-agentic" in path.name:
                review = r.get("review") or {}
                wall = r["builder_wall_s"] + review.get("wall_s", 0)
                dollars = r["builder_cost_usd"] + review.get("cost_usd", 0)
            elif "pilot" in path.name:
                dollars = pilot[c]["usd_per_call"]
            elif "cli" in r:
                dollars = cost(r)
            else:
                dollars = r.get("cost_usd")  # appendix pipelines already include both steps
            samples[c, context].append((passed, dollars, wall))
    for (c, context), rr in samples.items():
        passes = sum(bool(r[0]) for r in rr) if all(r[0] is not None for r in rr) else None
        walls = [r[2] for r in rr]
        entries[c]["measurements"].append(dict(
            context=context, attempts=len(rr), passed=passes,
            usd_per_pass=usd((r[1] for r in rr), passes) if passes else None,
            median_s=statistics.median(walls) if all(v is not None for v in walls) else None,
        ))
    for entry in entries.values():
        # Configs used on multiple sets appear once; labelled cell lines retain every set.
        entry["category"] = next((g for g in CATEGORIES if g in entry["categories"]), "Harness bias / appendix arms")
        entry["measurements"].sort(key=lambda m: m["context"])
    return entries
