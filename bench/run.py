"""Generate completions for the function track. Every call is cached; successful cached keys never call a model again; infrastructure failures get one retry.

python3 -m bench.run --phase main --configs haiku-low,luna-low --problems all --repeats 1-5 --lanes 4
python3 -m bench.run --phase hard --configs sonnet-medium,sol61-medium,haiku-low,luna-high --problems hard --repeats 1-5 --lanes 4
python3 -m bench.run --phase fastmode --configs sol61-high-fast,sol61-xhigh --problems hard --repeats 1-5 --lanes 4   # control: sol61-high --repeats 6-10

Cache entry: cache/calls/<sha256>.json with the completion text, token usage, wall time and CLI metadata.
Grading is a separate step (bench.grade_all), so lanes never compete with timed test runs."""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor

from bench import problems
from bench.codex_env import isolated_codex_env

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALLS = os.path.join(ROOT, "cache", "calls")
RAW = os.path.join(ROOT, "cache", "raw")  # full CLI stdout, gitignored (may contain local paths)
CLAUDE = os.environ.get("CLAUDE_BIN", "claude")
CODEX = os.environ.get("CODEX_BIN", "codex")
GROK = os.environ.get("GROK_BIN", "grok")
CLAUDE_BUDGET_USD = 8.00
GROK_BUDGET_USD = 60.00  # raised 2026-10-28 for the full-spectrum Grok run.

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
# Exploratory, 2026-10-23, at the operator's request: the previous Codex generation and the flagship, stock harness.
CONFIGS.update({"sol56-high": ("codex", "gpt-5.6-sol", "high"), "luna56-low": ("codex", "gpt-5.6-luna", "low"),
                "luna56-high": ("codex", "gpt-5.6-luna", "high"), "astra-medium": ("codex", "gpt-6-astra", "medium")})
# Exploratory, 2026-10-23, at the operator's request: sol61-high in fast mode (priority tier, same model and effort) as a
# fan-out default, and sol61 at xhigh effort for the "does more effort write worse code" question. Hard set only.
CONFIGS.update({"sol61-high-fast": ("codex", "gpt-6.1-sol", "high"), "sol61-xhigh": ("codex", "gpt-6.1-sol", "xhigh")})
# Exploratory, 2026-10-24, at the operator's request: both trusted Codex builders in fast mode on the main ladder and L7.
CONFIGS["astra-medium-fast"] = ("codex", "gpt-6-astra", "medium")
TIER = {"sol61-high-fast": "priority", "astra-medium-fast": "priority", "terra56-high-fast": "priority"}
# Exploratory, 2026-10-28, at the operator's request: Codex Terra (gpt-5.6-terra) on the main ladder, plus high in
# fast mode (priority tier, same model and effort). See PLAN.md.
CONFIGS.update({"terra56-low": ("codex", "gpt-5.6-terra", "low"), "terra56-high": ("codex", "gpt-5.6-terra", "high"),
                "terra56-high-fast": ("codex", "gpt-5.6-terra", "high")})
# Exploratory, 2026-10-26, operator request (hackathon): staged L1-L3 Grok lane; see PLAN.md.
CONFIGS.update({f"grok47-{e}": ("grok", "grok-4.7", e) for e in ("low", "medium", "high")})
CONFIGS["grok47fast-low"] = ("grok", "grok-4.7-build-fast", "low")


def codex_flags(config, portable=False):
    if config in TIER:
        return [f"service_tier={TIER[config]}" if f == "service_tier=default" else f for f in CODEX_FLAGS]
    if config not in TRIM_LEVEL:
        return CODEX_FLAGS
    from bench import trim_probe as T  # late import: trim_probe imports this module
    if hashlib.sha256(open(T.MIN_INST, "rb").read()).hexdigest() != T.MIN_INST_SHA:
        raise SystemExit("min_instructions.txt changed: add its hash to the cache key before making new calls")
    return CODEX_FLAGS + T.LEVELS[TRIM_LEVEL[config]] if portable else T.flags(TRIM_LEVEL[config])


