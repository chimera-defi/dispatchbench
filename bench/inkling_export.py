"""Turn local Inkling 2 Mini runner output (pNN.result.json, results/inkling/runner.py) into DispatchBench rows and a report.
Offline, no model calls. Usage: python3 -m bench.inkling_export <primary_run_dir> [<secondary_run_dir>]"""
import datetime, hashlib, json, os, shutil, sys
from bench import run as R

RES = os.path.join(R.ROOT, "results")
RUNS = {"primary": ("inkling2mini-default", 12288, "2026-11-22-inkling-function.jsonl"),
        "secondary": ("inkling2mini-n24576", 24576, "2026-11-22-inkling-n24576-function.jsonl")}


def rows_for(kind, d):
    config, cap, out = RUNS[kind]; rows = []
    flags = ["llama-server b12600", "--jinja", "-c", "32768", "-t", "6", "-np", "1", "--temp", "1.0", "--top-k", "50", "--top-p", "1.0", "--min-p", "0", f"max_tokens={cap}"]
    rawdir = os.path.join(RES, "inkling", "raw-" + kind); os.makedirs(rawdir, exist_ok=True)
    for pid in sorted(f[:-12] for f in os.listdir(d) if f.endswith(".result.json") and f.startswith("p")):
        r = json.load(open(f"{d}/{pid}.result.json")); v = r.get("verdict") or {}; prompt = R.prompt_for(pid)
        key = hashlib.sha256(json.dumps({"config": config, "flags": flags, "prompt": prompt, "problem": pid, "repeat": 1}, sort_keys=True).encode()).hexdigest()
        rows.append({"ts": datetime.datetime.fromtimestamp(os.path.getmtime(f"{d}/{pid}.result.json"), datetime.timezone.utc).isoformat(timespec="seconds"),
            "phase": "exploratory", "config": config, "cli": "llama.cpp", "cli_version": "b12600", "model": "Inkling-2-Mini-IQ4_NL.gguf", "effort": "default",
            "problem": pid, "repeat": 1, "lanes": 1, "wall_s": r["wall_s"], "api_duration_ms": None, "in_tok": r.get("prompt_tok"), "cached_tok": 0, "cache_write_tok": 0,
            "out_tok": r.get("out_tok"), "reasoning_tok": None, "cost_usd": 0.0, "cost_kind": "free local CPU model (i7-8700, no list price)", "tool_items": None,
            "is_error": bool(r.get("error")), "error": r.get("error"), "key": key, "prompt_sha": hashlib.sha256(prompt.encode()).hexdigest()[:12], "codex_home": None,
            "rung": R.problems.load(pid).RUNG, "outcome": v.get("outcome"), "passed": v.get("outcome") == "pass", "grade_detail": v.get("detail"),
            "code_lines": r.get("code_lines"), "finish_reason": r.get("finish_reason"), "max_tokens": cap, "gen_tok_per_s": r.get("gen_tps"),
            "prompt_tok_per_s": r.get("prompt_tps"), "peak_rss_kib": (r.get("rss_end") or {}).get("VmHWM") or r.get("peak_rss_kib"), "loadavg_start": r.get("loadavg_start")})
        shutil.copy(f"{d}/{pid}.raw.txt", f"{rawdir}/{pid}.raw.txt")
    with open(os.path.join(RES, out), "w") as f:
        for x in rows: f.write(json.dumps(x) + "\n")
    return rows


def hms(s): return f"{int(s//3600)}h{int(s%3600//60):02d}m"


def table(rows):
    t = ["| problem | rung | outcome | wall | out tok | gen tok/s | peak RSS GiB | load avg |", "|---|---|---|---|---|---|---|---|"]
    for x in rows:
        t.append(f"| {x['problem']} | L{x['rung']} | {'pass' if x['passed'] else x['outcome'] + ' (' + str(x['finish_reason']) + ')'} | {x['wall_s']/60:.1f} min | {x['out_tok']} | {x['gen_tok_per_s']:.1f} | {(x['peak_rss_kib'] or 0)/1048576:.1f} | {x['loadavg_start'][0]} |")
    return "\n".join(t)


def main(prim, sec=None):
    a = rows_for("primary", prim); b = rows_for("secondary", sec) if sec and os.path.isdir(sec) else []
    pa = sum(x["passed"] for x in a); ta = sum(x["wall_s"] for x in a)
    md = ["# Inkling 2 Mini on DispatchBench p01-p15 (2026-11-22)", "",
          "Free local CPU model (i7-8700 6C/12T, ~63 GiB RAM, no GPU), llama.cpp b12600, IQ4_NL GGUF. **Not comparable on latency** with the API lanes; no price (cost 0).",
          "Settings (frozen after p01 tuning, sources in `inkling/SETTINGS_NOTES.md`; tuning in `inkling/TUNING_LOG.md`): `llama-server --jinja -c 32768 -t 6 -tb 6 -np 1`, temp 1.0, top_k 50, top_p 1.0, min_p 0, default thinking effort (high, 0.9). One repeat, tasks run sequentially, frozen grader.", "",
          f"## Primary result (max_tokens 12288): **{pa}/{len(a)}**", f"Total generation wall time {hms(ta)} ({ta/3600:.2f} h); median {sorted(x['wall_s'] for x in a)[len(a)//2]/60:.1f} min per task.", "", table(a), ""]
    if b:
        merged = {x["problem"]: x for x in a}; merged.update({x["problem"]: x for x in b}); pm = sum(x["passed"] for x in merged.values()); tb = sum(x["wall_s"] for x in b)
        md += [f"## Secondary run (max_tokens 24576): reruns of the tasks that ended `no_code` at the 12288 cap", f"Passes {sum(x['passed'] for x in b)}/{len(b)} of the rerun tasks; combined with the primary passes: **{pm}/{len(merged)}** (secondary, labelled; the primary {pa}/{len(a)} stays the headline). Rerun wall time {hms(tb)}; both runs {hms(ta+tb)}.", "", table(b), ""]
    open(os.path.join(RES, "inkling-mini.md"), "w").write("\n".join(md) + "\n"); print("\n".join(md[:8]))


if __name__ == "__main__": main(*sys.argv[1:])
