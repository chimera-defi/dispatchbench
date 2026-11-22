"""Turn local Inkling 2 Mini runner output (pNN.result.json, results/inkling/runner.py) into DispatchBench rows and a report.
Offline, no model calls. Usage: python3 -m bench.inkling_export <primary_run_dir> [<retry_root_dir with sec_medium_16384, sec_low_16384, sec_default_24576>]"""
import datetime, hashlib, json, os, shutil, sys
from bench import run as R

RES = os.path.join(R.ROOT, "results")
RUNS = {"primary": ("inkling2mini-default", 12288, "default", "2026-11-22-inkling-function.jsonl"),
        "medium": ("inkling2mini-medium16k", 16384, "medium", None), "low": ("inkling2mini-low16k", 16384, "low", None), "def24": ("inkling2mini-default24k", 24576, "default", None)}
STAGE_DIRS = {"medium": "sec_medium_16384", "low": "sec_low_16384", "def24": "sec_default_24576"}
RETRY_OUT = "2026-11-22-inkling-retry-function.jsonl"


def rows_for(kind, d):
    config, cap, effort, out = RUNS[kind]; rows = []
    flags = ["llama-server b12600", "--jinja", "-c", "32768", "-t", "6", "-tb", "6", "-np", "1"] + ([f"reasoning_effort={effort}"] if effort != "default" else []) + ["--temp", "1.0", "--top-k", "50", "--top-p", "1.0", "--min-p", "0", f"max_tokens={cap}"]
    rawdir = os.path.join(RES, "inkling", "raw-" + kind); os.makedirs(rawdir, exist_ok=True)
    for pid in sorted(f[:-12] for f in os.listdir(d) if f.endswith(".result.json") and f.startswith("p")):
        r = json.load(open(f"{d}/{pid}.result.json")); v = r.get("verdict") or {}; prompt = R.prompt_for(pid)
        key = hashlib.sha256(json.dumps({"config": config, "flags": flags, "prompt": prompt, "problem": pid, "repeat": 1}, sort_keys=True).encode()).hexdigest()
        rows.append({"ts": datetime.datetime.fromtimestamp(os.path.getmtime(f"{d}/{pid}.result.json"), datetime.timezone.utc).isoformat(timespec="seconds"),
            "phase": "exploratory", "config": config, "cli": "llama.cpp", "cli_version": "b12600", "model": "Inkling-2-Mini-IQ4_NL.gguf", "effort": effort,
            "problem": pid, "repeat": 1, "lanes": 1, "wall_s": r["wall_s"], "api_duration_ms": None, "in_tok": r.get("prompt_tok"), "cached_tok": 0, "cache_write_tok": 0,
            "out_tok": r.get("out_tok"), "reasoning_tok": None, "cost_usd": 0.0, "cost_kind": "free local CPU model (i7-8700, no list price)", "tool_items": None,
            "is_error": bool(r.get("error")), "error": r.get("error"), "key": key, "prompt_sha": hashlib.sha256(prompt.encode()).hexdigest()[:12], "codex_home": None,
            "rung": R.problems.load(pid).RUNG, "outcome": v.get("outcome"), "passed": v.get("outcome") == "pass", "grade_detail": v.get("detail"),
            "code_lines": r.get("code_lines"), "finish_reason": r.get("finish_reason"), "max_tokens": cap, "gen_tok_per_s": r.get("gen_tps"),
            "prompt_tok_per_s": r.get("prompt_tps"), "peak_rss_kib": (r.get("rss_end") or {}).get("VmHWM") or r.get("peak_rss_kib"), "loadavg_start": r.get("loadavg_start")})
        shutil.copy(f"{d}/{pid}.raw.txt", f"{rawdir}/{pid}.raw.txt")
    if out:
        with open(os.path.join(RES, out), "w") as f:
            for x in rows: f.write(json.dumps(x) + "\n")
    return rows


def hms(s): return f"{int(s//3600)}h{int(s%3600//60):02d}m"


