"""Runs inside the sandbox subprocess: python3 -I mem_exec.py <source.py> <func> <cases.json> <out.json>.
Loads <source.py>, then calls <func>(*cases[0]) under tracemalloc and writes {"peak": bytes, "s": seconds} or {"err": ...}.
tracemalloc starts after the module is loaded and the arguments are parsed, so it counts Python allocations made by the call
itself (the input is not included)."""
import json, runpy, sys, time, tracemalloc

src, func, cases_path, out_path = sys.argv[1:5]
args = json.load(open(cases_path))[0]
sys.argv = [src]
try:
    f = runpy.run_path(src, run_name="candidate")[func]
except BaseException as e:
    json.dump({"err": f"load: {type(e).__name__}: {e}"[:200]}, open(out_path, "w")); sys.exit(0)
tracemalloc.start()
t = time.perf_counter()
try:
    f(*args)
    res = {"peak": tracemalloc.get_traced_memory()[1], "s": time.perf_counter() - t}
except BaseException as e:
    res = {"err": f"{type(e).__name__}: {e}"[:200]}
tracemalloc.stop()
json.dump(res, open(out_path, "w"))
