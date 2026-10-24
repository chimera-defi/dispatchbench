"""Harness contract checks; never invoke a real model or inspect problem solutions."""
from pathlib import Path
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from bench import codex_harness as H


class HarnessTests(unittest.TestCase):
    def test_installed_codex_package_helpers_run_inside_isolation(self):
        with tempfile.TemporaryDirectory() as d:
            work, home = H.prepare_dirs(Path(d))
            exe = H.codex_binary()
            prefix = H.isolation_prefix(work, home, exe, auth=None)
            helper = '/opt/codex-release/bin/codex-code-mode-host'
            result = subprocess.run(prefix + [helper, '--help'], env=H.child_env(),
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Usage: codex-code-mode-host', result.stdout)
            # Start the actual stdio server, then deliver EOF. No model or auth.
            result = subprocess.run(prefix + [helper, '--listen', 'stdio'], env=H.child_env(),
                                    stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            script = ("import json,shutil,subprocess; from pathlib import Path; "
                      "root=Path('/opt/codex-release'); "
                      "manifest=json.loads((root/'codex-package.json').read_text()); "
                      "assert (root/manifest['entrypoint']).is_file(); "
                      "assert (root/manifest['resourcesDir']/'bwrap').is_file(); "
                      "assert (root/manifest['pathDir']/'rg').is_file(); "
                      "assert shutil.which('rg') == str(root/'codex-path/rg'); "
                      "assert not Path('~').exists(); "
                      "subprocess.run(['rg','--version'],check=True,stdout=subprocess.DEVNULL); "
                      "subprocess.run(['node','--version'],check=True,stdout=subprocess.DEVNULL); "
                      "subprocess.run([str(root/'codex-resources/bwrap'),'--version'],check=True,stdout=subprocess.DEVNULL); "
                      "print('PACKAGE_RUNTIME_OK')")
            result = subprocess.run(prefix + ['/usr/bin/python3', '-c', script], env=H.child_env(),
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), 'PACKAGE_RUNTIME_OK')
            command = H.command_for('luna-low', work, home, exe, auth=None)
            self.assertEqual(command[command.index('--') + 1], '/opt/codex-release/bin/codex')

    def test_codex_tool_error_items_are_not_successful_tools(self):
        error = {'type': 'item.completed', 'item': {'type': 'error',
                 'message': 'Code Mode is unavailable: failed to spawn code-mode host'}}
        done = {'type': 'turn.completed', 'usage': {'input_tokens': 10, 'output_tokens': 20}}
        parsed = H.parse_codex('\n'.join(map(json.dumps, [error, done])))
        self.assertIn('Code Mode', parsed['error'])
        self.assertEqual(parsed['successful_tool_items'], 0)
        self.assertEqual(parsed['tool_items'], 0)
        ordinary_failure = {'type': 'item.completed', 'item': {'type': 'command_execution',
                            'status': 'completed', 'exit_code': 1}}
        success = {'type': 'item.completed', 'item': {'type': 'command_execution',
                   'status': 'completed', 'exit_code': 0}}
        parsed = H.parse_codex('\n'.join(map(json.dumps, [ordinary_failure, success, done])))
        self.assertIsNone(parsed['error'])
        self.assertEqual(parsed['tool_items'], 2)
        self.assertEqual(parsed['successful_tool_items'], 1)

    def test_missing_companion_in_a_packaged_codex_fails_before_launch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel in ('bin/codex', 'codex-path/rg', 'codex-resources/bwrap'):
                path = root/rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('#!/bin/sh\nexit 0\n')
                path.chmod(0o755)
            (root/'codex-package.json').write_text(json.dumps(dict(
                layoutVersion=1, entrypoint='bin/codex', pathDir='codex-path', resourcesDir='codex-resources')))
            with self.assertRaisesRegex(RuntimeError, 'codex-code-mode-host'):
                H.codex_package(root/'bin/codex')

    def test_codex_failure_events_and_stderr_never_cache_partial_artifacts(self):
        for mode in ('error_item', 'stderr', 'no_tools'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as d:
                base = Path(d)
                fake = base/'offline-codex'
                fake.write_text('''#!/usr/bin/python3
import json,sys
from pathlib import Path
mode = ''' + repr(mode) + '''
sys.stdin.read()
if mode != 'no_tools':
    Path('/work/solution.py').write_text('def fixture_only(): return 42\\n')
if mode == 'error_item':
    print(json.dumps({'type':'item.completed','item':{'type':'error', 'message':'Code Mode is unavailable'}}))
if mode == 'stderr':
    print('ERROR: failed to spawn code-mode host /opt/codex-code-mode-host',file=sys.stderr)
print(json.dumps({'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':20}}))
''')
                fake.chmod(0o755)
                with patch.object(H,'CACHE',base/'cache'), patch.object(H,'codex_binary',return_value=fake), \
                        patch.object(H,'auth_path',return_value=None):
                    entry = H.one('luna-low','p01_overlap_minutes',1,3,'test','test')
                    self.assertTrue(entry['is_error'])
                    self.assertEqual(H.grade_entry(entry)['outcome'],'harness_error')
                    self.assertFalse(list((H.CACHE/'calls').glob('*.json')))

    def test_codex_missing_artifact_without_successful_tools_is_not_cached(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(H, 'CACHE', Path(d)), patch.object(H, 'call_codex') as call:
                call.return_value = dict(text='', wall_s=5.8, is_error=False, error=None,
                                         tool_items=0, successful_tool_items=0)
                entry = H.one('luna-low', 'p01_overlap_minutes', 1, 3, 'test', 'test')
                self.assertTrue(entry['is_error'])
                self.assertEqual(H.grade_entry(entry)['outcome'], 'harness_error')
                self.assertFalse(list((Path(d)/'calls').glob('*.json')))
                H.one('luna-low', 'p01_overlap_minutes', 1, 3, 'test', 'test')
                self.assertEqual(call.call_count, 2)
                call.return_value.update(successful_tool_items=1, tool_items=1)
                entry = H.one('luna-low', 'p01_overlap_minutes', 1, 3, 'test', 'test')
                self.assertFalse(entry['is_error'])
                self.assertEqual(H.grade_entry(entry)['outcome'], 'no_code')

    def test_legacy_codex_tool_error_is_migrated_from_raw_log(self):
        with tempfile.TemporaryDirectory(dir=H.ROOT) as d:
            with patch.object(H, 'CACHE', Path(d)), patch.object(H, 'OUT', Path(d)/'rows.jsonl'):
                raw = Path(d)/'raw'
                raw.mkdir()
                events = [dict(type='item.completed', item=dict(type='error', message='Code Mode is unavailable')),
                          dict(type='turn.completed', usage={})]
                (raw/'old.out').write_text('\n'.join(map(json.dumps, events)))
                H.atomic_json(Path(d)/'calls/old.json', dict(key='old', cli='codex', is_error=False,
                              error=None, text='', tool_items=1, raw_id='old'))
                migrated = H.clear_failed_cache()
                self.assertIn('old', migrated)
                self.assertFalse((Path(d)/'calls/old.json').exists())
                receipt = json.loads(next((Path(d)/'errors').glob('*.json')).read_text())
                self.assertEqual(receipt['outcome'], 'harness_error')
                self.assertIn('Code Mode', receipt['error'])
                row = dict(key='old', cli='codex', config='luna-low', ts='test', problem='p01_overlap_minutes',
                           repeat=1, outcome='no_code', passed=False, is_error=False, tool_items=1)
                H.OUT.write_text(json.dumps(row)+'\n')
                with contextlib.redirect_stdout(io.StringIO()):
                    H.export([], migrated)
                row = json.loads(H.OUT.read_text())
                self.assertEqual(row['outcome'], 'harness_error')
                self.assertTrue(row['is_error'])

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
                "from pathlib import Path; import ssl; "
                f"assert not Path({str(H.ROOT)!r}).exists(); "
                "assert not Path('~').exists(); "
                "assert not Path('/home/codex/.codex/AGENTS.md').exists(); "
                "assert Path('/etc/resolv.conf').is_file(), 'resolver symlink is broken'; "
                "assert ssl.create_default_context().get_ca_certs(), 'no trusted CA certificates'; "
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
            cmd = prefix + [H.sandbox_codex_binary(H.codex_binary()), "--no-daemon", *flags,
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

    def test_interrupted_attempt_retries_on_next_invocation(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(H, "CACHE", Path(d)), patch.object(H, "call_codex") as call:
                call.side_effect = KeyboardInterrupt
                with self.assertRaises(KeyboardInterrupt):
                    H.one("luna-low", "p01_overlap_minutes", 1, 3, "0.163.0", "bwrap-test")
                call.side_effect = None
                call.return_value = dict(text="def f(): return 42\n", wall_s=0.1, is_error=False, error=None)
                entry = H.one("luna-low", "p01_overlap_minutes", 1, 3, "0.163.0", "bwrap-test")
                self.assertEqual(call.call_count, 2)
                self.assertFalse(entry["is_error"])

    def test_transport_failure_is_audited_not_cached_and_retries_next_time(self):
        for config, name in [("luna-low", "call_codex"), ("haiku-low", "call_claude")]:
            with self.subTest(config=config), tempfile.TemporaryDirectory() as d:
                with patch.object(H, "CACHE", Path(d)), patch.object(H, name) as call:
                    call.side_effect = [dict(text="def f(): return 42\n", wall_s=0.1,
                                             is_error=True, error="EAI_AGAIN"),
                                        dict(text="def f(): return 42\n", wall_s=0.2,
                                             is_error=False, error=None)]
                    failed = H.one(config, "p01_overlap_minutes", 1, 3, "test", "bwrap-test")
                    self.assertFalse(list((Path(d) / "calls").glob("*.json")))
                    self.assertEqual(len(list((Path(d) / "errors").glob("*.json"))), 1)
                    with patch.object(H, "grade_text", side_effect=AssertionError("must not grade partial artifacts")):
                        self.assertEqual(H.grade_entry(failed)["outcome"], "harness_error")
                    succeeded = H.one(config, "p01_overlap_minutes", 1, 3, "test", "bwrap-test")
                    self.assertFalse(succeeded["is_error"])
                    self.assertEqual(succeeded, H.one(config, "p01_overlap_minutes", 1, 3, "test", "bwrap-test"))
                    self.assertEqual(call.call_count, 2)

    def test_legacy_error_cache_is_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(H, "CACHE", Path(d)), patch.object(H, "call_codex") as call:
                prompt = H.prompt_for("p01_overlap_minutes")
                key = H.key_for("luna-low", "p01_overlap_minutes", 1, prompt, "test", "bwrap-test")
                H.atomic_json(Path(d) / "calls" / f"{key}.json", {
                    "is_error": True, "error": "workspace routing discovery failed"})
                call.return_value = dict(text="def f(): return 42\n", wall_s=0.1, is_error=False, error=None)
                result = H.one("luna-low", "p01_overlap_minutes", 1, 3, "test", "bwrap-test")
                self.assertFalse(result["is_error"])
                self.assertEqual(call.call_count, 1)

    def test_old_error_cache_and_result_rows_are_migrated(self):
        with tempfile.TemporaryDirectory(dir=H.ROOT) as d:
            base = Path(d)
            out = base / "rows.jsonl"
            failure = dict(key="old-error", ts="test", config="luna-low", problem="p01_overlap_minutes",
                           repeat=1, is_error=True, error="routing failed", outcome="pass", passed=True)
            with patch.object(H, "CACHE", base / "cache"), patch.object(H, "OUT", out), \
                    contextlib.redirect_stdout(io.StringIO()):
                H.atomic_json(H.CACHE / "calls" / "old-error.json", failure)
                H.atomic_json(H.CACHE / "calls" / "good.json", dict(is_error=False, error=None))
                H.clear_failed_cache()
                self.assertFalse((H.CACHE / "calls" / "old-error.json").exists())
                self.assertTrue((H.CACHE / "calls" / "good.json").exists())
                self.assertEqual(len(list((H.CACHE / "errors").glob("*.json"))), 1)
                out.write_text(json.dumps(failure) + "\n")
                H.export([])
                row = json.loads(out.read_text())
                self.assertEqual(row["outcome"], "harness_error")
                self.assertFalse(row["passed"])

    def test_connectivity_mode_never_calls_a_model(self):
        argv = ["bench.codex_harness", "--configs", "luna-low,haiku-low", "--check-connectivity"]
        with patch.object(sys, "argv", argv), patch.object(H, "check_connectivity", return_value=True) as check, \
                patch.object(H, "one", side_effect=AssertionError("no model cells")):
            H.main()
            self.assertEqual({c.args[0] for c in check.call_args_list}, {"codex", "claude"})

    def test_custom_ca_path_and_lowercase_proxy_survive_isolation(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            ca = base / "custom-ca.pem"
            ca.write_text("public certificate fixture\n")
            with patch.dict(os.environ, {"SSL_CERT_FILE": str(ca), "https_proxy": "http://proxy.invalid:3128"}):
                work, home = H.prepare_dirs(base)
                script = ("import os; from pathlib import Path; "
                          "assert Path(os.environ['SSL_CERT_FILE']).read_text() == 'public certificate fixture\\n'; "
                          "assert os.environ['https_proxy'] == 'http://proxy.invalid:3128'; print('CA_PROXY_OK')")
                cmd = H.isolation_prefix(work, home, H.codex_binary(), auth=None) + ["/usr/bin/python3", "-c", script]
                result = subprocess.run(cmd, env=H.child_env(), capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), "CA_PROXY_OK")


if __name__ == "__main__":
    unittest.main()