def table(rows):
    t = ["| problem | rung | outcome | wall | out tok | gen tok/s | server peak RSS so far GiB (VmHWM, cumulative, includes mapped weights) | load avg |", "|---|---|---|---|---|---|---|---|"]
    for x in rows:
        t.append(f"| {x['problem']} | L{x['rung']} | {'pass' if x['passed'] else x['outcome'] + ' (' + str(x['finish_reason']) + ')'} | {x['wall_s']/60:.1f} min | {x['out_tok']} | {x['gen_tok_per_s']:.1f} | {(x['peak_rss_kib'] or 0)/1048576:.1f} | {x['loadavg_start'][0]} |")
    return "\n".join(t)


def main(prim, retry_root=None):
    a = rows_for("primary", prim)
    pa = sum(x["passed"] for x in a); ta = sum(x["wall_s"] for x in a)
    md = ["# Inkling 2 Mini on DispatchBench p01-p15 (2026-11-22)", "",
          "Free local CPU model (i7-8700 6C/12T, ~63 GiB RAM, no GPU), llama.cpp b12600, IQ4_NL GGUF. **Not comparable on latency** with the API lanes; no price (cost 0).",
          "Settings (frozen after p01 tuning, sources in `inkling/SETTINGS_NOTES.md`; tuning in `inkling/TUNING_LOG.md`): `llama-server --jinja -c 32768 -t 6 -tb 6 -np 1`, temp 1.0, top_k 50, top_p 1.0, min_p 0, default thinking effort (high, 0.9). One repeat, tasks run sequentially, frozen grader. Each task is capped at 12288 generated tokens, which the API lanes are not; every `no_code (length)` row below means the model was still thinking at the cap and wrote no final code, so those are token-budget failures, not wrong answers. One server process served all tasks, so the memory column is a running high-water mark. The load column is the 1-minute load average at task start; other host processes pushed it to 12-25 during p15 (2.2 tok/s vs 4-5 elsewhere), so p15's time is inflated.", "",
          f"## Primary result (max_tokens 12288): **{pa}/{len(a)}**", f"Total generation wall time {hms(ta)} ({ta/3600:.2f} h); median {sorted(x['wall_s'] for x in a)[len(a)//2]/60:.1f} min per task.", "", table(a), ""]
    if retry_root:
        stages = [(k, rows_for(k, os.path.join(retry_root, STAGE_DIRS[k]))) for k in ("medium", "low", "def24") if os.path.isdir(os.path.join(retry_root, STAGE_DIRS[k]))]
        allr = [x for _, rr in stages for x in rr]
        with open(os.path.join(RES, RETRY_OUT), "w") as f:
            for x in allr: f.write(json.dumps(x) + "\n")
        best = {x["problem"]: x for x in a}
        for _, rr in stages:  # a later stage only ran because the earlier one was capped, so the last row per task is the end of the ladder
            best.update({x["problem"]: x for x in rr})
        pb = sum(x["passed"] for x in best.values()); tr = sum(x["wall_s"] for x in allr)
        md += ["## Secondary: retry ladder on the tasks that were capped at 12288 (labelled; the primary above stays the headline)",
               "The operator asked for a retry of the capped tasks. Stage 1: thinking effort medium (0.7, `chat_template_kwargs.reasoning_effort`) at max_tokens 16384 on every capped task. Stage 2: effort low (0.2) at 16384 on the tasks still capped. Stage 3: default effort at 24576 on the task still capped. A task moves to the next stage only if it ended `no_code` at the cap; a wrong or crashing answer ends the ladder for that task. Same server flags, sampling and grader as the primary. Host load at task start was 5.7-14.8 during these runs (3.0-4.5 tok/s, slower than the primary), so times are inflated by other host processes.", "",
               f"**Ladder result: {pb}/{len(best)}** (primary passes + best ladder outcome per task). This mixes settings per task, so it is a secondary figure, not a single-configuration score. Retry wall time {hms(tr)} ({tr/3600:.2f} h); primary + retries {hms(ta+tr)} ({(ta+tr)/3600:.2f} h)."]
        for k, rr in stages:
            c, cap, eff, _ = RUNS[k]
            md += ["", f"### Stage `{c}` (effort {eff}, max_tokens {cap}): {sum(x['passed'] for x in rr)}/{len(rr)} pass", "", table(rr)]
        md += [""]
    open(os.path.join(RES, "inkling-mini.md"), "w").write("\n".join(md) + "\n"); print("\n".join(md[:8]))


if __name__ == "__main__": main(*sys.argv[1:])
