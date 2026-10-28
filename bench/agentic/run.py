"""Agentic track: each config edits a small repo with tools on; hidden tests are copied in only after the agent exits.

python3 -m bench.agentic.run --configs haiku-low,sonnet-medium,luna-low,sol61-medium --tasks all --repeats 1-3 --lanes 4
python3 -m bench.agentic.run --export        # rebuild results/2026-10-22b-agentic.jsonl from cache, no model calls

Cache entry: cache/agentic/<sha256>.json. The key covers config, CLI version, harness flags, the task prompt, a hash of the
task's starting repo and hidden tests, and the repeat number."""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor

from bench.run import CONFIGS, CLAUDE, CODEX, GROK, grok_spend, check_claude_budget, SpendLimit, cache_state, failure, stop_message, cli_version, parse_reps
from bench.codex_env import isolated_codex_env

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TASKS = os.path.join(ROOT, "bench", "agentic", "tasks")
CACHE = os.path.join(ROOT, "cache", "agentic")
RAW = os.path.join(ROOT, "cache", "raw")
PATCHES = os.path.join(ROOT, "cache", "agentic_patches")
GRADER_VERSIONS = {"t1_discount": 3}  # unchanged tasks keep version 2 cache identities
OUT = os.path.join(ROOT, "results", "2026-10-22b-agentic.jsonl")
TASK_IDS = sorted(d for d in os.listdir(TASKS) if d.startswith("t"))

# Matched harnesses: shell + file edit tools on both sides, no user/project settings, no MCP servers.
CLAUDE_FLAGS = ["--output-format", "stream-json", "--verbose", "--no-session-persistence", "--setting-sources", "",
                "--strict-mcp-config", "--tools", "Bash,Read,Edit,Write,Glob,Grep", "--permission-mode", "bypassPermissions"]
CODEX_FLAGS = ["--ignore-user-config", "-c", "skills.include_instructions=false", "-c", "service_tier=default",
               "--json", "--ephemeral", "--skip-git-repo-check", "-s", "workspace-write"]
GROK_FLAGS = ["--output-format", "json", "--always-approve", "--no-subagents", "--disable-web-search"]
GROK_BUDGET_USD = 15.0
GROK_OUT = os.path.join(ROOT, "results", "2026-10-27-grok-agentic.jsonl")
DELEGATE = re.compile(r"\b(devin|kimi|grok|delegate|codex exec|claude -p)\b")


def tree_hash(*dirs):
    h = hashlib.sha256()
    for d in dirs:
        for base, _, files in sorted(os.walk(d)):
            for f in sorted(files):
                p = os.path.join(base, f); h.update(os.path.relpath(p, d).encode()); h.update(open(p, "rb").read())
    return h.hexdigest()


def grader_version(task):
    return GRADER_VERSIONS.get(task, 2)


def key_for(config, task, rep, legacy=False):
    cli, mid, eff = CONFIGS[config]; t = os.path.join(TASKS, task)
    dirs = [os.path.join(t, "repo"), os.path.join(t, "hidden")] + ([] if legacy else [os.path.join(t, "solution")])
    identity = {"track": "agentic", "config": config, "model": mid, "effort": eff, "cli": cli, "cli_version": cli_version(cli),
                       "flags": {"claude": CLAUDE_FLAGS, "codex": CODEX_FLAGS, "grok": GROK_FLAGS}[cli], "prompt": open(os.path.join(t, "TASK.md")).read(),
                       "task": task, "task_tree": tree_hash(*dirs), "repeat": rep}
    if not legacy: identity["grader_version"] = grader_version(task)
    if cli == "codex": identity["codex_home"] = "isolated"
    blob = json.dumps(identity, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def run_claude(mid, eff, prompt, w):
    check_claude_budget()
    cmd = [CLAUDE, "-p", prompt, "--model", mid, "--effort", eff] + CLAUDE_FLAGS
    r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=w, timeout=1500)
    res = {}; tools = {}
    for line in r.stdout.splitlines():
        try: ev = json.loads(line)
        except json.JSONDecodeError: continue
        if ev.get("type") == "assistant":
            for c in ev.get("message", {}).get("content", []):
                if c.get("type") == "tool_use": tools[c["name"]] = tools.get(c["name"], 0) + 1
        if ev.get("type") == "result": res = ev
    u = res.get("usage", {})
    return dict(in_tok=u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0),
                cached_tok=u.get("cache_read_input_tokens", 0), cache_write_tok=u.get("cache_creation_input_tokens", 0),
                out_tok=u.get("output_tokens", 0), cost_usd=res.get("total_cost_usd"), cost_kind="measured (CLI total_cost_usd)",
                turns=res.get("num_turns"), tool_calls=tools, is_error=bool(res.get("is_error")) or not res or r.returncode != 0,
                error=None if res and not res.get("is_error") and not r.returncode else (r.stderr or res.get("result") or r.stdout)[-300:],
                error_type="infrastructure" if r.returncode or not res else "model", delegate_calls=0), r.stdout


