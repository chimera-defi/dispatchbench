"""Agentic e2e: python3 e2e.py <pipeline A|B|C> <round>. Appends a row to ../results_e2e.jsonl."""
import json, os, shutil, subprocess, sys, time, datetime
D = os.path.dirname(os.path.abspath(__file__)); CLAUDE = os.environ.get("CLAUDE_BIN", "claude"); CODEX = os.environ.get("CODEX_BIN", "codex")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(D))))
from bench.codex_env import isolated_codex_env
PRICES = {"gpt-6.1-sol": (2.0, 0.10, 10.0), "gpt-6-luna": (0.10, 0.01, 0.50)}
TRIM = ["-c", "skills.include_instructions=false", "--disable", "multi_agent", "-c", "project_doc_max_bytes=0"]
PIPE = {"A": ("codex", "gpt-6.1-sol"), "B": ("codex", "gpt-6-luna"), "C": ("claude", "claude-sonnet-5-5")}
pl, rnd = sys.argv[1], sys.argv[2]; kind, model = PIPE[pl]
w = f"{D}/work/{pl}-r{rnd}"; shutil.rmtree(w, ignore_errors=True); shutil.copytree(f"{D}/template", w)
g = lambda *a: subprocess.run(["git", "-C", w, *a], capture_output=True, text=True)
g("init", "-q"); g("add", "-A"); g("-c", "user.name=bench", "-c", "user.email=bench@localhost", "commit", "-qm", "base")
task = open(f"{D}/TASK.md").read()
t = time.monotonic()
if kind == "codex":
    cmd = [CODEX, "exec", "--ignore-user-config", "-m", model, "-c", "model_reasoning_effort=low", "-c", "service_tier=default", "--json", "--ephemeral",
           "--skip-git-repo-check", "-s", "workspace-write", "-C", w] + TRIM + [task]
    with isolated_codex_env() as env:
        r = subprocess.run(cmd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=1200)
    open(f"{w}.builder.jsonl", "w").write(r.stdout)
    i = c = o = 0; tools = 0
    for line in r.stdout.splitlines():
        try: ev = json.loads(line)
        except Exception: continue
        if ev.get("type") == "turn.completed":
            u = ev["usage"]; i += u.get("input_tokens", 0); c += u.get("cached_input_tokens", 0); o += u.get("output_tokens", 0)
        it = ev.get("item") or {}
        if ev.get("type") == "item.completed" and it.get("type") not in ("agent_message", "reasoning"): tools += 1
    pi, pc, po = PRICES[model]; bcost = ((i - c) * pi + c * pc + o * po) / 1e6; bkind = "proxy(api-list, default tier)"
else:
    cmd = [CLAUDE, "-p", task, "--model", model, "--effort", "low", "--output-format", "json", "--no-session-persistence",
           "--permission-mode", "bypassPermissions"]
    r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=1200, cwd=w)
    d = json.loads(r.stdout); u = d.get("usage", {}); open(f"{w}.builder.json", "w").write(r.stdout)
    i = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
    c = u.get("cache_read_input_tokens", 0); o = u.get("output_tokens", 0); tools = max(0, (d.get("num_turns") or 1) - 1)
    bcost = d.get("total_cost_usd"); bkind = "list (CLI)"
bwall = time.monotonic() - t
vis = subprocess.run(["python3", "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=w, capture_output=True, text=True)
shutil.copy(f"{D}/hidden_test.py", f"{w}/tests/hidden_test.py")
hid = subprocess.run(["python3", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/hidden_test.py"], cwd=w, capture_output=True, text=True)
os.remove(f"{w}/tests/hidden_test.py")
own = os.path.exists(f"{w}/tests/test_discount.py")
g("add", "-A"); diff = g("diff", "--cached", "HEAD").stdout
review = None
if kind == "codex":  # pipeline A/B: Haiku low reviews the diff (single shot, tools off)
    rp = (f"You are reviewing a code change against its spec. Spec:\n\n{task}\n\nDiff:\n```diff\n{diff}\n```\n\n"
          "List concrete spec violations or bugs only (no style). Reply with only JSON: "
          '{"verdict": "ok" | "issues", "issues": ["..."]}')
    t2 = time.monotonic()
    rr = subprocess.run([CLAUDE, "-p", rp, "--model", "claude-haiku-5-5", "--effort", "low", "--output-format", "json", "--tools", "",
                         "--no-session-persistence", "--setting-sources", ""], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=600)
    rd = json.loads(rr.stdout); ru = rd.get("usage", {})
    txt = rd.get("result", ""); s0, s1 = txt.find("{"), txt.rfind("}")
    try: parsed = json.loads(txt[s0:s1 + 1])
    except Exception: parsed = {"verdict": "unparsed", "raw": txt[:500]}
    review = dict(wall_s=time.monotonic() - t2, cost_usd=rd.get("total_cost_usd"),
                  in_tok=ru.get("input_tokens", 0) + ru.get("cache_creation_input_tokens", 0) + ru.get("cache_read_input_tokens", 0),
                  out_tok=ru.get("output_tokens", 0), **parsed)
row = dict(ts=datetime.datetime.now(datetime.timezone.utc).isoformat(), pipeline=pl, round=int(rnd), builder=model, builder_kind=kind,
           builder_wall_s=bwall, builder_in=i, builder_cached=c, builder_out=o, builder_cost_usd=bcost, builder_cost_kind=bkind, tool_items=tools,
           builder_rc=r.returncode, visible_pass=vis.returncode == 0, visible_tail=vis.stdout.strip().splitlines()[-1:] ,
           hidden_pass=hid.returncode == 0, hidden_tail=hid.stdout.strip().splitlines()[-3:], own_tests=own,
           diff_lines=len(diff.splitlines()), review=review)
open(f"{D}/../results_e2e.jsonl", "a").write(json.dumps(row) + "\n"); print(json.dumps(row)[:600])
