"""Export every graded completion as a browsable file under results/solutions/. Standard library only, no model calls.

    python3 -m analysis.export_solutions        (or: make solutions)

Each cache/calls/*.json (phase "warmup" skipped) is passed through bench.grade_all.extract, the grader's own extractor.
The grade key sha256(problem_file_hash16 + NUL + code) is recomputed exactly as in bench/grade_all.py and the matching
cache/grades/<key>.json must exist (except harness_error / no_code rows, which have no cached grade), otherwise this
fails. Output is deterministic: sorted, no timestamps, so a re-run leaves no diff."""
import hashlib, json, os, shutil, sys
from collections import defaultdict

from bench import problems
from bench.grade_all import GRADES, extract
from bench.run import CALLS, ROOT

OUT = os.path.join(ROOT, "results", "solutions")
QUALITY = os.path.join(ROOT, "results", "quality.jsonl")
OUTCOMES = ["pass", "wrong", "crash", "timeout", "no_code", "harness_error"]


def grade_of(e, code):
    """Mirror bench/grade_all.main(): returns (grade dict, grade key)."""
    ph = hashlib.sha256(open(problems.path(e["problem"]), "rb").read()).hexdigest()[:16]
    gk = hashlib.sha256((ph + "\0" + code).encode()).hexdigest()
    gp = os.path.join(GRADES, gk + ".json")
    if e["is_error"] and not code.strip():
        return {"outcome": "harness_error", "detail": (e.get("error") or "")[:300]}, gk
    if not code.strip():
        return {"outcome": "no_code", "detail": "empty completion"}, gk
    if not os.path.exists(gp):
        raise SystemExit(f"grade key mismatch: no cache/grades/{gk}.json for call {e['key']} "
                         f"({e['config']} {e['problem']} {e['phase']} r{e['repeat']}); code is not what was graded")
    return json.load(open(gp)), gk


def loc(code):
    return sum(1 for l in code.splitlines() if l.strip() and not l.strip().startswith("#"))


def short(s, n=70):
    s = " ".join(str(s or "").split()).replace("|", "\\|")
    return s if len(s) <= n else s[:n - 3] + "..."


