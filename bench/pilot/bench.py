"""One run: python3 bench.py <config> <problem> <round> [--tag pilot|main]. Appends one row to results.jsonl."""
import json, re, subprocess, sys, time, os, datetime
D = os.path.dirname(os.path.abspath(__file__))
CLAUDE = os.environ.get("CLAUDE_BIN", "claude")
CODEX = os.environ.get("CODEX_BIN", "codex")
VERS = {"claude": "2.1.308", "claude-agent": "2.1.308", "codex": "0.163.0", "codex-lean": "0.163.0", "codex-bare": "0.163.0"}
# $ per 1M tokens. Claude: total_cost_usd (costBasis=list) used directly.
# Codex proxy: gpt-6.1-sol standard list $2 in / $0.10 cached / $10 out (eesel.ai/blog/gpt-6-1-sol-pricing, 3rd-party; openai.com 403'd).
# Host config runs service_tier=priority; config comment says 1.5x usage -> PRIORITY_MULT applied to proxy.
PRICE = {"in": 2.0, "cached": 0.10, "out": 10.0}; PRIORITY_MULT = 1.5
# eesel.ai/blog/gpt-6-astra-pricing ($10/$1/$50) and eesel.ai/blog/gpt-6-luna-pricing ($0.10/$0.01/$0.50, single source)
# gpt-6-sol: eesel gpt-6-1-sol page ("input, cache writes, output stayed where GPT-6 Sol had them", cache $0.20); gpt-5.6-terra: developers.openai.com/api/docs/models/gpt-5.6-terra
PRICES = {"gpt-6.1-sol": PRICE, "gpt-6-sol": {"in": 2.0, "cached": 0.20, "out": 10.0}, "gpt-5.6-terra": {"in": 2.0, "cached": 0.20, "out": 12.0}, "gpt-6-astra": {"in": 10.0, "cached": 1.0, "out": 50.0}, "gpt-6-luna": {"in": 0.10, "cached": 0.01, "out": 0.50}}
CONFIGS = {}
for m, mid in [("haiku", "claude-haiku-5-5"), ("sonnet", "claude-sonnet-5-5")]:
    for e in ["low", "medium", "high"]:
        CONFIGS[f"{m}-{e}"] = ("claude", mid, e)
for e in ["low", "medium", "high", "xhigh"]:
    CONFIGS[f"codex-{e}"] = ("codex", "gpt-6.1-sol", e)
CONFIGS["astra-low"] = ("codex", "gpt-6-astra", "low")
CONFIGS["luna-low"] = ("codex", "gpt-6-luna", "low")
# ladder: explicit service tier per run (None = whatever ~/.codex/config.toml says, i.e. priority)
TIER = {}
for name, mid in [("sol61", "gpt-6.1-sol"), ("sol6", "gpt-6-sol"), ("astra", "gpt-6-astra"), ("luna", "gpt-6-luna"), ("terra56", "gpt-5.6-terra")]:
    for e in ["low", "medium", "high", "xhigh"]:
        for t in ["priority", "default"]:
            CONFIGS[f"{name}-{e}-{t[:4]}"] = ("codex", mid, e); TIER[f"{name}-{e}-{t[:4]}"] = t
CONFIGS["codex-bare"] = ("codex-bare", "gpt-6.1-sol", "low")  # skills list, multi-agent, AGENTS.md, env ctx and base prompt stripped; tool schemas can't be
BARE = ["-c", "skills.include_instructions=false", "--disable", "multi_agent", "-c", "project_doc_max_bytes=0",
        "-c", "include_environment_context=false", "-c", f'model_instructions_file="{D}/min_instructions.txt"']
CONFIGS["codex-low-lean"] = ("codex-lean", "gpt-6.1-sol", "low")  # --ignore-user-config: no AGENTS.md/host config, default tier
CONFIGS["haiku-low-agent"] = ("claude-agent", "claude-haiku-5-5", "low")  # harness ON: default tools + normal settings
CONFIGS["sonnet-medium-agent"] = ("claude-agent", "claude-sonnet-5-5", "medium")

TEMPLATE = open(os.path.join(D, "prompt_template.txt")).read()

def prompt(prob):
    return TEMPLATE.format(statement=open(f"{D}/problems/{prob}.md").read().strip(),
                           signature=open(f"{D}/problems/{prob}.sig").read().strip())

def extract(text):
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)
    return blocks[-1] if blocks else text

