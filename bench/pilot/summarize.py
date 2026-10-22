"""Summarise rows -> summary{_round2}.json/.md. All $ recomputed here from raw token fields (cost_of).
score = pass_rate/(median_wall_s*mean_cost), best=100 within each harness group (on / off)."""
import json, statistics as st, collections, os, sys
PH = sys.argv[1] if len(sys.argv) > 1 else "r1"; SUF = "" if PH == "r1" else "_" + PH
D = os.path.dirname(os.path.abspath(__file__))
# per 1M tokens: in / cached-in / out. Third-party (eesel.ai) except gpt-5.6-terra (developers.openai.com); gpt-6-sol inferred.
PRICES = {"gpt-6.1-sol": (2.0, 0.10, 10.0), "gpt-6-sol": (2.0, 0.20, 10.0), "gpt-5.6-terra": (2.0, 0.20, 12.0),
          "gpt-6-astra": (10.0, 1.0, 50.0), "gpt-6-luna": (0.10, 0.01, 0.50)}
PRIORITY_MULT = 1.5  # from a comment in ~/.codex/config.toml; unverified

def cost_of(r):
    """One place for $: Claude = CLI-reported list cost; Codex = API list price on raw tokens, x1.5 if priority tier."""
    if r["cli"].startswith("claude"): return r["cost_usd"]
    pi, pc, po = PRICES[r["model"]]
    std = ((r["in_tok"] - r["cached_tok"]) * pi + r["cached_tok"] * pc + r["out_tok"] * po) / 1e6
    return std * (PRIORITY_MULT if r["service_tier"].startswith("priority") else 1)

HARNESS = {"claude": "off", "codex-bare": "trimmed", "codex-lean": "trimmed", "claude-agent": "on", "codex": "on"}
GROUP = {"on": "on", "off": "off", "trimmed": "off"}  # trimmed Codex is scored with tools-off Claude
q = lambda xs: st.quantiles(xs, n=4, method="inclusive") if len(xs) > 1 else [xs[0]] * 3
rows = [json.loads(l) for l in open(f"{D}/results.jsonl") if l.strip()]
rows = [r for r in rows if (r.get("phase") in ("main", "variant", "ladder", "fair") if PH == "r1" else r.get("phase") == "round2")]
by = collections.defaultdict(list)
for r in rows: by[r["config"]].append(r)
out = []
for c, rs in by.items():
    probs = collections.defaultdict(list)
    for r in rs: probs[r["problem"]].append(bool(r["passed"]))
    walls = [r["wall_s"] for r in rs]; costs = [cost_of(r) for r in rs]; wq = q(walls)
    tiers = sorted({r["service_tier"] for r in rs})
    out.append(dict(config=c, cli=rs[0]["cli"], model=rs[0]["model"], effort=rs[0]["effort"], harness=HARNESS[rs[0]["cli"]],
        service_tier="/".join(tiers), rounds=len({r["round"] for r in rs}), runs=len(rs), passes=sum(r["passed"] for r in rs),
        pass_rate=sum(r["passed"] for r in rs) / len(rs),
        problems_passed=sum(all(v) for v in probs.values()), problems=len(probs),
        failed=[p for p, v in probs.items() if not all(v)],
        med_wall=wq[1], p25_wall=wq[0], p75_wall=wq[2], min_wall=min(walls), max_wall=max(walls),
        med_wall_by_prob={p: round(st.median(r["wall_s"] for r in rs if r["problem"] == p), 1) for p in probs},
        mean_in=st.mean(r["in_tok"] for r in rs), mean_cached=st.mean(r["cached_tok"] or 0 for r in rs),
        cache_pct=100 * sum(r["cached_tok"] or 0 for r in rs) / sum(r["in_tok"] for r in rs),
        mean_out=st.mean(r["out_tok"] for r in rs), mean_reason=st.mean(r["reasoning_tok"] or 0 for r in rs),
        mean_cost=st.mean(costs), med_cost=st.median(costs), min_cost=min(costs), max_cost=max(costs),
        cost_kind="list (CLI)" if rs[0]["cli"].startswith("claude") else "proxy", tool_items=sum(r.get("tool_items", 0) for r in rs)))
for o in out: o["raw"] = o["pass_rate"] / (o["med_wall"] * o["mean_cost"])
for g in ("on", "off"):
    grp = [o for o in out if GROUP[o["harness"]] == g]
    if not grp: continue
    best = max(o["raw"] for o in grp)
    for o in grp: o["score"] = round(100 * o["raw"] / best, 1)
out.sort(key=lambda o: (GROUP[o["harness"]] != "on", -o["score"]))
json.dump(out, open(f"{D}/summary{SUF}.json", "w"), indent=1)
lines = ["| harness | config | tier | pass | med s (p25–p75) | tok in (cache %) / out | $ mean / median | score |", "|---|---|---|---|---|---|---|---|"]
for o in out:
    lines.append(f"| {o['harness']} | {o['config']} | {o['service_tier']} | {o['passes']}/{o['runs']}{' FAIL:'+','.join(o['failed']) if o['failed'] else ''} | {o['med_wall']:.2f} ({o['p25_wall']:.1f}–{o['p75_wall']:.1f}) | {o['mean_in']:.0f} ({o['cache_pct']:.0f}%) / {o['mean_out']:.0f} | {'~' if o['cost_kind']=='proxy' else ''}{o['mean_cost']:.4f} / {o['med_cost']:.4f} | {o['score']} |")
open(f"{D}/summary{SUF}.md", "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