# Function track harness. Claude: no tools, no user/project settings. Codex: fresh HOME/CODEX_HOME,
# auth symlink only, user config ignored, default tier, read-only sandbox.
CLAUDE_FLAGS = ["--output-format", "json", "--no-session-persistence", "--tools", "", "--setting-sources", "", "--strict-mcp-config"]
# Empty/unknown allowlists retain defaults. Allow one known tool, then deny it and the always-on MCP meta-tools.
# https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-agent/src/tool_list.rs
GROK_FLAGS = ["--output-format", "json", "--tools", "read_file", "--disallowed-tools", "read_file,search_tool,use_tool",
              "--no-subagents", "--disable-web-search",
              "--max-turns", "1", "--no-plan", "--verbatim", "--permission-mode", "dontAsk", "--no-leader"]
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
        exe = {"claude": CLAUDE, "codex": CODEX, "grok": GROK}[cli]
        if cli == "codex":
            with isolated_codex_env() as env:
                version = subprocess.run([exe, "--version"], env=env, capture_output=True, text=True).stdout
        else:
            version = subprocess.run([exe, "--version"], capture_output=True, text=True).stdout
        _versions[cli] = version.strip().split()[1 if cli == "grok" else -1 if cli == "codex" else 0]
    return _versions[cli]


def prompt_for(pid):
    m = problems.load(pid)
    return TEMPLATE.format(statement=m.STATEMENT.strip(), signature=m.SIGNATURE)


