"""Agentic track: each config edits a small repo with tools on; hidden tests are copied in only after the agent exits.

python3 -m bench.agentic.run --configs haiku-low,sonnet-medium,luna-low,sol61-medium --tasks all --repeats 1-3 --lanes 4
python3 -m bench.agentic.run --export        # rebuild results/2026-10-22b-agentic.jsonl from cache, no model calls

Cache entry: cache/agentic/<sha256>.json. The key covers config, CLI version, harness flags, the task prompt, a hash of the
task's starting repo and hidden tests, and the repeat number."""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor

from bench.run import CONFIGS, CLAUDE, CODEX, CLAUDE_BUDGET_USD, claude_spend, cli_version, parse_reps

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TASKS = os.path.join(ROOT, "bench", "agentic", "tasks")
CACHE = os.path.join(ROOT, "cache", "agentic")
RAW = os.path.join(ROOT, "cache", "raw")
OUT = os.path.join(ROOT, "results", "2026-10-22b-agentic.jsonl")
TASK_IDS = sorted(d for d in os.listdir(TASKS) if d.startswith("t"))

# Matched harnesses: shell + file edit tools on both sides, no user/project settings, no MCP servers.
CLAUDE_FLAGS = ["--output-format", "stream-json", "--verbose", "--no-session-persistence", "--setting-sources", "",
                "--strict-mcp-config", "--tools", "Bash,Read,Edit,Write,Glob,Grep", "--permission-mode", "bypassPermissions"]
CODEX_FLAGS = ["--ignore-user-config", "-c", "skills.include_instructions=false", "-c", "service_tier=default",
               "--json", "--ephemeral", "--skip-git-repo-check", "-s", "workspace-write"]
DELEGATE = re.compile(r"\b(devin|kimi|grok|delegate|codex exec|claude -p)\b")


def tree_hash(*dirs):
    h = hashlib.sha256()
    for d in dirs:
        for base, _, files in sorted(os.walk(d)):
            for f in sorted(files):
                p = os.path.join(base, f); h.update(os.path.relpath(p, d).encode()); h.update(open(p, "rb").read())
    return h.hexdigest()


def key_for(config, task, rep):
    cli, mid, eff = CONFIGS[config]; t = os.path.join(TASKS, task)
    blob = json.dumps({"track": "agentic", "config": config, "model": mid, "effort": eff, "cli": cli, "cli_version": cli_version(cli),
                       "flags": CLAUDE_FLAGS if cli == "claude" else CODEX_FLAGS, "prompt": open(os.path.join(t, "TASK.md")).read(),
                       "task": task, "task_tree": tree_hash(os.path.join(t, "repo"), os.path.join(t, "hidden")), "repeat": rep}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def run_claude(mid, eff, prompt, w):
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
                turns=res.get("num_turns"), tool_calls=tools, is_error=bool(res.get("is_error")) or not res,
                error=None if res and not res.get("is_error") else (res.get("result") or r.stderr)[-300:], delegate_calls=0), r.stdout


def run_codex(mid, eff, prompt, w):
    cmd = [CODEX, "exec", "-m", mid, "-c", f"model_reasoning_effort={eff}"] + CODEX_FLAGS + ["-C", w, prompt]
    r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=1500)
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
                error=err or (r.stderr.strip()[-300:] if r.returncode else None), delegate_calls=deleg), r.stdout


def pytest(w, *args):
    r = subprocess.run(["python3", "-m", "pytest", "-q", "-p", "no:cacheprovider", *args], cwd=w, capture_output=True, text=True, timeout=300)
    tail = (r.stdout.strip().splitlines() or [""])[-1]
    n = lambda word: int(m.group(1)) if (m := re.search(rf"(\d+) {word}", tail)) else 0
    return dict(ok=r.returncode == 0, passed=n("passed"), failed=n("failed") + n("error"), tail=tail[:200])


