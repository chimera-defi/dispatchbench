"""Generate completions for the function track. Every call is cached; a cached key never calls a model again.

python3 -m bench.run --phase main --configs haiku-low,luna-low --problems all --repeats 1-5 --lanes 4

Cache entry: cache/calls/<sha256>.json with the completion text, token usage, wall time and CLI metadata.
Grading is a separate step (bench.grade_all), so lanes never compete with timed test runs."""
import argparse, datetime, hashlib, json, os, shutil, subprocess, sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor

from bench import problems

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALLS = os.path.join(ROOT, "cache", "calls")
RAW = os.path.join(ROOT, "cache", "raw")  # full CLI stdout, gitignored (may contain local paths)
CLAUDE = os.environ.get("CLAUDE_BIN", "claude")
CODEX = os.environ.get("CODEX_BIN", "codex")
CLAUDE_BUDGET_USD = 8.00

CONFIGS = {}
for fam, mid in [("haiku", "claude-haiku-5-5"), ("sonnet", "claude-sonnet-5-5")]:
    for e in ["low", "medium", "high"]:
        CONFIGS[f"{fam}-{e}"] = ("claude", mid, e)
for fam, mid in [("luna", "gpt-6-luna"), ("sol61", "gpt-6.1-sol")]:
    for e in ["low", "medium", "high"]:
        CONFIGS[f"{fam}-{e}"] = ("codex", mid, e)

# Exploratory, added after the main run (not pre-registered): luna-low with the leanest Codex harness found by
# bench/trim_probe.py ("noshell": tool features, shell and base instructions stripped). See PLAN.md, Deviations.
CONFIGS["luna-low-bare"] = ("codex", "gpt-6-luna", "low")
TRIM_LEVEL = {"luna-low-bare": "noshell"}


def codex_flags(config, portable=False):
    if config not in TRIM_LEVEL:
        return CODEX_FLAGS
    from bench import trim_probe as T  # late import: trim_probe imports this module
    return CODEX_FLAGS + T.LEVELS[TRIM_LEVEL[config]] if portable else T.flags(TRIM_LEVEL[config])


# Function track harness. Claude: no tools, no user/project settings. Codex: user config ignored, host skill list
# dropped, default (non-priority) tier, read-only sandbox (Codex tools cannot be switched off).
CLAUDE_FLAGS = ["--output-format", "json", "--no-session-persistence", "--tools", "", "--setting-sources", "", "--strict-mcp-config"]
CODEX_FLAGS = ["--ignore-user-config", "-c", "skills.include_instructions=false", "-c", "service_tier=default",
               "--json", "--ephemeral", "--skip-git-repo-check", "-s", "read-only"]

TEMPLATE = """Solve this problem in Python 3.

{statement}

Implement exactly this function (a top-level function, not a class):
```python
{signature}
```
Reply with only the code in a single ```python block. Do not run any commands or tools."""

_versions = {}


def cli_version(cli):
    if cli not in _versions:
        exe = CLAUDE if cli == "claude" else CODEX
        _versions[cli] = subprocess.run([exe, "--version"], capture_output=True, text=True).stdout.strip().split()[-1 if cli == "codex" else 0]
    return _versions[cli]


def prompt_for(pid):
    m = problems.load(pid)
    return TEMPLATE.format(statement=m.STATEMENT.strip(), signature=m.SIGNATURE)


def key_for(config, pid, rep, prompt):
    cli, mid, eff = CONFIGS[config]
    flags = CLAUDE_FLAGS if cli == "claude" else codex_flags(config, portable=True)
    blob = json.dumps({"config": config, "model": mid, "effort": eff, "cli": cli, "cli_version": cli_version(cli),
                       "flags": flags, "prompt": prompt, "problem": pid, "repeat": rep}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def claude_spend():
    total = 0.0
    if os.path.isdir(CALLS):
        for f in os.listdir(CALLS):
            d = json.load(open(os.path.join(CALLS, f)))
            if d["cli"] == "claude": total += d.get("cost_usd") or 0.0
    return total


def call_claude(mid, eff, prompt, cwd):
    cmd = [CLAUDE, "-p", prompt, "--model", mid, "--effort", eff] + CLAUDE_FLAGS
    t = time.monotonic(); r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=cwd, timeout=1200)
    wall = time.monotonic() - t
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        return dict(wall_s=wall, text="", is_error=True, error=(r.stderr or r.stdout)[-300:]), r.stdout
    u = d.get("usage", {})
    return dict(wall_s=wall, text=d.get("result", ""), is_error=bool(d.get("is_error")), error=None if not d.get("is_error") else d.get("result", "")[:300],
                api_duration_ms=d.get("duration_api_ms"),
                in_tok=u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0),
                cached_tok=u.get("cache_read_input_tokens", 0), cache_write_tok=u.get("cache_creation_input_tokens", 0),
                out_tok=u.get("output_tokens", 0), reasoning_tok=(u.get("output_tokens_details") or {}).get("thinking_tokens", 0),
                cost_usd=d.get("total_cost_usd"), cost_kind="measured (CLI total_cost_usd)", turns=d.get("num_turns")), r.stdout


