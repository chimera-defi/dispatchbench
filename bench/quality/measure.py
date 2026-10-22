"""Quality measurements for one code string: static (LOC, cyclomatic complexity, lint) and empirical (time growth, memory).

Static metrics run once in batch with uvx (radon==6.0.1, ruff@0.17.1). Runtime metrics run the candidate in the same sandbox as
bench/grade.py (python3 -I, 2 GB RLIMIT_AS, CPU limit) through bench.grade.run_sandbox, one fresh process per repeat, and use the
function's own timer (bench/sandbox_exec.py reports it), so interpreter start-up and JSON loading are not timed."""
import hashlib, io, json, math, os, resource, subprocess, sys, tempfile, tokenize

from bench import problems
from bench.grade import MEM_BYTES, _limits, run_sandbox
from bench.quality import sizes as S

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CACHE = os.path.join(ROOT, "cache", "quality")
CAP_S = 10.0          # a single run longer than this is killed and the size counts as capped
REPS = 3              # min over this many fresh processes per size (1 if the first run took more than SLOW_S)
SLOW_S = 2.0
MEM_WALL_S = 60.0     # tracemalloc is slow; the memory run gets its own, larger wall limit
RADON = "radon==6.0.1"
RUFF = "ruff@0.17.1"
LINT_SELECT = ["--select", "E,F,W,B", "--ignore", "E501"]


# ----------------------------------------------------------------------------------------------------------- static
def loc(code):
    """Non-blank, non-comment source lines (a line counts if it has any token other than a comment/newline). Docstrings count."""
    try:
        lines = set()
        for tok in tokenize.generate_tokens(io.StringIO(code).readline):
            if tok.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER):
                continue
            lines.update(range(tok.start[0], tok.end[0] + 1))
        return len(lines)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return sum(1 for ln in code.splitlines() if ln.strip() and not ln.strip().startswith("#"))


def _blocks(entries):
    """Function and method blocks, closures included. Class entries are skipped (radon repeats their methods at top level)."""
    for e in entries:
        if e.get("type") != "class":
            yield e["complexity"]
            yield from _blocks(e.get("closures", []))


def static_batch(codes):
    """{id: code} -> {id: {loc, cc_max, cc_total, lint_warnings, lint_codes, static_note}}. One radon and one ruff call."""
    out = {i: {"loc": loc(c), "cc_max": None, "cc_total": None, "lint_warnings": None, "lint_codes": None, "static_note": None}
           for i, c in codes.items()}
    if not codes:
        return out
    with tempfile.TemporaryDirectory(prefix="quality-static-") as d:
        for i, c in codes.items():
            open(os.path.join(d, i + ".py"), "w").write(c)
        r = subprocess.run(["uvx", RADON, "cc", "-j", "-s", d], capture_output=True, text=True, stdin=subprocess.DEVNULL)
        radon = json.loads(r.stdout) if r.stdout.strip() else {}
        r2 = subprocess.run(["uvx", RUFF, "check", "--isolated", "--no-cache", "--output-format", "json", *LINT_SELECT, d],
                            capture_output=True, text=True, stdin=subprocess.DEVNULL)
        diags = json.loads(r2.stdout) if r2.stdout.strip() else []
        if not r.stdout.strip() or (r2.returncode not in (0, 1) or not r2.stdout.strip()):
            raise RuntimeError(f"radon/ruff failed: {r.stderr[-300:]} {r2.stderr[-300:]}")
        lint = {i: [] for i in codes}
        for dg in diags:
            lint[os.path.basename(dg["filename"])[:-3]].append(dg["code"] or "SyntaxError")
        for i in codes:
            ent = radon.get(os.path.join(d, i + ".py"))
            if isinstance(ent, dict):
                out[i]["static_note"] = f"radon: {ent.get('error', 'failed')}"[:120]
            elif ent is not None:
                cc = list(_blocks(ent))
                out[i]["cc_max"] = max(cc) if cc else 0
                out[i]["cc_total"] = sum(cc)
            out[i]["lint_warnings"] = len(lint[i]); out[i]["lint_codes"] = sorted(set(lint[i]))
    return out