def one(config, task, rep, lanes):
    key = key_for(config, task, rep); fp = os.path.join(CACHE, key + ".json")
    if os.path.exists(fp):
        return "cached"
    cli, mid, eff = CONFIGS[config]
    if cli == "claude":
        spent = claude_spend() + agentic_spend()
        if spent >= CLAUDE_BUDGET_USD:
            return f"refused: Claude spend ${spent:.2f} >= ${CLAUDE_BUDGET_USD}"
    t = os.path.join(TASKS, task); prompt = open(os.path.join(t, "TASK.md")).read()
    w = tempfile.mkdtemp(prefix="mrb-agent-")
    try:
        shutil.copytree(os.path.join(t, "repo"), w, dirs_exist_ok=True)
        g = lambda *a: subprocess.run(["git", "-C", w, *a], capture_output=True, text=True)
        g("init", "-q"); g("add", "-A"); g("-c", "user.name=bench", "-c", "user.email=bench@localhost", "commit", "-qm", "base")
        orig_tests = {f: open(os.path.join(w, "tests", f), "rb").read() for f in os.listdir(os.path.join(w, "tests"))}
        t0 = time.monotonic()
        res, raw = (run_claude if cli == "claude" else run_codex)(mid, eff, prompt, w)
        wall = time.monotonic() - t0
        tampered = [f for f, b in orig_tests.items() if not os.path.exists(os.path.join(w, "tests", f)) or open(os.path.join(w, "tests", f), "rb").read() != b]
        want = re.findall(r"tests/(test_\w+\.py)", prompt)
        own = all(os.path.exists(os.path.join(w, "tests", f)) for f in want)
        vis = pytest(w)
        g("add", "-A"); diff = g("diff", "--cached", "--stat", "HEAD").stdout.strip().splitlines()
        hid_name = "test_zz_hidden_" + key[:8] + ".py"
        shutil.copy(os.path.join(t, "hidden", "test_hidden.py"), os.path.join(w, "tests", hid_name))
        hid = pytest(w, os.path.join("tests", hid_name))
    finally:
        shutil.rmtree(w, ignore_errors=True)
    if res.get("error"):
        res["error"] = res["error"].replace(w, "<cwd>").replace(os.path.expanduser("~"), "~")
    entry = dict(key=key, ts=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), track="agentic", config=config, cli=cli,
                 cli_version=cli_version(cli), model=mid, effort=eff, task=task, repeat=rep, lanes=lanes, wall_s=wall, **res,
                 visible_pass=vis["ok"], visible=vis, hidden_pass=hid["ok"], hidden=hid, own_tests=own, tests_tampered=tampered,
                 diff_stat=diff[-1] if diff else "")
    os.makedirs(CACHE, exist_ok=True); os.makedirs(RAW, exist_ok=True)
    json.dump(entry, open(fp + ".tmp", "w"), indent=1); os.replace(fp + ".tmp", fp)
    open(os.path.join(RAW, "agentic-" + key + ".out"), "w").write(raw)
    return f"{'ERR ' if entry['is_error'] else ''}{wall:.0f}s hidden={hid['passed']}/{hid['passed'] + hid['failed']} visible={vis['ok']}"


def agentic_spend():
    if not os.path.isdir(CACHE): return 0.0
    return sum((json.load(open(os.path.join(CACHE, f))).get("cost_usd") or 0.0) for f in os.listdir(CACHE) if f.endswith(".json"))


def export():
    rows = [json.load(open(os.path.join(CACHE, f))) for f in sorted(os.listdir(CACHE)) if f.endswith(".json")] if os.path.isdir(CACHE) else []
    rows.sort(key=lambda r: (r["config"], r["task"], r["repeat"]))
    with open(OUT, "w") as f:
        for r in rows: f.write(json.dumps(r, sort_keys=True) + "\n")
    print(f"{len(rows)} agentic runs -> {os.path.relpath(OUT, ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs"); ap.add_argument("--tasks", default="all"); ap.add_argument("--repeats", default="1-3")
    ap.add_argument("--lanes", type=int, default=4); ap.add_argument("--export", action="store_true")
    a = ap.parse_args()
    if a.export:
        return export()
    cfgs = a.configs.split(","); tasks = TASK_IDS if a.tasks == "all" else a.tasks.split(","); reps = parse_reps(a.repeats)
    assert a.lanes <= 4

    def lane(cfg):
        for rep in reps:
            for task in tasks:
                msg = one(cfg, task, rep, a.lanes); print(f"[agentic] {cfg} {task} r{rep}: {msg}", flush=True)
                if msg.startswith("refused"): return
    with ThreadPoolExecutor(a.lanes) as ex:
        list(ex.map(lane, cfgs))
    export()


if __name__ == "__main__":
    main()