def key_for(config, pid, rep, prompt):
    cli, mid, eff = CONFIGS[config]
    flags = CLAUDE_FLAGS if cli == "claude" else GROK_FLAGS if cli == "grok" else codex_flags(config, portable=True)
    identity = {"config": config, "model": mid, "effort": eff, "cli": cli, "cli_version": cli_version(cli),
                "flags": flags, "prompt": prompt, "problem": pid, "repeat": rep}
    if cli == "codex": identity["codex_home"] = "isolated"
    blob = json.dumps(identity, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def claude_spend(cache_root=None):
    """Known Claude CLI cost across every cache directory, including retained retry receipts."""
    def amount(d):
        if not isinstance(d, dict): return 0.0
        claude = (d.get("cli") == "claude" or str(d.get("model", "")).startswith("claude") or
                  (not d.get("cli") and not d.get("model") and d.get("cost_kind", "").startswith("measured")))
        return ((d.get("cost_usd") or 0.0) if claude else 0.0) + amount(d.get("previous_attempt"))
    total = 0.0
    for base, _, files in os.walk(cache_root or os.path.join(ROOT, "cache")):
        for f in files:
            if f.endswith(".json"):
                with open(os.path.join(base, f)) as src: total += amount(json.load(src))
    return total


def grok_spend(cache_root=None):
    """Known Grok CLI cost, including the tool probe and retained retry receipts."""
    def amount(d):
        if not isinstance(d, dict): return 0.0
        grok = d.get("cli") == "grok" or str(d.get("model", "")).startswith("grok-")
        return ((d.get("cost_usd") or 0.0) if grok else 0.0) + amount(d.get("previous_attempt"))
    total = 0.0
    for base, _, files in os.walk(cache_root or os.path.join(ROOT, "cache")):
        for f in files:
            if f.endswith(".json"):
                with open(os.path.join(base, f)) as src: total += amount(json.load(src))
    return total


class SpendLimit(RuntimeError): pass


def check_claude_budget():
    spent = claude_spend()
    if spent >= CLAUDE_BUDGET_USD:
        raise SpendLimit(f"refused: Claude spend ${spent:.2f} >= ${CLAUDE_BUDGET_USD}")


def check_grok_budget():
    spent = grok_spend()
    if spent >= GROK_BUDGET_USD:
        raise SpendLimit(f"refused: Grok spend ${spent:.2f} >= ${GROK_BUDGET_USD}")


def error_kind(row):
    msg = (row.get("error") or "").lower()
    if row.get("quota_error") or re.search(r"quota|rate[ _-]?limit|too many requests|\b429\b|usage limit", msg): return "limit"
    if row.get("error_type") == "infrastructure" or row.get("outcome") in ("timeout", "harness_error") or re.search(r"infrastructure|temporary|overloaded|connection|econn|timed? ?out|timeout|\b50[0234]\b", msg): return "infrastructure"
    return "model"


def cache_state(fp):
    if not os.path.exists(fp): return None, None
    with open(fp) as src: prior = json.load(src)
    if prior.get("is_error") and error_kind(prior) == "limit": return "stopped: quota/rate limit", prior
    if prior.get("is_error") and error_kind(prior) == "infrastructure" and prior.get("retry_count", 0) < 1: return None, prior
    return "cached", prior


def failure(exc, wall):
    timeout = isinstance(exc, subprocess.TimeoutExpired)
    raw = getattr(exc, "stdout", "") or ""
    if isinstance(raw, bytes): raw = raw.decode(errors="replace")
    return dict(wall_s=wall, text="", is_error=True, error=str(exc)[-300:], error_type="infrastructure",
                outcome="timeout" if timeout else "harness_error", cost_usd=None, in_tok=0, cached_tok=0,
                cache_write_tok=0, out_tok=0, reasoning_tok=0), raw


def stop_message(entry):
    return "stopped: quota/rate limit" if entry.get("is_error") and error_kind(entry) == "limit" else None


def call_claude(mid, eff, prompt, cwd):
    check_claude_budget()
    cmd = [CLAUDE, "-p", prompt, "--model", mid, "--effort", eff] + CLAUDE_FLAGS
    t = time.monotonic(); r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=cwd, timeout=1200)
    wall = time.monotonic() - t
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        return dict(wall_s=wall, text="", is_error=True, error=(r.stderr or r.stdout)[-300:], error_type="infrastructure", cost_usd=None), r.stdout
    u = d.get("usage", {})
    return dict(wall_s=wall, text=d.get("result", ""), is_error=bool(d.get("is_error")) or r.returncode != 0,
                error=(r.stderr or d.get("result", ""))[-300:] if r.returncode or d.get("is_error") else None,
                error_type="infrastructure" if r.returncode else "model",
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


def call_grok(mid, eff, prompt, cwd):
    check_grok_budget()
    cmd = [GROK, "-p", prompt, "-m", mid, "--reasoning-effort", eff] + GROK_FLAGS
    t = time.monotonic()
    r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=cwd, timeout=1200)
    wall = time.monotonic() - t
    try:
        d = json.loads(r.stdout)
        if not isinstance(d, dict): raise ValueError("expected a JSON object")
    except (ValueError, TypeError):
        return dict(wall_s=wall, text="", is_error=True, error=(r.stderr or r.stdout)[-300:],
                    error_type="infrastructure", cost_usd=None), r.stdout
    u = d.get("usage") or {}
    error = d.get("error")
    is_error = bool(d.get("is_error") or error or r.returncode)
    return dict(wall_s=wall, text=d.get("text", ""), is_error=is_error,
                error=str(r.stderr or error or d.get("text", ""))[-300:] if is_error else None,
                error_type="infrastructure" if r.returncode else "model",
                in_tok=u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0),
                cached_tok=u.get("cache_read_input_tokens", 0), cache_write_tok=u.get("cache_creation_input_tokens", 0),
                out_tok=u.get("output_tokens", 0), reasoning_tok=u.get("reasoning_tokens", 0),
                cost_usd=d.get("total_cost_usd"), cost_kind="measured (CLI total_cost_usd)",
                turns=d.get("num_turns")), r.stdout