def read_quality():
    q = {}
    if not os.path.exists(QUALITY):
        return None
    for line in open(QUALITY, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if isinstance(o, dict) and o.get("key"):
            q[o["key"]] = o
    return q


def exploratory_entries():
    """Read cached F/G completions by rebuilding the runners' content-addressed keys."""
    from bench import gated_repair as G, plan_first as F
    from bench.run import cli_version, prompt_for
    from analysis.luna_rescue import PIDS

    appendix = os.path.join(ROOT, "results", "appendix", "luna_rescue.jsonl")
    if not os.path.exists(appendix): return []
    rows = [json.loads(line) for line in open(appendix) if line.strip()]
    out, seen = [], set()

    def cached(cache, kind, blob):
        key = hashlib.sha256(json.dumps(blob, sort_keys=True).encode()).hexdigest()
        path = os.path.join(cache, f"{kind}-{key}.json")
        if not os.path.exists(path): return key, None
        return key, json.load(open(path))

    indexed = {(r.get("arm"), r.get("config"), r.get("problem"), r.get("repeat")): r for r in rows}
    for rep in F.REPS:
        for pid in PIDS:
            for cfg in F.BUILDERS:
                row = indexed.get(("F", cfg, pid, rep), {})
                m = problems.load(pid); planner_prompt = F.PLAN.format(statement=m.STATEMENT.strip(), signature=m.SIGNATURE)
                plan_blob = {"model": F.PLANNER, "cli": row.get("claude_cli") or cli_version("claude"), "flags": F.CLAUDE_FLAGS,
                             "prompt": planner_prompt, "repeat": rep}
                _, plan = cached(F.CACHE, "plan", plan_blob)
                if not plan or not plan.get("text"): continue
                mid, effort, flags = F.BUILDERS[cfg]
                prompt = F.BUILD.format(prompt=prompt_for(pid), plan=plan["text"].strip())
                blob = {"config": cfg, "model": mid, "effort": effort, "cli": row.get("codex_cli") or cli_version("codex"),
                        "flags": flags, "prompt": prompt, "repeat": rep}
                key, result = cached(F.CACHE, "build", blob)
                if result and result.get("text") and ("F", key) not in seen:
                    seen.add(("F", key)); out.append(("F build", key, cfg, pid, rep, extract(result["text"]), row.get("check", "cached")))
    for rep in G.REPS:
        for pid in PIDS:
            for cfg, (mid, effort, flags, repair_kind) in G.CONFIGS.items():
                row = indexed.get(("G", cfg, pid, rep), {})
                blob, _ = G.build_key(pid, rep, mid, effort, flags)
                if row.get("codex_cli"): blob["cli"] = row["codex_cli"]
                key, build = cached(G.CACHE, "build", blob)
                if build and build.get("text") and ("G-build", key) not in seen:
                    seen.add(("G-build", key)); out.append(("G build", key, cfg, pid, rep, extract(build["text"]), "cached"))
                if not build or not build.get("text"): continue
                base_code = extract(build["text"])
                ok, report = G.visible(pid, base_code)
                if ok and repair_kind != "review": continue
                prompt = (G.REVIEW if repair_kind == "review" else G.REPAIR).format(
                    prompt=prompt_for(pid), report=report, code=base_code)
                if repair_kind in ("haiku", "review"):
                    model = "claude-haiku-5-5"
                    repair_blob = {"model": (model, "low"), "cli": row.get("claude_cli") or cli_version("claude"),
                                   "flags": G.CLAUDE_FLAGS, "prompt": prompt, "repeat": rep}
                else:
                    repair_blob = {"model": mid, "effort": effort, "cli": row.get("codex_cli") or cli_version("codex"),
                                   "flags": flags, "prompt": prompt, "repeat": rep}
                repair_key, repair = cached(G.CACHE, "repair", repair_blob)
                if repair and repair.get("text") and ("G-repair", repair_key) not in seen:
                    seen.add(("G-repair", repair_key)); out.append(("G repair", repair_key, cfg, pid, rep, extract(repair["text"]), row.get("check", "cached")))
    return out


def fmt(v):
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


def main():
    entries = []
    for f in sorted(os.listdir(CALLS)):
        if f.endswith(".json"):
            e = json.load(open(os.path.join(CALLS, f)))
            if e["phase"] != "warmup":
                entries.append(e)
    quality = read_quality()
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    rows = defaultdict(list)
    seen_keys, seen_names = set(), {}
    phase_counts = defaultdict(int); source_counts = defaultdict(int)
    for e in entries:
        if e["key"] in seen_keys:
            continue
        seen_keys.add(e["key"])
        code = extract(e.get("text"))
        g, gk = grade_of(e, code)
        rel = f"{e['config']}/{e['phase']}-r{e['repeat']}.py"
        name = (e["problem"], rel)
        if name in seen_names:
            raise SystemExit(f"file name collision {name}: calls {seen_names[name]} and {e['key']}")
        seen_names[name] = e["key"]
        path = os.path.join(OUT, e["problem"], rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(code.encode())
        assert open(path, "rb").read() == code.encode()
        phase_counts[e["phase"]] += 1
        rows[e["problem"]].append(dict(e=e, g=g, code=code, rel=rel))

    for source, key, cfg, pid, rep, code, outcome in exploratory_entries():
        rel = f"{cfg}/{source.lower().replace(' ', '-')}-r{rep}.py"
        name = (pid, rel)
        if name in seen_names: raise SystemExit(f"file name collision {name}: {seen_names[name]} and {key}")
        seen_names[name] = key
        path = os.path.join(OUT, pid, rel); os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh: fh.write(code.encode())
        assert open(path, "rb").read() == code.encode()
        phase_counts[source] += 1; source_counts[source] += 1
        rows[pid].append(dict(e={"config": cfg, "phase": source.lower().replace(" ", "-"), "repeat": rep,
                                 "key": key}, g={"outcome": outcome}, code=code, rel=rel))

    for pid in sorted(rows):
        m = problems.load(pid)
        rs = sorted(rows[pid], key=lambda r: (r["e"]["config"], r["e"]["phase"], r["e"]["repeat"]))
        head = ["config", "phase", "rep", "outcome", "grade detail", "LOC", "lines"]
        if quality is not None:
            head += ["cc_max", "lint", "time exp (model vs ref)", "mem ratio"]
        head += ["file"]
        out = [f"# {pid}", "", f"Rung L{m.RUNG}. Signature: `{m.SIGNATURE}`", "",
               "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        for r in rs:
            e = r["e"]
            cells = [e["config"], e["phase"], str(e["repeat"]), r["g"]["outcome"], short(r["g"].get("detail")),
                     str(loc(r["code"])), str(len(r["code"].splitlines()))]
            if quality is not None:
                q = quality.get(e["key"], {})
                cells += [fmt(q.get("cc_max")), fmt(q.get("lint_warnings")),
                          f"{fmt(q.get('time_exp'))} vs {fmt(q.get('ref_time_exp'))}", fmt(q.get("mem_ratio"))]
            cells.append(f"[{r['rel'].split('/')[-1]}]({r['rel']})")
            out.append("| " + " | ".join(cells) + " |")
        with open(os.path.join(OUT, pid, "index.md"), "w") as fh:
            fh.write("\n".join(out) + "\n")

    configs = sorted({r["e"]["config"] for rs in rows.values() for r in rs})
    ph = ", ".join(f"{k} {v}" for k, v in sorted(phase_counts.items()))
    out = ["# Graded solutions", "",
           "Every completion that was graded, as the code the grader saw. Browse `<problem>/index.md` for a table per problem "
           "(outcome, grade detail, size, and quality metrics when `results/quality.jsonl` exists).", "",
           "Layout: `<problem>/<config>/<phase>-r<repeat>.py`. The phase is in the name because the same config, problem and repeat "
           "can occur in several phases (calibration, main, hard, escalation, exploratory). Warmup calls are not exported.", "",
           "Each file is byte-identical to the code that was graded: it is the output of `bench.grade_all.extract` on the cached "
           "completion, with no header added. `python3 -m analysis.export_solutions` recomputes the grade key "
           "`sha256(problem_file_hash16 + NUL + code)` for every file and fails unless `cache/grades/<key>.json` exists "
           "(harness errors and empty completions have no cached grade). Output is deterministic; re-running leaves no diff.", "",
           f"Files by phase: {ph}. Total {sum(phase_counts.values())}.", "",
           "Post-hoc appendix F/G completions are exported when their cache entries hold text; other appendix arms contain "
           "summary rows only.", "",
           "Passes per config (pass / graded, all phases):", "",
           "| problem | rung | " + " | ".join(configs) + " |", "|---|---|" + "---|" * len(configs)]
    for pid in sorted(rows):
        cells = []
        for c in configs:
            rs = [r for r in rows[pid] if r["e"]["config"] == c]
            graded = [r for r in rs if r["g"]["outcome"] in OUTCOMES]
            cells.append(f"{sum(r['g']['outcome'] == 'pass' for r in graded)}/{len(graded)}" if graded else "-")
        out.append(f"| [{pid}]({pid}/index.md) | L{problems.load(pid).RUNG} | " + " | ".join(cells) + " |")
    with open(os.path.join(OUT, "README.md"), "w") as fh:
        fh.write("\n".join(out) + "\n")
    counts = ", ".join(f"{k} {v}" for k, v in sorted(source_counts.items())) or "none"
    print(f"exported {sum(phase_counts.values())} solutions ({ph}; exploratory: {counts}) for {len(rows)} problems -> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
