"""Checker validity, no model calls. For every problem:
1. ref reproduces every example in the statement;
2. ref and an independently written brute force agree on fixed cases and 2,000 random small inputs;
3. ref passes the grader; every planted wrong solution fails it."""
import json, random, sys, time
from concurrent.futures import ProcessPoolExecutor

from bench import problems
from bench.grade import grade_text, _norm, expected_for

N_AGREE = 2000


def check(pid):
    t0 = time.time(); m = problems.load(pid); errs = []
    for args, want in m.EXAMPLES:
        got = _norm(m.ref(*args))
        if got != _norm(want): errs.append(f"example {args!r:.80}: ref={got!r:.80} want={want!r:.80}")
    rng = random.Random(f"{pid}-selftest")
    for i, args in enumerate(list(m.fixed()) + [m.small(rng) for _ in range(N_AGREE)]):
        a, b = _norm(m.ref(*args)), _norm(m.brute(*args))
        if a != b:
            errs.append(f"ref!=brute on {args!r:.200}: ref={a!r:.100} brute={b!r:.100}"); break
    expected_for(pid)
    src = open(problems.path(pid)).read()
    ref_src = src + f"\n{m.FUNC} = ref\n"
    g = grade_text(pid, ref_src)
    if g["outcome"] != "pass": errs.append(f"ref does not pass grader: {g}")
    wrong = {}
    for name, code in m.WRONG.items():
        g = grade_text(pid, code); wrong[name] = g["outcome"]
        if g["outcome"] == "pass": errs.append(f"planted wrong '{name}' passes")
    return pid, errs, wrong, round(time.time() - t0, 1)


if __name__ == "__main__":
    ids = sys.argv[1:] or problems.IDS
    bad = 0
    with ProcessPoolExecutor(4) as ex:
        for pid, errs, wrong, secs in ex.map(check, ids):
            print(f"{pid}: {'OK' if not errs else 'FAIL'} ({secs}s) planted={json.dumps(wrong)}")
            for e in errs: print("   ", e)
            bad += bool(errs)
    sys.exit(1 if bad else 0)