def parse_codex(stdout):
    i = c = o = rs = 0; tools = 0; err = None; text = ""
    for line in stdout.splitlines():
        try: ev = json.loads(line)
        except json.JSONDecodeError: continue
        if ev.get("type") == "turn.completed":
            u = ev.get("usage", {}); i += u.get("input_tokens", 0); c += u.get("cached_input_tokens", 0)
            o += u.get("output_tokens", 0); rs += u.get("reasoning_output_tokens", 0)
        if ev.get("type") in ("error", "turn.failed"): err = line[:300]
        it = ev.get("item") or {}
        if ev.get("type") == "item.completed":
            if it.get("type") == "agent_message": text = it.get("text", text)
            elif it.get("type") != "reasoning": tools += 1
    return dict(in_tok=i, cached_tok=c, cache_write_tok=0, out_tok=o, reasoning_tok=rs, tool_items=tools, error=err, text=text)


def call_codex(mid, eff, prompt, cwd, flags=CODEX_FLAGS):
    cmd = [CODEX, "exec", "-m", mid, "-c", f"model_reasoning_effort={eff}"] + flags + ["-C", cwd, prompt]
    t = time.monotonic(); r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=1200)
    wall = time.monotonic() - t
    p = parse_codex(r.stdout)
    p.update(wall_s=wall, is_error=bool(p["error"]) or r.returncode != 0, cost_usd=None, cost_kind="proxy (list price x tokens)")
    if r.returncode and not p["error"]: p["error"] = r.stderr.strip()[-300:]
    return p, r.stdout


_lock = threading.Lock()


def one(config, pid, rep, phase, lanes):
    prompt = prompt_for(pid); key = key_for(config, pid, rep, prompt); fp = os.path.join(CALLS, key + ".json")
    if os.path.exists(fp):
        return "cached"
    cli, mid, eff = CONFIGS[config]
    if cli == "claude":
        with _lock:
            spent = claude_spend()
        if spent >= CLAUDE_BUDGET_USD:
            return f"refused: Claude spend ${spent:.2f} >= ${CLAUDE_BUDGET_USD}"
    cwd = tempfile.mkdtemp(prefix="mrb-")
    try:
        res, raw = call_claude(mid, eff, prompt, cwd) if cli == "claude" else call_codex(mid, eff, prompt, cwd, codex_flags(config))
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
    if res.get("error"):
        res["error"] = res["error"].replace(cwd, "<cwd>").replace(os.path.expanduser("~"), "~")
    entry = dict(key=key, ts=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), phase=phase, config=config, cli=cli,
                 cli_version=cli_version(cli), model=mid, effort=eff, problem=pid, repeat=rep, lanes=lanes,
                 prompt_sha=hashlib.sha256(prompt.encode()).hexdigest()[:12], **res)
    if entry["is_error"] and "quota" in (entry.get("error") or "").lower():
        entry["quota_error"] = True
    os.makedirs(CALLS, exist_ok=True); os.makedirs(RAW, exist_ok=True)
    json.dump(entry, open(fp + ".tmp", "w"), indent=1); os.replace(fp + ".tmp", fp)
    open(os.path.join(RAW, key + ".out"), "w").write(raw)
    return f"{'ERR ' if entry['is_error'] else ''}{entry['wall_s']:.1f}s out={entry.get('out_tok')}"


def parse_reps(s):
    a, _, b = s.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True); ap.add_argument("--configs", required=True)
    ap.add_argument("--problems", default="all"); ap.add_argument("--repeats", default="1-5"); ap.add_argument("--lanes", type=int, default=4)
    a = ap.parse_args()
    cfgs = a.configs.split(","); pids = problems.IDS if a.problems == "all" else a.problems.split(","); reps = parse_reps(a.repeats)
    assert a.lanes <= 4, "at most 4 lanes (timing hygiene)"
    for c in cfgs: assert c in CONFIGS, c

    def lane(cfg):  # one config per lane; calls inside a lane are sequential
        for rep in reps:
            for pid in pids:
                msg = one(cfg, pid, rep, a.phase, a.lanes)
                print(f"[{a.phase}] {cfg} {pid} r{rep}: {msg}", flush=True)
                if msg.startswith("refused"): return
    with ThreadPoolExecutor(a.lanes) as ex:
        list(ex.map(lane, cfgs))
    print(f"Claude spend so far: ${claude_spend():.4f}")


if __name__ == "__main__":
    main()
