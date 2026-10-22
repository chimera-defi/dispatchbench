"""Programmatic quality metrics for every graded completion. No model calls. Needs uvx (radon, ruff).

python3 -m bench.quality.run --jobs 4

Writes results/quality.jsonl (one row per cache/calls entry except phase "warmup", sorted by call key) and results/quality_meta.json.
Runtime metrics (time growth, memory) are measured only for completions whose grade outcome in results/2026-10-22b-function.jsonl is
"pass". Static metrics (LOC, cyclomatic complexity, lint) are computed for every completion that has code.
Results are cached per (problem, sha256(code)) in cache/quality/ and recomputed when sizes.py, the problem file or the measurement
settings change. Timing varies from run to run, and --jobs above 4 adds contention noise: the committed jsonl is the record."""
import argparse, datetime, hashlib, json, os, platform, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed

from bench import problems
from bench.grade_all import OUT as GRADES_JSONL, extract
from bench.quality import measure as M
from bench.quality import sizes as S
from bench.run import CALLS

ROOT = M.ROOT
OUT = os.path.join(ROOT, "results", "quality.jsonl")
META = os.path.join(ROOT, "results", "quality_meta.json")
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()


def _cpath(name):
    return os.path.join(M.CACHE, name)


def _load(name):
    p = _cpath(name)
    return json.load(open(p)) if os.path.exists(p) else None


def _save(name, obj):
    os.makedirs(M.CACHE, exist_ok=True); tmp = _cpath(f"{name}.{os.getpid()}.tmp")
    json.dump(obj, open(tmp, "w")); os.replace(tmp, _cpath(name))


def _ser(g):  # JSON keys must be strings
    return {str(n): v for n, v in g.items()}


def ref_measure(pid):
    """Cached per problem: reference time at each size, its output hashes, and its memory peak at 4 n0."""
    gh = M.gen_hash(pid); name = f"ref-{pid}-{gh}.json"
    c = _load(name)
    if c:
        return c
    g = M.time_growth(pid, problems.path(pid), "ref", cap_s=120)
    mem, mnote = M.peak_memory(pid, problems.path(pid), "ref")
    c = {"sizes": _ser(g), **M.summarize_growth(g), "mem_peak_bytes": mem, "mem_note": mnote}
    _save(name, c)
    return c


