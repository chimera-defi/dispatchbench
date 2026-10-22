"""Recover which test files each agentic run wrote and how many test functions it added, from the raw transcripts.

    python3 -m analysis.agentic_tests

Rebuildable from the scrubbed transcripts in cache/agentic_raw/. Use --scrub to copy cache/raw/agentic-<key>.out there
with local paths and email addresses scrubbed. It writes results/agentic_tests.json and never copies transcript text,
paths or commands into it. Standard library only, no model calls.

What is recoverable (inspected, see `method`):
  claude: Write / Edit / MultiEdit tool inputs (content, so test functions are counted: `def test_` in the written
          content, or in new_string minus old_string for edits), plus Bash heredoc writes (cat/tee > tests/...).
  codex:  file_change events list paths only (no content), so touched test files are known but added functions are not,
          except where the file was written by a shell heredoc (`cat > tests/... <<EOF`), which carries the content.
In-place rewrites of an existing test file through shell (python - <<EOF ... s.replace, sed -i) are not parsed, so counts are
lower bounds: they cover new files and Write/Edit/heredoc content only.
test_functions_added is null when a touched test file's content was not recoverable (a lower bound is then reported
in test_functions_lower_bound)."""
import argparse, json, os, re

from bench.run import ROOT

AGENTIC = os.path.join(ROOT, "cache", "agentic")
RAW = os.path.join(ROOT, "cache", "agentic_raw")
SOURCE_RAW = os.path.join(ROOT, "cache", "raw")
OUT = os.path.join(ROOT, "results", "agentic_tests.json")
TEST_DEF = re.compile(r"^\s*(?:async\s+)?def test_\w*", re.M)
HOME_PATH = re.compile(r"/home/[^/\\\s\"'<>]+")
TMP_PATH = re.compile(r"/tmp(?=/|[\s\"'<>]|$)")
EMAIL = re.compile(r"(?<![\w.+\\-\\\\])[\w.!#$%&'*+/=?^`{|}~-]+@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,}")
REL_PATH = re.compile(r"(?:\.\./|claude-\d+/)[^\s\"'\\]+")
# Commands that only the host's user-level AGENTS.md asks for: look for AGENTS.md files, run its search helper or its delegate, clean up the
# delegate's artifacts/ directory. Counted per run so the report can say how much of the Codex agentic work the host file caused.
HOST_DOC = re.compile(r"AGENTS\.md|token-reduce|kimi-delegate|\bartifacts\b")
HEREDOC = re.compile(r"(?:cat|tee)\s+(?:-a\s+)?(?:>>?\s*)?(['\"]?)((?:<path>)?[^\s<>|'\"]*tests/[^\s<>|'\"]+)\1[^\n]*<<\s*-?\\?['\"]?(\w+)['\"]?[^\n]*\n(.*?)\n\3\b", re.S)


def test_path(p):
    """Return the path relative to the first tests/ directory, or None. Only this relative tail is ever kept in memory."""
    m = re.search(r"(?:^|/)tests/(.+)$", p or "")
    return m.group(1) if m else None


def count_defs(s):
    return len(TEST_DEF.findall(s or ""))


def scrub_raw(source, dest):
    """Copy a transcript while replacing machine-specific path roots and email addresses."""
    text = open(source, encoding="utf-8", errors="replace").read()
    text = HOME_PATH.sub("<path>", text)
    text = TMP_PATH.sub("<path>", text)
    text = EMAIL.sub("<email>", text)
    text = REL_PATH.sub("<path>", text)  # sibling dirs an agent listed (e.g. rg --files ..) name other host sessions
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(text)


def scrub_raw_files():
    sources = sorted(os.path.join(SOURCE_RAW, f) for f in os.listdir(SOURCE_RAW) if f.startswith("agentic-") and f.endswith(".out"))
    for source in sources:
        scrub_raw(source, os.path.join(RAW, os.path.basename(source)))
    print(f"scrubbed {len(sources)} transcripts -> {os.path.relpath(RAW, ROOT)}")


def events(path):
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if isinstance(o, dict):
            yield o


def analyse(path):
    files, added, methods, unknown = set(), 0, set(), set()
    shell = host = 0
    for o in events(path):
        if o.get("type") == "assistant":
            for b in (o.get("message") or {}).get("content") or []:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                name, inp = b.get("name"), b.get("input") or {}
                if name in ("Write", "Edit", "MultiEdit"):
                    tp = test_path(inp.get("file_path"))
                    if tp is None:
                        continue
                    files.add(tp)
                    if name == "Write":
                        added += count_defs(inp.get("content")); methods.add("claude Write content")
                    elif name == "Edit":
                        added += max(0, count_defs(inp.get("new_string")) - count_defs(inp.get("old_string"))); methods.add("claude Edit new_string")
                    else:
                        for ed in inp.get("edits") or []:
                            added += max(0, count_defs(ed.get("new_string")) - count_defs(ed.get("old_string")))
                        methods.add("claude MultiEdit new_string")
                elif name == "Bash":
                    cmd = inp.get("command") or ""
                    shell += 1; host += bool(HOST_DOC.search(cmd))
                    for m in HEREDOC.finditer(cmd):
                        tp = test_path(m.group(2))
                        if tp:
                            files.add(tp); added += count_defs(m.group(4)); methods.add("shell heredoc content")
        elif o.get("type") == "item.completed" and isinstance(o.get("item"), dict):
            it = o["item"]
            if it.get("type") == "file_change":
                for ch in it.get("changes") or []:
                    tp = test_path(ch.get("path"))
                    if tp:
                        files.add(tp); unknown.add(tp); methods.add("codex file_change paths (no content)")
            elif it.get("type") == "command_execution":
                shell += 1; host += bool(HOST_DOC.search(it.get("command") or ""))
                for m in HEREDOC.finditer(it.get("command") or ""):
                    tp = test_path(m.group(2))
                    if tp:
                        files.add(tp); unknown.discard(tp); added += count_defs(m.group(4)); methods.add("shell heredoc content")
    return files, added, methods, unknown, shell, host


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scrub", action="store_true")
    if parser.parse_args().scrub:
        scrub_raw_files()
    out = []
    for f in sorted(os.listdir(AGENTIC)):
        if not f.endswith(".json"):
            continue
        r = json.load(open(os.path.join(AGENTIC, f)))
        raw = os.path.join(RAW, f"agentic-{r['key']}.out")
        row = {"key": r["key"], "config": r["config"], "task": r["task"], "repeat": r["repeat"]}
        if not os.path.exists(raw):
            row.update(test_files_touched=None, test_functions_added=None, test_functions_lower_bound=None, method="unrecoverable",
                       shell_commands=None, host_agents_md_commands=None)
        else:
            files, added, methods, unknown, shell, host = analyse(raw)
            row.update(shell_commands=shell, host_agents_md_commands=host,
                       test_files_touched=len(files),
                       test_functions_added=None if unknown else added,
                       test_functions_lower_bound=added,
                       method=", ".join(sorted(methods)) if methods else "no test writes found in transcript")
        out.append(row)
    out.sort(key=lambda r: (r["config"], r["task"], r["repeat"], r["key"]))
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"wrote {len(out)} rows -> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
