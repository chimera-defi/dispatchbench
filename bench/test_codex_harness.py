"""Harness contract checks; never invoke a real model or inspect problem solutions."""
from pathlib import Path
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from bench import codex_harness as H


class HarnessTests(unittest.TestCase):
    def test_claude_json_cost_tokens_and_error_extraction(self):
        result = dict(type="result", result="Done.", is_error=False, total_cost_usd=0.0123,
                      duration_api_ms=456, num_turns=4, usage={
                          "input_tokens": 20, "cache_creation_input_tokens": 30,
                          "cache_read_input_tokens": 40, "output_tokens": 50})
        parsed = H.parse_claude(json.dumps(result))
        self.assertEqual(parsed["text"], "Done.")
        self.assertEqual(parsed["in_tok"], 90)
        self.assertEqual(parsed["cached_tok"], 40)
        self.assertEqual(parsed["cache_write_tok"], 30)
        self.assertEqual(parsed["out_tok"], 50)
        self.assertEqual(parsed["cost_usd"], 0.0123)
        self.assertEqual(parsed["cost_kind"], "measured (CLI total_cost_usd)")
        self.assertEqual(parsed["api_duration_ms"], 456)
        self.assertIsNone(parsed["error"])
        result.update(is_error=True, result="permission denied")
        self.assertIn("permission denied", H.parse_claude(json.dumps(result))["error"])
        self.assertTrue(H.parse_claude("invalid JSON")["error"])
        self.assertTrue(H.parse_claude("[]")["error"])

    def test_claude_prompt_key_and_command_are_family_specific(self):
        pid = "p01_overlap_minutes"
        prompt = H.prompt_for(pid, "haiku-low")
        self.assertIn(H.problems.load(pid).STATEMENT, prompt)
        self.assertIn("<submission>", prompt)
        args = ("haiku-low", pid, 1, prompt, "2.1.293", "bwrap-test")
        key = H.key_for(*args)
        with patch.object(H, "CLAUDE_FLAGS", H.CLAUDE_FLAGS + ["--no-chrome"]):
            self.assertNotEqual(key, H.key_for(*args))
        with tempfile.TemporaryDirectory() as d:
            work, home = H.prepare_dirs(Path(d), "claude")
            cmd = H.command_for("haiku-high", work, home, Path("/usr/bin/claude"), auth=None)
            self.assertIn("claude-haiku-5-5", cmd)
            self.assertEqual(cmd[cmd.index("--effort") + 1], "high")
            self.assertEqual(cmd[cmd.index("--permission-mode") + 1], "dontAsk")
            self.assertNotIn("--dangerously-skip-permissions", cmd)
            self.assertEqual(cmd[-1], "-p")
        self.assertEqual(H.CONFIGS["sonnet-medium"], ("claude-sonnet-5-5", "medium"))

    def test_claude_artifact_pipeline_and_exported_cost(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            fake = base / "fake-claude"
            fake.write_text('''#!/usr/bin/python3
import json, sys
from pathlib import Path
assert '-p' in sys.argv
assert '<submission>' in sys.stdin.read()
assert not Path('~').exists()
assert not Path('/home/codex/.claude/CLAUDE.md').exists()
assert not Path('/home/codex/.codex/auth.json').exists()
Path('/work/solution.py').write_text('def f(): return "```python literal"\\n')
print(json.dumps({'type': 'result', 'result': 'Done, not the source.', 'is_error': False,
 'total_cost_usd': 0.0042, 'duration_api_ms': 123, 'num_turns': 3,
 'usage': {'input_tokens': 11, 'output_tokens': 22, 'cache_read_input_tokens': 33}}))
''')
            fake.chmod(0o755)
            with patch.object(H, "CACHE", base / "cache"), \
                    patch.object(H, "claude_binary", return_value=fake), \
                    patch.object(H, "claude_auth_path", return_value=None):
                first = H.one("haiku-low", "p01_overlap_minutes", 1, 3, "2.1.293", "bwrap-test")
                with patch.object(H, "call_claude", side_effect=AssertionError("cache must prevent launch")):
                    self.assertEqual(first, H.one("haiku-low", "p01_overlap_minutes", 1, 3, "2.1.293", "bwrap-test"))
                self.assertEqual(first["cli"], "claude")
                self.assertEqual(first["text"], 'def f(): return "```python literal"\n')
                self.assertEqual(first["final_message"], "Done, not the source.")
                self.assertFalse(first["is_error"], first.get("error"))
                with patch.object(H, "grade_text", return_value={"outcome": "pass"}):
                    row = H.grade_entry(first)
                self.assertEqual(row["cost_usd"], 0.0042)
                self.assertEqual(row["cost_kind"], "measured (CLI total_cost_usd)")
                self.assertEqual(row["in_tok"], 44)
                self.assertEqual(set(row), set(H.FIELDS) | {
                    "rung", "outcome", "passed", "grade_detail", "code_lines", "harness"})

    def test_mixed_cli_runs_both_families_with_offline_executables(self):
        with tempfile.TemporaryDirectory(dir=H.ROOT) as d:
            base = Path(d)
            fake = base / "offline-cli"
            fake.write_text('''#!/usr/bin/python3
import json, sys
from pathlib import Path
if '--version' in sys.argv:
    print('offline-test-version')
    raise SystemExit
prompt = sys.stdin.read()
assert '<problem>' in prompt
model = sys.argv[sys.argv.index('--model') + 1]
if model.startswith('claude-'):
    assert '--effort' in sys.argv
    assert '<submission>' in prompt
    result = {'type': 'result', 'is_error': False, 'result': 'Done.',
              'total_cost_usd': 0.001, 'usage': {'input_tokens': 10, 'output_tokens': 20}}
else:
    assert any(x.startswith('model_reasoning_effort=') for x in sys.argv)
    result = {'type': 'turn.completed', 'usage': {'input_tokens': 10, 'output_tokens': 20}}
Path('/work/solution.py').write_text('def fixture_only(): return 1\\n')
print(json.dumps(result))
''')
            fake.chmod(0o755)
            out = base / "rows.jsonl"
            argv = ["bench.codex_harness", "--configs", ",".join(H.CONFIGS),
                    "--repeats", "1", "--lanes", "3", "--problems", "p01_overlap_minutes"]
            with patch.object(sys, "argv", argv), \
                    patch.object(H, "CACHE", base / "cache"), \
                    patch.object(H, "OUT", out), patch.object(H, "CODEX", str(fake)), \
                    patch.object(H, "CLAUDE", str(fake)), patch.object(H, "auth_path", return_value=None), \
                    patch.object(H, "claude_auth_path", return_value=None), \
                    patch.object(H, "grade_text", return_value={"outcome": "pass"}) as grader, \
                    contextlib.redirect_stdout(io.StringIO()):
                H.main()
                # Identical fixture code shares a single cached grade across families.
                self.assertEqual(grader.call_count, 1)
            rows = [json.loads(line) for line in out.read_text().splitlines()]
            self.assertEqual({r["config"] for r in rows}, set(H.CONFIGS))
            self.assertTrue(all(r["passed"] and not r["is_error"] for r in rows))
            for row in rows:
                self.assertEqual(row["cli"], H.cli_for(row["config"]))
                self.assertEqual((row["model"], row["effort"]), H.CONFIGS[row["config"]])
                self.assertEqual(row["cli_version"], "offline-test-version")
                if row["cli"] == "claude":
                    self.assertEqual(row["cost_usd"], 0.001)

    def test_extracts_exact_artifact_not_final_message(self):
        with tempfile.TemporaryDirectory() as d:
            code = 'def f():\n    return "```python is data, not a fence"\n'
            Path(d, "solution.py").write_text(code)
            self.assertEqual(H.extract_answer(Path(d)), code)

    def test_missing_and_symlink_artifacts_are_not_answers(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(H.extract_answer(Path(d)), "")
            Path(d, "other.py").write_text("def f(): return 123\n")
            Path(d, "solution.py").symlink_to(Path(d, "other.py"))
            self.assertEqual(H.extract_answer(Path(d)), "")

    def test_prompt_preserves_statement(self):
        p = H.prompt_for("p01_overlap_minutes")
        self.assertIn(H.problems.load("p01_overlap_minutes").STATEMENT, p)
        self.assertIn("solution.py", p)

    def test_key_changes_with_prompt_flags_repeat_and_effort(self):
        args = ("luna-low", "p01_overlap_minutes", 1, "statement", "0.163.0", "bwrap-test")
        key = H.key_for(*args)
        for index, value in [(0, "luna-medium"), (2, 2), (3, "changed statement")]:
            changed = list(args)
            changed[index] = value
            self.assertNotEqual(key, H.key_for(*changed))
        with patch.object(H, "CODEX_FLAGS", H.CODEX_FLAGS + ["-c", "model_verbosity=low"]):
            self.assertNotEqual(key, H.key_for(*args))

    def test_isolation_allows_python_but_hides_repo_and_host_home(self):
        with tempfile.TemporaryDirectory() as d:
            work, home = H.prepare_dirs(Path(d))
            script = (
                "from pathlib import Path; "
                f"assert not Path({str(H.ROOT)!r}).exists(); "
                "assert not Path('~').exists(); "
                "assert not Path('/home/codex/.codex/AGENTS.md').exists(); "
                "Path('/work/solution.py').write_text('def f(): return 42\\n'); "
                "print('ISOLATION_OK')"
            )
            cmd = H.isolation_prefix(work, home, Path('/usr/bin/true'), auth=None)
            result = subprocess.run(cmd + ['/usr/bin/python3', '-c', script],
                                    env=H.child_env(), capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "ISOLATION_OK")
            self.assertEqual(H.extract_answer(work), "def f(): return 42\n")

    def test_native_codex_sandbox_can_execute_python_without_a_model(self):
        with tempfile.TemporaryDirectory() as d:
            work, home = H.prepare_dirs(Path(d))
            prefix = H.isolation_prefix(work, home, H.codex_binary(), auth=None)
            # Exercise the same configuration via the offline `sandbox` command.
            # exec-only switches and --strict-config are not supported by sandbox.
            flags = []
            for i, arg in enumerate(H.CODEX_FLAGS):
                if arg in ("-c", "--disable", "--enable"):
                    flags.extend([arg, H.CODEX_FLAGS[i + 1]])
            script = "from pathlib import Path; Path('/work/checked').write_text('ok'); print('PYTHON_OK')"
            cmd = prefix + ["/opt/codex", "--no-daemon", *flags,
                            "-c", 'sandbox_mode="workspace-write"', "sandbox", "--",
                            "/usr/bin/python3", "-c", script]
            result = subprocess.run(cmd, env=H.child_env(), capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "PYTHON_OK")
            self.assertEqual((work / "checked").read_text(), "ok")

    def test_cache_reuses_one_attempt_and_row_matches_existing_schema(self):
        with tempfile.TemporaryDirectory() as d:
            cache = Path(d, "cache")
            with patch.object(H, "CACHE", cache), patch.object(H, "call_codex") as call:
                call.return_value = dict(text="def f(): return 1\n", wall_s=0.1,
                                         is_error=False, error=None, in_tok=2, out_tok=3)
                first = H.one("luna-low", "p01_overlap_minutes", 1, 3, "0.163.0", "bwrap-test")
                second = H.one("luna-low", "p01_overlap_minutes", 1, 3, "0.163.0", "bwrap-test")
                self.assertEqual(call.call_count, 1)
                self.assertEqual(first, second)
                with patch.object(H, "grade_text", return_value={"outcome": "pass", "cases": 1}):
                    row = H.grade_entry(first)
                self.assertEqual(set(row), set(H.FIELDS) | {
                    "rung", "outcome", "passed", "grade_detail", "code_lines", "harness"})
                self.assertEqual(row["harness"], "codex-designed")
                self.assertTrue(row["passed"])

    def test_complete_offline_cli_pipeline_extracts_artifact_and_usage(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            fake = base / "fake-codex"
            fake.write_text('''#!/usr/bin/python3
import json
from pathlib import Path
import sys
assert sys.argv[1:3] == ['--no-daemon', 'exec']
assert '<problem>' in sys.stdin.read()
Path('/work/solution.py').write_text('def f(): return 42\\n')
print(json.dumps({'type': 'item.completed', 'item': {
    'type': 'agent_message', 'text': 'Finished. This is not the source.'}}))
print(json.dumps({'type': 'turn.completed', 'usage': {
    'input_tokens': 123, 'cached_input_tokens': 10, 'output_tokens': 45}}))
''')
            fake.chmod(0o755)
            with patch.object(H, "CACHE", base / "cache"), \
                    patch.object(H, "codex_binary", return_value=fake), \
                    patch.object(H, "auth_path", return_value=None):
                result = H.call_codex("luna-low", "<problem>offline test</problem>", "fake-key")
            self.assertEqual(result["text"], "def f(): return 42\n")
            self.assertEqual(result["final_message"], "Finished. This is not the source.")
            self.assertEqual((result["in_tok"], result["cached_tok"], result["out_tok"]), (123, 10, 45))
            self.assertFalse(result["is_error"])

    def test_interrupted_attempt_is_not_retried(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(H, "CACHE", Path(d)), patch.object(H, "call_codex") as call:
                call.side_effect = KeyboardInterrupt
                with self.assertRaises(KeyboardInterrupt):
                    H.one("luna-low", "p01_overlap_minutes", 1, 3, "0.163.0", "bwrap-test")
                entry = H.one("luna-low", "p01_overlap_minutes", 1, 3, "0.163.0", "bwrap-test")
                self.assertEqual(call.call_count, 1)
                self.assertTrue(entry["is_error"])
                self.assertIn("interrupted", entry["error"])


if __name__ == "__main__":
    unittest.main()