def cand_measure(pid, code, h):
    gh = M.gen_hash(pid); name = f"rt-{pid}-{gh}-{h}.json"
    c = _load(name)
    if c:
        return c
    ref = ref_measure(pid); func = problems.load(pid).FUNC
    import tempfile
    with tempfile.TemporaryDirectory(prefix="quality-cand-") as d:
        src = os.path.join(d, "cand.py"); open(src, "w").write(code)
        g = M.time_growth(pid, src, func)
        mem, mnote = M.peak_memory(pid, src, func)
    sm = M.summarize_growth(g); notes = []
    ok = [n for n in sm["n_ok"]]
    bad = [n for n in ok if g[n]["hash"] != ref["sizes"][str(n)]["hash"]]
    if bad: notes.append(f"output differs from ref at n={bad[0]}")
    if sm["err"]: notes.append(f"run error at n={sm['err'][0]}: {sm['err'][1]}")
    if sm["capped"]: notes.append(f"capped at n={sm['capped_at']}: {g[sm['capped_at']]['capped']}")
    if sm["t_n0_ms"] is not None and sm["t_n0_ms"] < 5: notes.append("t(n0)<5ms: exponent noisy")
    if mnote: notes.append(mnote)
    both = [n for n in ok if "s" in ref["sizes"].get(str(n), {})]
    ratio = g[max(both)]["s"] / max(ref["sizes"][str(max(both))]["s"], 1e-7) if both else None
    c = {"sizes": _ser(g), **sm, "agree": not bad, "time_ratio": ratio, "ratio_n": max(both) if both else None,
         "mem_peak_bytes": mem, "notes": notes}
    _save(name, c)
    return c


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", help="comma list of problem id prefixes, e.g. p04,p15 (pilot)")
    ap.add_argument("--per-problem", type=int, help="pilot: at most this many distinct passing codes per problem")
    ap.add_argument("--out", default=OUT); ap.add_argument("--meta", default=META)
    a = ap.parse_args()
    if a.jobs > 4: print("warning: --jobs above 4 adds timing noise", file=sys.stderr)
    t0 = time.time(); log = lambda *x: print(f"[{time.time() - t0:7.0f}s]", *x, flush=True)

    grades = {}
    for ln in open(GRADES_JSONL):
        r = json.loads(ln); grades[r["key"]] = r["outcome"]
    entries = [json.load(open(os.path.join(CALLS, f))) for f in os.listdir(CALLS) if f.endswith(".json")]
    entries = sorted((e for e in entries if e["phase"] != "warmup"), key=lambda e: e["key"])
    missing = [e["key"] for e in entries if e["key"] not in grades]
    assert not missing, f"{len(missing)} calls have no grade in {GRADES_JSONL}; run make grade"
    if a.only: entries = [e for e in entries if e["problem"].startswith(tuple(a.only.split(",")))]
    for e in entries: e["code"] = extract(e.get("text")); e["outcome"] = grades[e["key"]]; e["h"] = sha(e["code"])
    log(f"{len(entries)} calls, {sum(e['outcome'] == 'pass' for e in entries)} passing")

    # static: one radon and one ruff call over every code not cached
    need = {}
    for e in entries:
        if e["code"].strip() and not _load(f"static-{e['h']}.json"): need[e["h"]] = e["code"]
    if need:
        log(f"static metrics for {len(need)} new codes")
        for h, v in M.static_batch(need).items(): _save(f"static-{h}.json", v)

    # runtime: reference first (same worker pool, so it sees the same load), then the distinct passing codes
    work = {}
    for e in entries:
        if e["outcome"] == "pass": work.setdefault((e["problem"], e["h"]), e["code"])
    items = sorted(work.items())
    if a.per_problem:
        cnt = {}; keep = []
        for (pid, h), code in items:
            if cnt.get(pid, 0) < a.per_problem: keep.append(((pid, h), code)); cnt[pid] = cnt.get(pid, 0) + 1
        items = keep
    pids = sorted({p for (p, _), _ in items})
    with ProcessPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(ref_measure, p): p for p in pids}
        for i, f in enumerate(as_completed(futs)):
            r = f.result(); log(f"ref {futs[f]} ({i + 1}/{len(futs)}) exp={r['time_exp']}")
        futs = {ex.submit(cand_measure, p, c, h): (p, h) for (p, h), c in items}
        for i, f in enumerate(as_completed(futs)):
            f.result()
            if (i + 1) % 10 == 0 or i + 1 == len(futs): log(f"measured {i + 1}/{len(futs)}")

    rows = []
    for e in entries:
        pid = e["problem"]; code = e["code"]; row = {"key": e["key"], "problem": pid, "config": e["config"], "phase": e["phase"], "repeat": e["repeat"],
                                                     "outcome": e["outcome"]}
        st = _load(f"static-{e['h']}.json") or {}
        for k in ("loc", "cc_max", "cc_total", "lint_warnings", "lint_codes"): row[k] = st.get(k)
        note = [st["static_note"]] if st.get("static_note") else []
        if not code.strip(): note.append("no code")
        rt = None
        if e["outcome"] == "pass" and (pid, e["h"]) in work and not (a.per_problem and (pid, e["h"]) not in dict(items)):
            rt = cand_measure(pid, code, e["h"]); ref = ref_measure(pid)
            mem = rt["mem_peak_bytes"]; rmem = ref["mem_peak_bytes"]
            row.update(time_exp=rt["time_exp"], ref_time_exp=ref["time_exp"], time_ratio=rt["time_ratio"], capped=rt["capped"],
                       mem_peak_kb=None if mem is None else round(mem / 1024, 1), ref_mem_peak_kb=None if rmem is None else round(rmem / 1024, 1),
                       mem_ratio=None if not (mem and rmem) else mem / rmem)
            note += rt["notes"]
        else:
            row.update(time_exp=None, ref_time_exp=None, time_ratio=None, capped=None, mem_peak_kb=None, ref_mem_peak_kb=None, mem_ratio=None)
            if e["outcome"] != "pass": note.append(f"not measured: {e['outcome']}")
        row.update(size_param=S.SIZE_PARAM[pid], n0=S.N0[pid], note="; ".join(note) or None)
        row.update(t_n0_ms=rt["t_n0_ms"] if rt else None, ratio_n=rt["ratio_n"] if rt else None, capped_at=rt["capped_at"] if rt else None)
        rows.append(row)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
    refs = {p: ref_measure(p) for p in pids}
    meta = {"generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "tools": M.tool_versions(),
            "platform": platform.platform(), "cpus": os.cpu_count(), "jobs": a.jobs, "cap_s": M.CAP_S, "reps_per_size": M.REPS,
            "slow_first_run_s": M.SLOW_S, "mem_wall_s": M.MEM_WALL_S, "mem_size_factor": "4 * n0", "rows": len(rows),
            "n0": S.N0, "max_n": S.MAX_N, "sizes": {p: S.sizes(p) for p in S.N0},
            "ref_ms_at_n0": {p: r["t_n0_ms"] for p, r in refs.items()}, "ref_time_exp": {p: r["time_exp"] for p, r in refs.items()},
            "ref_mem_peak_kb": {p: None if r["mem_peak_bytes"] is None else round(r["mem_peak_bytes"] / 1024, 1) for p, r in refs.items()},
            "lint": {"select": "E,F,W,B", "ignore": "E501", "flags": "--isolated --no-cache"},
            "note": "timing varies run to run; jobs <= 4 on a 12-core host; this file and quality.jsonl are the record of one run"}
    json.dump(meta, open(a.meta, "w"), indent=1)
    log(f"wrote {len(rows)} rows -> {a.out}")


if __name__ == "__main__":
    main()