def tool_versions():
    v = {"python": sys.version.split()[0]}
    for name, spec in (("radon", RADON), ("ruff", RUFF)):
        r = subprocess.run(["uvx", spec, "--version"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
        v[name] = r.stdout.strip() or r.stderr.strip()[-80:]
    return v


# --------------------------------------------------------------------------------------------------------- generators
def gen_hash(pid):
    """Changes when the generator file, the problem file or the measurement settings change: invalidates cached runtime results."""
    h = hashlib.sha256()
    for p in (os.path.join(HERE, "sizes.py"), problems.path(pid), os.path.abspath(__file__), os.path.join(HERE, "mem_exec.py")):
        h.update(open(p, "rb").read())
    h.update(repr((CAP_S, REPS, SLOW_S, MEM_WALL_S)).encode())
    return h.hexdigest()[:16]


_ARGS = {}


def args_for(pid, n):
    k = (pid, n)
    if k not in _ARGS:
        _ARGS[k] = list(S.sized(pid, S.rng_for(pid, n), n))
        assert S.N0[pid] * 8 <= S.MAX_N[pid]
    return _ARGS[k]


# --------------------------------------------------------------------------------------------------------- time growth
def out_hash(out):
    return hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()[:16]


def fit_exp(points):
    """Least-squares slope of log(time) on log(n); None with fewer than 2 points."""
    pts = [(math.log(n), math.log(max(t, 1e-7))) for n, t in points]
    if len(pts) < 2:
        return None
    mx = sum(x for x, _ in pts) / len(pts); my = sum(y for _, y in pts) / len(pts)
    den = sum((x - mx) ** 2 for x, _ in pts)
    return sum((x - mx) * (y - my) for x, y in pts) / den


def time_growth(pid, src_path, func, cap_s=CAP_S):
    """Runs the function at n0, 2 n0, 4 n0, 8 n0. Returns {"sizes": {n: {"s": min seconds, "hash": out hash} | {"capped": reason}
    | {"err": text}}, "stopped": bool}. Stops at the first size that is capped or errors."""
    res = {}
    for n in S.sizes(pid):
        args = args_for(pid, n); times = []; h = None; stop = None
        for rep in range(REPS):
            r, st = run_sandbox(src_path, func, [args], cap_s)
            if st == "timeout":
                stop = {"capped": f"over {cap_s:g} s"}; break
            if st != "ok":
                stop = {"err": st[:160]}; break
            r = r[0]
            if "err" in r:
                stop = {"capped": "memory limit"} if r["err"].startswith("MemoryError") else {"err": r["err"][:160]}; break
            times.append(r["s"]); h = h or out_hash(r["out"])
            if rep == 0 and r["s"] > SLOW_S: break
        if times:
            res[n] = {"s": min(times), "hash": h, "reps": len(times)}
            if stop: res[n]["capped"] = stop.get("capped"); res[n]["err"] = stop.get("err")  # partial: later repeat failed
        else:
            res[n] = stop
        if stop: break
    return res


def summarize_growth(g):
    """From time_growth output to time_exp etc. A size that failed or was capped is excluded from the fit."""
    ok = {n: v for n, v in g.items() if "s" in v}
    return {"time_exp": fit_exp([(n, v["s"]) for n, v in ok.items()]),
            "t_n0_ms": round(ok[min(ok)]["s"] * 1000, 4) if ok else None, "n_ok": sorted(ok),
            "capped": any(v.get("capped") for v in g.values()), "capped_at": next((n for n, v in g.items() if v.get("capped")), None),
            "err": next(((n, v["err"]) for n, v in g.items() if v.get("err")), None)}


# ------------------------------------------------------------------------------------------------------------ memory
def peak_memory(pid, src_path, func):
    """tracemalloc peak (bytes) of one call at 4 n0, in its own sandbox process. Returns (bytes | None, note | None)."""
    n = S.N0[pid] * 4
    with tempfile.TemporaryDirectory(prefix="quality-mem-") as d:
        cp, op = os.path.join(d, "cases.json"), os.path.join(d, "out.json")
        json.dump([args_for(pid, n)], open(cp, "w"))
        try:
            r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "mem_exec.py"), src_path, func, cp, op], cwd=d, capture_output=True,
                               text=True, timeout=MEM_WALL_S, preexec_fn=_limits(MEM_WALL_S), stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return None, f"memory run over {MEM_WALL_S:g} s"
        if not os.path.exists(op):
            return None, f"memory run died rc={r.returncode}"
        res = json.load(open(op))
    return (res["peak"], None) if "peak" in res else (None, f"memory run: {res['err']}")