def run_codex(mid, eff, prompt, w):
    cmd = [CODEX, "exec", "-m", mid, "-c", f"model_reasoning_effort={eff}"] + CODEX_FLAGS + ["-C", w, prompt]
    with isolated_codex_env() as env:
        r = subprocess.run(cmd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=1500)
    i = c = o = rs = 0; tools = {}; err = None; turns = 0; deleg = 0
    for line in r.stdout.splitlines():
        try: ev = json.loads(line)
        except json.JSONDecodeError: continue
        if ev.get("type") == "turn.completed":
            u = ev.get("usage", {}); turns += 1
            i += u.get("input_tokens", 0); c += u.get("cached_input_tokens", 0); o += u.get("output_tokens", 0); rs += u.get("reasoning_output_tokens", 0)
        if ev.get("type") in ("error", "turn.failed"): err = line[:300]
        it = ev.get("item") or {}
        if ev.get("type") == "item.completed" and it.get("type") not in ("agent_message", "reasoning"):
            tools[it.get("type")] = tools.get(it.get("type"), 0) + 1
            if DELEGATE.search(str(it.get("command", ""))): deleg += 1
    return dict(in_tok=i, cached_tok=c, cache_write_tok=0, out_tok=o, reasoning_tok=rs, cost_usd=None, cost_kind="proxy (list price x tokens)",
                turns=turns, tool_calls=tools, is_error=bool(err) or r.returncode != 0,
                error=err or (r.stderr.strip()[-300:] if r.returncode else None), error_type="infrastructure" if err or r.returncode else None, delegate_calls=deleg), r.stdout


def run_grok(mid, eff, prompt, w):
    spent = grok_spend(CACHE)
    if spent >= GROK_BUDGET_USD:
        raise SpendLimit(f"refused: Grok agentic spend ${spent:.2f} >= ${GROK_BUDGET_USD}")
    cmd = [GROK, "-p", prompt, "-m", mid, "--reasoning-effort", eff, "--cwd", w] + GROK_FLAGS
    r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=w, timeout=1500)
    try:
        d = json.loads(r.stdout)
        if not isinstance(d, dict): raise ValueError("expected a JSON object")
    except (ValueError, TypeError):
        return dict(is_error=True, error=(r.stderr or r.stdout or "missing Grok JSON")[-300:],
                    error_type="infrastructure", cost_usd=None), r.stdout
    u = d.get("usage") or {}
    err = bool(d.get("is_error") or d.get("error") or r.returncode)
    return dict(in_tok=u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0),
                cached_tok=u.get("cache_read_input_tokens", 0), cache_write_tok=u.get("cache_creation_input_tokens", 0),
                out_tok=u.get("output_tokens", 0), reasoning_tok=u.get("reasoning_tokens", 0),
                cost_usd=d.get("total_cost_usd"), cost_kind="measured (CLI total_cost_usd)",
                turns=d.get("num_turns"), tool_calls=None, delegate_calls=None, is_error=err,
                error=str(r.stderr or d.get("error") or d.get("text") or "Grok error")[-300:] if err else None,
                error_type="infrastructure" if r.returncode else "model" if err else None), r.stdout


