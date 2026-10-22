"""Runs inside the sandbox subprocess: python3 -I sandbox_exec.py <source.py> <func> <cases.json> <out.json>.
Loads <source.py>, calls <func>(*args) for each case, and writes [{"out": ..., "s": seconds} | {"err": "..."}]."""
import json, runpy, sys, time, traceback

src, func, cases_path, out_path = sys.argv[1:5]
cases = json.load(open(cases_path))
sys.argv = [src]
try:
    ns = runpy.run_path(src, run_name="candidate")
    f = ns[func]
except BaseException as e:
    json.dump({"load_error": f"{type(e).__name__}: {e}"[:300]}, open(out_path, "w")); sys.exit(0)
res = []
for args in cases:
    t = time.perf_counter()
    try:
        out = f(*args)
        res.append({"out": json.loads(json.dumps(out, default=list)), "s": time.perf_counter() - t})
    except BaseException as e:
        res.append({"err": f"{type(e).__name__}: {e}"[:200], "tb": traceback.format_exc()[-300:], "s": time.perf_counter() - t})
json.dump(res, open(out_path, "w"))
