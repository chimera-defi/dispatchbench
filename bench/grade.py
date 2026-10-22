"""Grades one candidate source against one problem. No model calls.

Outcomes: pass | wrong | timeout | crash | no_code. Cases are generated from a fixed seed per problem.
Small cases (fixed + 300 random) run in one sandbox process; each large case runs in its own process with
limit max(2 s, 10 x reference time measured in the same sandbox)."""
import hashlib, json, os, random, resource, subprocess, sys, tempfile

from bench import problems

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXEC = os.path.join(ROOT, "bench", "sandbox_exec.py")
EXPECTED_DIR = os.path.join(ROOT, "cache", "expected")
N_SMALL = 300
MEM_BYTES = 2 * 1024 ** 3


def _limits(cpu_s):
    def f():
        resource.setrlimit(resource.RLIMIT_AS, (MEM_BYTES, MEM_BYTES))
        resource.setrlimit(resource.RLIMIT_CPU, (int(cpu_s) + 1, int(cpu_s) + 2))
    return f


def run_sandbox(src_path, func, cases, wall_s):
    """Returns (results | None, status) where status is ok | timeout | crash:<detail>."""
    with tempfile.TemporaryDirectory(prefix="grade-") as d:
        cp, op = os.path.join(d, "cases.json"), os.path.join(d, "out.json")
        json.dump(cases, open(cp, "w"))
        try:
            r = subprocess.run([sys.executable, "-I", EXEC, src_path, func, cp, op], cwd=d, capture_output=True, text=True,
                               timeout=wall_s, preexec_fn=_limits(wall_s), stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return None, "timeout"
        if r.returncode in (-9, -24) or "CPU time limit" in r.stderr:  # SIGKILL / SIGXCPU from RLIMIT_CPU
            return None, "timeout"
        if not os.path.exists(op):
            return None, f"crash:rc={r.returncode} {r.stderr.strip()[-200:]}"
        res = json.load(open(op))
        if isinstance(res, dict):
            return None, f"crash:{res['load_error']}"
        return res, "ok"


def _norm(x):
    return json.loads(json.dumps(x, default=list))


def cases_for(pid):
    m = problems.load(pid); rng = random.Random(f"{pid}-v1")
    small = [list(a) for a in m.fixed()] + [list(m.small(rng)) for _ in range(N_SMALL)]
    big = [list(a) for a in m.big(rng)]
    return small, big


def expected_for(pid):
    """Reference outputs and reference timings, cached by the problem file's hash."""
    h = hashlib.sha256(open(problems.path(pid), "rb").read()).hexdigest()[:16]
    fp = os.path.join(EXPECTED_DIR, f"{pid}-{h}.json")
    if os.path.exists(fp):
        return json.load(open(fp))
    small, big = cases_for(pid); m = problems.load(pid)
    exp_small = [_norm(m.ref(*a)) for a in small]
    exp_big, ref_s = [], []
    for a in big:
        res, st = run_sandbox(problems.path(pid), "ref", [a], 600)
        assert st == "ok" and "out" in res[0], (pid, st, res)
        exp_big.append(res[0]["out"]); ref_s.append(res[0]["s"])
    data = {"small": exp_small, "big": exp_big, "ref_s": ref_s}
    os.makedirs(EXPECTED_DIR, exist_ok=True); json.dump(data, open(fp, "w"))
    return data


def grade_source(pid, src_path):
    m = problems.load(pid)
    code = open(src_path).read()
    if f"def {m.FUNC}" not in code:
        return {"outcome": "no_code", "detail": "function definition not found"}
    exp = expected_for(pid); small, big = cases_for(pid)
    res, st = run_sandbox(src_path, m.FUNC, small, 60)
    if st != "ok":
        return {"outcome": "timeout" if st == "timeout" else "crash", "detail": f"small cases: {st}"[:300]}
    for i, (r, e) in enumerate(zip(res, exp["small"])):
        if "err" in r:
            return {"outcome": "crash", "detail": f"small case {i}: {r['err']}", "case": i}
        if r["out"] != e:
            return {"outcome": "wrong", "detail": f"small case {i}", "case": i}
    worst = 0.0
    for i, (a, e, rs) in enumerate(zip(big, exp["big"], exp["ref_s"])):
        limit = max(2.0, 10 * rs)
        res, st = run_sandbox(src_path, m.FUNC, [a], limit + 10)
        if st != "ok":
            return {"outcome": "timeout" if st == "timeout" else "crash", "detail": f"large case {i}: {st}"[:300], "case": f"L{i}"}
        r = res[0]
        if "err" in r:
            return {"outcome": "crash", "detail": f"large case {i}: {r['err']}", "case": f"L{i}"}
        if r["s"] > limit:
            return {"outcome": "timeout", "detail": f"large case {i}: {r['s']:.2f}s > limit {limit:.2f}s", "case": f"L{i}"}
        if r["out"] != e:
            return {"outcome": "wrong", "detail": f"large case {i}", "case": f"L{i}"}
        worst = max(worst, r["s"] / limit)
    return {"outcome": "pass", "cases": len(small) + len(big), "worst_time_frac": round(worst, 3)}


def grade_text(pid, code):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, prefix="cand-") as f:
        f.write(code); p = f.name
    try:
        return grade_source(pid, p)
    finally:
        os.remove(p)


if __name__ == "__main__":
    print(json.dumps(grade_source(sys.argv[1], sys.argv[2])))
