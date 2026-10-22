"""How low can the Codex CLI's input-token floor go, and does a stripped Codex model beat Haiku on the pilot problems?

Trim levels are cumulative. Each adds Codex config knobs that exist in CLI 0.163.0 (`codex features list`, `codex exec --help`):
  base     the function-track harness (bench/run.py CODEX_FLAGS)
  nodoc    + project_doc_max_bytes=0                      (instruction files such as AGENTS.md)
  noctx    + include_environment_context=false, include_permissions_instructions=false
  nofeat   + every enabled feature that adds a tool or tool instructions turned off, web search off
  mininst  + model_instructions_file = a one-line system prompt  (replaces Codex's base instructions: no longer stock Codex)
  noshell  + shell and exec tools off (function track only: the model needs no tools there)

python3 -m bench.trim_probe --step floor     # 1 call per (model, level) on fizzbuzz: token floor per level
python3 -m bench.trim_probe --step pair      # 3 rounds x 3 pilot problems: luna/terra at chosen levels, and haiku-low
Results: results/2026-10-22b-trim.jsonl. Every call is cached in cache/trim/ under a key of config, CLI version, flags, prompt."""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, tempfile, time
from concurrent.futures import ThreadPoolExecutor

from bench.run import CLAUDE, CODEX, CLAUDE_FLAGS, CODEX_FLAGS, cli_version, call_claude

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT = os.path.join(ROOT, "bench", "pilot")
CACHE = os.path.join(ROOT, "cache", "trim")
OUT = os.path.join(ROOT, "results", "2026-10-22b-trim.jsonl")
PROBLEMS = ["fizzbuzz", "course2", "candy"]
MIN_INST = os.path.join(PILOT, "min_instructions.txt")
# The cache key holds the placeholder <MIN_INST>, not the file, so a changed file must not silently reuse cached calls.
MIN_INST_SHA = "47eee3a1a40de1c1ea690e4ebb6abf00241430c3fba42e5a01b9deebdab26df3"

TOOL_FEATURES = ["multi_agent", "apps", "browser_use", "browser_use_external", "computer_use", "image_generation", "memories", "plugins",
                 "goals", "view_image", "tool_suggest", "sleep_tool", "skill_search", "in_app_browser", "hooks", "remote_plugin",
                 "skill_mcp_dependency_install", "workspace_dependencies", "worktrees"]
LEVELS = {"base": []}
LEVELS["nodoc"] = LEVELS["base"] + ["-c", "project_doc_max_bytes=0"]
LEVELS["noctx"] = LEVELS["nodoc"] + ["-c", "include_environment_context=false", "-c", "include_permissions_instructions=false"]
LEVELS["nofeat"] = LEVELS["noctx"] + [x for f in TOOL_FEATURES for x in ("--disable", f)] + ["-c", 'web_search="disabled"']
LEVELS["mininst"] = LEVELS["nofeat"] + ["-c", "model_instructions_file=<MIN_INST>"]
LEVELS["noshell"] = LEVELS["mininst"] + [x for f in ("shell_tool", "unified_exec", "unified_exec_tty", "shell_snapshot") for x in ("--disable", f)]
MODELS = {"luna": "gpt-6-luna", "terra": "gpt-5.6-terra"}


def prompt(prob):
    t = open(os.path.join(PILOT, "prompt_template.txt")).read()
    return t.format(statement=open(f"{PILOT}/problems/{prob}.md").read().strip(), signature=open(f"{PILOT}/problems/{prob}.sig").read().strip())


def flags(level):
    return CODEX_FLAGS + [x.replace("<MIN_INST>", json.dumps(MIN_INST)) for x in LEVELS[level]]


def codex(mid, level, p):
    cwd = tempfile.mkdtemp(prefix="mrb-"); last = os.path.join(cwd, "last.txt")
    cmd = [CODEX, "exec", "-m", mid, "-c", "model_reasoning_effort=low"] + flags(level) + ["-C", cwd, "-o", last, p]
    t0 = time.monotonic(); r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=600); wall = time.monotonic() - t0
    u = {}; err = None; tools = 0
    for line in r.stdout.splitlines():
        try: ev = json.loads(line)
        except json.JSONDecodeError: continue
        if ev.get("type") == "turn.completed": u = ev.get("usage", {})
        if ev.get("type") in ("error", "turn.failed"): err = line[:300]
        it = ev.get("item") or {}
        if ev.get("type") == "item.completed" and it.get("type") not in ("agent_message", "reasoning"): tools += 1
    text = open(last).read() if os.path.exists(last) else ""
    shutil.rmtree(cwd, ignore_errors=True)
    if r.returncode and not err: err = r.stderr.strip()[-300:]
    if err: err = err.replace(cwd, "<cwd>").replace(os.path.expanduser("~"), "~")
    return dict(wall_s=wall, text=text, is_error=bool(err), error=err, in_tok=u.get("input_tokens", 0), cached_tok=u.get("cached_input_tokens", 0),
                out_tok=u.get("output_tokens", 0), reasoning_tok=u.get("reasoning_output_tokens", 0), cost_usd=None, tool_items=tools)