def run_claude(mid, eff, p, agent=False):
    # agent=True: harness ON (default tools + user/project settings), matching how Codex always runs
    cmd = [CLAUDE, "-p", p, "--model", mid, "--effort", eff, "--output-format", "json", "--no-session-persistence"] + \
          ([] if agent else ["--tools", "", "--setting-sources", ""])
    t = time.monotonic(); r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=f"{D}/sandbox", timeout=600); wall = time.monotonic() - t
    d = json.loads(r.stdout); u = d.get("usage", {})
    return dict(wall_s=wall, text=d.get("result", ""), is_error=d.get("is_error"), duration_ms=d.get("duration_ms"),
                in_tok=u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0),
                cached_tok=u.get("cache_read_input_tokens", 0), cache_write_tok=u.get("cache_creation_input_tokens", 0),
                out_tok=u.get("output_tokens", 0), reasoning_tok=(u.get("output_tokens_details") or {}).get("thinking_tokens", 0),
                cost_usd=d.get("total_cost_usd"), cost_kind="list", tool_items=max(0, (d.get("num_turns") or 1) - 1))

def run_codex(mid, eff, p, tag, lean=False, tier=None, bare=False):
    last = f"{D}/runs/{tag}.last.txt"
    cmd = [CODEX, "exec", "-m", mid, "-c", f"model_reasoning_effort={eff}", "--json", "--ephemeral",
           "--skip-git-repo-check", "-s", "read-only", "-C", f"{D}/sandbox", "-o", last] + (["--ignore-user-config"] if lean else []) + (["-c", f"service_tier={tier}"] if tier else []) + (BARE + ["-c", "service_tier=priority"] if bare else []) + [p]
    if os.path.exists(last): os.remove(last)
    t = time.monotonic(); r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=900); wall = time.monotonic() - t
    open(f"{D}/runs/{tag}.jsonl", "w").write(r.stdout)
    u = {}; tools = 0; err = None
    for line in r.stdout.splitlines():
        try: ev = json.loads(line)
        except Exception: continue
        if ev.get("type") == "turn.completed": u = ev.get("usage", {})
        if ev.get("type") in ("error", "turn.failed"): err = line[:300]
        it = ev.get("item") or {}
        if ev.get("type") == "item.completed" and it.get("type") not in ("agent_message", "reasoning"): tools += 1
    text = open(last).read() if os.path.exists(last) else ""
    i, c, o = u.get("input_tokens", 0), u.get("cached_input_tokens", 0), u.get("output_tokens", 0)
    pr = PRICES[mid]
    std = ((i - c) * pr["in"] + c * pr["cached"] + o * pr["out"]) / 1e6  # output_tokens includes reasoning (verified in pilot)
    return dict(wall_s=wall, text=text, is_error=bool(err) or r.returncode != 0, error=err or (r.stderr[-300:] if r.returncode else None),
                in_tok=i, cached_tok=c, cache_write_tok=u.get("cache_write_input_tokens", 0), out_tok=o,
                reasoning_tok=u.get("reasoning_output_tokens", 0), cost_usd=std * (1 if (lean or tier == "default") else PRIORITY_MULT), cost_std_usd=std,
                cost_kind="proxy(api-list)" if (lean or tier == "default") else "proxy(api-list x1.5 priority)", tool_items=tools,
                service_tier=("unset(--ignore-user-config)" if lean else "priority" if bare else (tier or "priority(config)")))

def main():
    cfg, prob, rnd = sys.argv[1], sys.argv[2], int(sys.argv[3]); phase = sys.argv[4] if len(sys.argv) > 4 else "main"
    kind, mid, eff = CONFIGS[cfg]; tag = f"{phase}-{cfg}-{prob}-r{rnd}"
    p = prompt(prob)
    res = run_claude(mid, eff, p, agent=(kind == "claude-agent")) if kind in ("claude", "claude-agent") else run_codex(mid, eff, p, tag, lean=(kind == "codex-lean"), tier=TIER.get(cfg), bare=(kind == "codex-bare"))
    code = extract(res.pop("text") or ""); cand = f"{D}/runs/{tag}.py"; open(cand, "w").write(code)
    try:
        ck = subprocess.run(["python3", "-I", f"{D}/checker.py", prob, cand], capture_output=True, text=True, timeout=300)
        verdict = json.loads(ck.stdout.strip().splitlines()[-1]) if ck.stdout.strip() else {"pass": False, "detail": ck.stderr[-300:]}
    except Exception as e:
        verdict = {"pass": False, "detail": f"checker: {e!r}"[:300]}
    row = dict(ts=datetime.datetime.now(datetime.timezone.utc).isoformat(), phase=phase, config=cfg, cli=kind, cli_version=VERS[kind],
               model=mid, effort=eff, problem=prob, round=rnd, **res, passed=verdict.get("pass"), check=verdict)
    with open(f"{D}/results.jsonl", "a") as f: f.write(json.dumps(row) + "\n")
    print(json.dumps({k: row[k] for k in ["config", "problem", "round", "passed", "wall_s", "in_tok", "out_tok", "reasoning_tok", "cost_usd", "tool_items"]}))

main()