def pytest(w, *args, source=None, collect=False):
    output = os.path.join(w, "receipt.json")
    runner = os.path.join(ROOT, "bench", "agentic", "pytest_runner.py")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTEST_", "PYTHON"))}
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    cmd = ["python3", "-B", "-I", runner, source or w, output, "-q", "-p", "no:cacheprovider", "--rootdir", w, "-c", "/dev/null", "--noconftest"]
    try:
        r = subprocess.run(cmd + (["--collect-only"] if collect else []) + list(args), cwd=w, env=env, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return dict(ok=False, passed=0, failed=0, tail="pytest timeout", collected_ids=[], reports=[], deselected=[])
    receipt = json.load(open(output)) if os.path.exists(output) else dict(collected_ids=[], reports=[], deselected=[])
    reports = receipt["reports"]; ids = receipt["collected_ids"]
    passed = [i for i in ids if any(p["id"] == i and p["when"] == "call" and p["outcome"] == "passed" for p in reports)
              and {p["when"] for p in reports if p["id"] == i} == {"setup", "call", "teardown"}
              and all(p["outcome"] == "passed" and not p["xfail"] for p in reports if p["id"] == i)]
    good = bool(ids) and not receipt["deselected"] and (collect or len(passed) == len(ids))
    return dict(ok=r.returncode == 0 and good, passed=len(passed), failed=sum(p["outcome"] == "failed" for p in reports),
                tail=((r.stdout.strip().splitlines() or [r.stderr.strip()])[-1])[:200], **receipt)


def hidden_pytest(w, reference, hidden):
    with tempfile.TemporaryDirectory(prefix="mrb-hidden-") as clean:
        shutil.copyfile(hidden, os.path.join(clean, "test_hidden.py"))
        expected = pytest(clean, "test_hidden.py", source=reference, collect=True)
        result = pytest(clean, "test_hidden.py", source=w)
    result["expected_ids"] = expected["collected_ids"]
    result["expected_collection"] = dict(ok=expected["ok"], tail=expected["tail"])
    result["ok"] = result["ok"] and expected["ok"] and result["collected_ids"] == result["expected_ids"]
    return result


def visible_pytest(w):
    # Run the delivered visible tests, including added tests, without loading their hooks/config.
    with tempfile.TemporaryDirectory(prefix="mrb-visible-") as clean:
        shutil.copytree(os.path.join(w, "tests"), os.path.join(clean, "tests"))
        return pytest(clean, "tests", source=w)


def one(config, task, rep, lanes, regrade=False):
    if not regrade and os.path.exists(os.path.join(CACHE, key_for(config, task, rep, legacy=True) + ".json")):
        return "cached (grader_version=1)"
    key = key_for(config, task, rep); fp = os.path.join(CACHE, key + ".json")
    status, prior = cache_state(fp)
    if status: return status
    cli, mid, eff = CONFIGS[config]
    t = os.path.join(TASKS, task); prompt = open(os.path.join(t, "TASK.md")).read()
    w = tempfile.mkdtemp(prefix="mrb-agent-")
    res = {}; raw = ""; wall = 0.0; tampered = []; own = False; diff = []
    vis = hid = dict(ok=False, passed=0, failed=0, tail="model call failed")
    try:
        shutil.copytree(os.path.join(t, "repo"), w, dirs_exist_ok=True)
        g = lambda *a: subprocess.run(["git", "-C", w, *a], capture_output=True, text=True)
        g("init", "-q"); g("add", "-f", "-A"); g("-c", "user.name=bench", "-c", "user.email=bench@localhost", "commit", "-qm", "base")
        base = g("rev-parse", "HEAD").stdout.strip()
        orig_tests = {f: open(os.path.join(w, "tests", f), "rb").read() for f in os.listdir(os.path.join(w, "tests"))}
        t0 = time.monotonic()
        try:
            res, raw = {"claude": run_claude, "codex": run_codex, "grok": run_grok}[cli](mid, eff, prompt, w)
        except (subprocess.TimeoutExpired, OSError) as exc:
            res, raw = failure(exc, time.monotonic() - t0)
        wall = time.monotonic() - t0
        res.pop("wall_s", None)
        tampered = [f for f, b in orig_tests.items() if not os.path.exists(os.path.join(w, "tests", f)) or open(os.path.join(w, "tests", f), "rb").read() != b]
        want = re.findall(r"tests/(test_\w+\.py)", prompt)
        own = all(os.path.exists(os.path.join(w, "tests", f)) for f in want)
        if not res.get("is_error"):
            vis = visible_pytest(w)
            hid = hidden_pytest(w, os.path.join(t, "solution"), os.path.join(t, "hidden", "test_hidden.py"))
    except SpendLimit as exc:
        return str(exc)
    finally:
        g("add", "-f", "-A")
        diff = g("diff", "--cached", "--stat", base).stdout.strip().splitlines()
        patch = g("diff", "--cached", "--binary", base).stdout
        os.makedirs(PATCHES, exist_ok=True)
        with open(os.path.join(PATCHES, key + ".patch"), "w") as f: f.write(patch)
        shutil.rmtree(w, ignore_errors=True)
    if res.get("error"):
        res["error"] = res["error"].replace(w, "<cwd>").replace(os.path.expanduser("~"), "~")
    entry = dict(key=key, ts=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), track="agentic", grader_version=grader_version(task), config=config, cli=cli,
                 cli_version=cli_version(cli), model=mid, effort=eff, task=task, repeat=rep, lanes=lanes, wall_s=wall, **res,
                 visible_pass=vis["ok"], visible=vis, hidden_pass=hid["ok"], hidden=hid, task_complete=vis["ok"] and hid["ok"], own_tests=own, tests_tampered=tampered,
                 diff_stat=diff[-1] if diff else "", patch=os.path.relpath(os.path.join(PATCHES, key + ".patch"), ROOT))
    entry["retry_count"] = (prior.get("retry_count", 0) + 1) if prior else 0
    if cli == "codex": entry["codex_home"] = "isolated"
    if prior: entry["previous_attempt"] = prior
    if stop_message(entry): entry["quota_error"] = True
    os.makedirs(CACHE, exist_ok=True); os.makedirs(RAW, exist_ok=True)
    json.dump(entry, open(fp + ".tmp", "w"), indent=1); os.replace(fp + ".tmp", fp)
    open(os.path.join(RAW, "agentic-" + key + ".out"), "w").write(raw)
    return stop_message(entry) or f"{'ERR ' if entry['is_error'] else ''}{wall:.0f}s hidden={hid['passed']}/{hid['passed'] + hid['failed']} visible={vis['ok']}"