def check(prob, text):
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text or "", re.S); code = blocks[-1] if blocks else (text or "")
    d = tempfile.mkdtemp(prefix="mrb-chk-"); cand = os.path.join(d, "cand.py"); open(cand, "w").write(code)
    try:
        ck = subprocess.run(["python3", "-I", os.path.join(PILOT, "checker.py"), prob, cand], capture_output=True, text=True, timeout=300)
        v = json.loads(ck.stdout.strip().splitlines()[-1]) if ck.stdout.strip() else {"pass": False}
    except Exception as e:
        v = {"pass": False, "detail": repr(e)[:200]}
    shutil.rmtree(d, ignore_errors=True)
    return bool(v.get("pass"))


def one(config, prob, rnd, step):
    fam, level = config.split("/") if "/" in config else (config, None)
    p = prompt(prob); cli = "claude" if fam == "haiku" else "codex"
    fl = CLAUDE_FLAGS if cli == "claude" else CODEX_FLAGS + LEVELS[level]  # placeholder path keeps the key portable
    key = hashlib.sha256(json.dumps({"track": "trim", "config": config, "cli_version": cli_version(cli), "flags": fl, "prompt": p, "round": rnd},
                                    sort_keys=True).encode()).hexdigest()
    fp = os.path.join(CACHE, key + ".json")
    if os.path.exists(fp): return json.load(open(fp))
    if hashlib.sha256(open(MIN_INST, "rb").read()).hexdigest() != MIN_INST_SHA:
        raise SystemExit("min_instructions.txt changed: add its hash to the cache key before making new calls")
    if cli == "claude":
        cwd = tempfile.mkdtemp(prefix="mrb-")
        try: res, _ = call_claude("claude-haiku-5-5", "low", p, cwd)
        finally: shutil.rmtree(cwd, ignore_errors=True)
    else:
        res = codex(MODELS[fam], level, p)
    e = dict(key=key, ts=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), step=step, config=config, cli=cli,
             cli_version=cli_version(cli), model="claude-haiku-5-5" if cli == "claude" else MODELS[fam], effort="low", level=level,
             problem=prob, round=rnd, **{k: v for k, v in res.items() if k != "text"}, passed=check(prob, res.get("text")),
             text=res.get("text"))
    os.makedirs(CACHE, exist_ok=True); json.dump(e, open(fp + ".tmp", "w"), indent=1); os.replace(fp + ".tmp", fp)
    return e


def export():
    rows = [json.load(open(os.path.join(CACHE, f))) for f in sorted(os.listdir(CACHE)) if f.endswith(".json")] if os.path.isdir(CACHE) else []
    rows.sort(key=lambda r: (r["step"], r["config"], r["problem"], r["round"]))
    with open(OUT, "w") as f:
        for r in rows: f.write(json.dumps({k: v for k, v in r.items() if k != "text"}, sort_keys=True) + "\n")
    print(f"{len(rows)} trim rows -> {os.path.relpath(OUT, ROOT)}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--step", choices=["floor", "pair", "export"], required=True)
    ap.add_argument("--levels", default="base,nofeat,mininst", help="pair step: Codex levels to run 3x3")
    a = ap.parse_args()
    if a.step == "export": return export()
    if a.step == "floor":
        jobs = [[(f"{m}/{lv}", "fizzbuzz", 1) for lv in LEVELS] for m in MODELS]
    else:
        lv = a.levels.split(",")
        jobs = [[(f"{m}/{l}", p, r) for l in lv for r in (1, 2, 3) for p in PROBLEMS] for m in MODELS] + [[("haiku", p, r) for r in (1, 2, 3) for p in PROBLEMS]]

    def lane(js):
        for c, p, r in js:
            e = one(c, p, r, a.step)
            print(f"[trim {a.step}] {c} {p} r{r}: in={e['in_tok']} cached={e['cached_tok']} out={e['out_tok']} tools={e.get('tool_items', e.get('turns'))} "
                  f"pass={e['passed']} {e['wall_s']:.1f}s{' ERR ' + str(e['error'])[:160] if e['is_error'] else ''}", flush=True)
    with ThreadPoolExecutor(min(4, len(jobs))) as ex: list(ex.map(lane, jobs))
    export()


if __name__ == "__main__":
    main()