def call_codex(mid, eff, prompt, cwd, flags=CODEX_FLAGS):
    cmd = [CODEX, "exec", "-m", mid, "-c", f"model_reasoning_effort={eff}"] + flags + ["-C", cwd, prompt]
    t = time.monotonic()
    with isolated_codex_env() as env:
        r = subprocess.run(cmd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=1200)
    wall = time.monotonic() - t
    p = parse_codex(r.stdout)
    p.update(wall_s=wall, is_error=bool(p["error"]) or r.returncode != 0, cost_usd=None, cost_kind="proxy (list price x tokens)")
    if r.returncode and not p["error"]: p["error"] = r.stderr.strip()[-300:]
    if p["is_error"]: p["error_type"] = "infrastructure"
    return p, r.stdout


def one(config, pid, rep, phase, lanes):
    prompt = prompt_for(pid); key = key_for(config, pid, rep, prompt); fp = os.path.join(CALLS, key + ".json")
    status, prior = cache_state(fp)
    if status: return status
    cli, mid, eff = CONFIGS[config]
    cwd = tempfile.mkdtemp(prefix="mrb-")
    t0 = time.monotonic()
    try:
        if cli == "claude": res, raw = call_claude(mid, eff, prompt, cwd)
        elif cli == "grok": res, raw = call_grok(mid, eff, prompt, cwd)
        else: res, raw = call_codex(mid, eff, prompt, cwd, codex_flags(config))
    except SpendLimit as exc:
        return str(exc)
    except (subprocess.TimeoutExpired, OSError) as exc:
        res, raw = failure(exc, time.monotonic() - t0)
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
    if res.get("error"):
        res["error"] = res["error"].replace(cwd, "<cwd>").replace(os.path.expanduser("~"), "~")
    entry = dict(key=key, ts=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), phase=phase, config=config, cli=cli,
                 cli_version=cli_version(cli), model=mid, effort=eff, problem=pid, repeat=rep, lanes=lanes,
                 prompt_sha=hashlib.sha256(prompt.encode()).hexdigest()[:12], **res)
    entry["retry_count"] = (prior.get("retry_count", 0) + 1) if prior else 0
    if cli == "codex": entry["codex_home"] = "isolated"
    if prior: entry["previous_attempt"] = prior
    if stop_message(entry): entry["quota_error"] = True
    os.makedirs(CALLS, exist_ok=True); os.makedirs(RAW, exist_ok=True)
    tmp = f"{fp}.{os.getpid()}.{threading.get_ident()}.tmp"
    with open(tmp, "w") as f:
        json.dump(entry, f, indent=1)
    os.replace(tmp, fp)
    with open(os.path.join(RAW, key + ".out"), "w") as f:
        f.write(raw)
    return stop_message(entry) or f"{'ERR ' if entry['is_error'] else ''}{entry['wall_s']:.1f}s out={entry.get('out_tok')}"


def parse_reps(s):
    a, _, b = s.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True); ap.add_argument("--configs", required=True)
    ap.add_argument("--problems", default="all"); ap.add_argument("--repeats", default="1-5"); ap.add_argument("--lanes", type=int, default=4)
    a = ap.parse_args()
    cfgs = a.configs.split(","); pids = {"all": problems.MAIN, "hard": problems.HARD}.get(a.problems) or a.problems.split(","); reps = parse_reps(a.repeats)
    assert a.lanes <= 4, "at most 4 lanes (timing hygiene)"
    for c in cfgs: assert c in CONFIGS, c

    def lane(cfg):  # one config per lane; calls inside a lane are sequential
        for rep in reps:
            for pid in pids:
                msg = one(cfg, pid, rep, a.phase, a.lanes)
                print(f"[{a.phase}] {cfg} {pid} r{rep}: {msg}", flush=True)
                if msg.startswith(("refused", "stopped")): return
    with ThreadPoolExecutor(a.lanes) as ex:
        list(ex.map(lane, cfgs))
    print(f"Known Claude CLI cost across all cache dirs: ${claude_spend():.4f}")
    if any(CONFIGS[c][0] == "grok" for c in cfgs):
        print(f"Known Grok CLI cost across all cache dirs: ${grok_spend():.4f}")


if __name__ == "__main__":
    main()
