"""Grade every cached completion serially and write results/<run>-function.jsonl. No model calls.

Grades are cached in cache/grades by (problem file hash, code hash), so a rebuild only grades what changed."""
import hashlib, json, os, re, sys

from bench import problems
from bench.grade import grade_text
from bench.run import CALLS, ROOT

GRADES = os.path.join(ROOT, "cache", "grades")
OUT = os.path.join(ROOT, "results", "2026-10-22b-function.jsonl")
FIELDS = ["ts", "phase", "config", "cli", "cli_version", "model", "effort", "problem", "repeat", "lanes", "wall_s", "api_duration_ms",
          "in_tok", "cached_tok", "cache_write_tok", "out_tok", "reasoning_tok", "cost_usd", "cost_kind", "tool_items", "is_error", "error", "key", "prompt_sha", "codex_home"]


def extract(text):
    blocks = re.findall(r"```(?:python|py|python3)?[ \t]*\n(.*?)```", text or "", re.S)
    return blocks[-1] if blocks else (text or "")


# Grades are cached by (problem file, code), not by grader source. If the grader changes, these hashes stop matching
# and cached grades are refused rather than silently reused; regrade with an empty cache/grades/ and update the hashes.
GRADER_SHA = {"grade.py": "2a1339d60158a92320535736131618bf6ada0ec86a55b441ee9d8faff2246155",
              "sandbox_exec.py": "0440be72f984035604492c270785f989b29698061f7ba072df4ad32eaca63f2c"}


def check_grader():
    here = os.path.dirname(os.path.abspath(__file__))
    for f, want in GRADER_SHA.items():
        got = hashlib.sha256(open(os.path.join(here, f), "rb").read()).hexdigest()
        if want and got != want and os.listdir(GRADES):
            raise SystemExit(f"bench/{f} changed since cache/grades/ was written: clear cache/grades/ and update GRADER_SHA")


def main(entries=None, output=None):
    check_grader()
    rows = []
    entries = sorted(entries if entries is not None else
                     (json.load(open(os.path.join(CALLS, f))) for f in os.listdir(CALLS) if f.endswith(".json")),
                     key=lambda e: (e["ts"], e["config"]))
    os.makedirs(GRADES, exist_ok=True)
    for e in entries:
        code = extract(e.get("text"))
        ph = hashlib.sha256(open(problems.path(e["problem"]), "rb").read()).hexdigest()[:16]
        gk = hashlib.sha256((ph + "\0" + code).encode()).hexdigest()
        gp = os.path.join(GRADES, gk + ".json")
        if e["is_error"]:
            g = {"outcome": e.get("outcome", "harness_error"), "detail": (e.get("error") or "")[:300]}
        elif os.path.exists(gp):
            g = json.load(open(gp))
        else:
            g = grade_text(e["problem"], code) if code.strip() else {"outcome": "no_code", "detail": "empty completion"}
            json.dump(g, open(gp, "w"))
        m = problems.load(e["problem"])
        row = {k: e.get(k) for k in FIELDS}
        row.update(rung=m.RUNG, outcome=g["outcome"], passed=g["outcome"] == "pass", grade_detail=g.get("detail"), code_lines=code.count("\n"))
        rows.append(row)
    output = output or OUT
    with open(output, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
    print(f"graded {len(rows)} calls -> {os.path.relpath(output, ROOT)}")


if __name__ == "__main__":
    main()