def export(output=None, keys=None):
    output = output or OUT
    rows = [json.load(open(os.path.join(CACHE, f))) for f in sorted(os.listdir(CACHE)) if f.endswith(".json")] if os.path.isdir(CACHE) else []
    if keys is not None: rows = [r for r in rows if r["key"] in keys]
    else:
        # Default historical exports must never absorb the separate Grok experiment.
        rows = [r for r in rows if (r.get("cli") == "grok") == (os.path.abspath(output) == os.path.abspath(GROK_OUT))]
    rows.sort(key=lambda r: (r.get("grader_version", 1), r.get("ts", ""), r.get("key", "")))
    latest = {(r["config"], r["task"], r["repeat"]): r for r in rows}
    rows = [latest[k] for k in sorted(latest)]
    with open(output, "w") as f:
        for r in rows: f.write(json.dumps(r, sort_keys=True) + "\n")
    print(f"{len(rows)} agentic runs -> {os.path.relpath(output, ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs"); ap.add_argument("--tasks", default="all"); ap.add_argument("--repeats", default="1-3")
    ap.add_argument("--lanes", type=int, default=4); ap.add_argument("--export", action="store_true")
    ap.add_argument("--regrade", action="store_true", help="allow new model calls for legacy verdicts under the current grader")
    ap.add_argument("--output", help="results file; Grok runs default to their separate preregistered file")
    a = ap.parse_args()
    if a.export:
        return export(a.output)
    cfgs = a.configs.split(","); tasks = TASK_IDS if a.tasks == "all" else a.tasks.split(","); reps = parse_reps(a.repeats)
    assert 1 <= a.lanes <= 4
    is_grok = any(CONFIGS[c][0] == "grok" for c in cfgs)
    if is_grok:
        assert all(CONFIGS[c][0] == "grok" for c in cfgs), "run Grok separately from historical lanes"
        jobs = [(cfg, task, rep) for rep in reps for task in tasks for cfg in cfgs]
        def job(args):
            cfg, task, rep = args
            msg = one(cfg, task, rep, a.lanes, regrade=a.regrade)
            print(f"[agentic] {cfg} {task} r{rep}: {msg}", flush=True)
        with ThreadPoolExecutor(a.lanes) as ex:
            list(ex.map(job, jobs))
        return export(a.output or GROK_OUT, {key_for(*args) for args in jobs})

    def lane(cfg):
        for rep in reps:
            for task in tasks:
                msg = one(cfg, task, rep, a.lanes, regrade=a.regrade); print(f"[agentic] {cfg} {task} r{rep}: {msg}", flush=True)
                if msg.startswith(("refused", "stopped")): return
    with ThreadPoolExecutor(a.lanes) as ex:
        list(ex.map(lane, cfgs))
    export(a.output)


if __name__ == "__main__":
    main()
