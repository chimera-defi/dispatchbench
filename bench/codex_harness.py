"""Codex-designed, exploratory harness for both families on unchanged L1-L6.

Design decisions (fixed before any model calls through this harness):
* Treat Codex as a coding agent: implement solution.py, execute Python checks,
  and revise inside ONE exec session. Examples and self-authored checks are
  allowed; no grader feedback, reference implementation, or hidden tests reach it.
* Use a concise task/check/submit prompt around the verbatim STATEMENT and
  SIGNATURE. Ask for complexity and semantic checks without prescribing an
  algorithm, revealing failure-specific hints, or demanding a reasoning transcript.
* Keep Codex's native model instructions and shell/edit tools. Disable unrelated
  integrations, delegation, memory, skills and hooks; none are needed for Python.
  Preserve the complete standalone release layout read-only at /opt/codex-release,
  including the sibling Code Mode host, bundled ripgrep and sandbox resources.
* Give Claude native instructions plus a task/problem/submission XML prompt, with
  Bash/Read/Edit/Write for the same implement/check/revise workflow. Use dontAsk
  with those tools explicitly allowed and permission prompts disabled, rather
  than a permission bypass. JSON output supplies measured total_cost_usd and
  usage; the submitted answer is still solution.py, never the JSON result text.
* Claude safe-mode disables customizations while retaining OAuth authentication
  (--bare would disable OAuth). Ignore setting sources and MCP, disable skills
  and Chrome. Mount only .claude/.credentials.json into a fresh Claude home;
  synthesize hasCompletedOnboarding instead of exposing the host .claude.json.
* A fresh home plus a Bubblewrap allowlist exposes system runtimes and /work,
  never the repo, previous completions, or host instructions. Existing auth.json
  is mounted read-only for the CLI, without reading/copying its contents here;
  API-key environment authentication also works. No login/credential mutation.
* workspace-write permits actual example checks. Sandbox networking is enabled:
  CLI 0.163.0's network isolation needs a NETLINK_ROUTE socket denied by the
  enclosing environment, so disabling it breaks Python tool execution. External
  lookups are forbidden in the prompt and web tools are disabled; shell egress is
  not technically blocked. No daemon or approval flow.
* Pin the requested model, effort, default tier and 1200-second total invocation
  deadline. Suppress reasoning summaries (not reasoning); leave output budgets
  and native instructions at model defaults. Never retry within an invocation or
  select among answers. Infrastructure errors may retry on the next invocation.
* The only submitted answer is the UTF-8 solution.py artifact. Preserve its bytes
  as text; ignore the final conversational message. No fence guessing, JSON code
  escaping, or test-based choice of a better candidate. For Codex, a missing file
  with no successful tools is harness_error; genuine tool success without an
  answer remains no_code. Tool error items are always infrastructure failures.
* Cache by prompt+flags hash, model/effort, repeat, CLI/Bubblewrap versions,
  isolation policy and harness source. Only non-error completions enter calls/;
  pending/ reservations and errors/ receipts are audit records, never cache hits.
  Every error is harness_error even if a partial artifact exists. Grade with
  unmodified bench.grade, serially AFTER all lanes
  finish. Rows retain bench.grade_all.FIELDS plus the usual grading fields and
  harness='codex-designed'; distinct keys are retained when exporting again.

This is a bundled harness intervention, including code execution, not an
ablation or evidence of author bias. Gains would warrant follow-up ablations.
Requires Linux, Bubblewrap/user namespaces and the selected CLI executables.
Validated CLI surfaces: codex-cli 0.163.0 exec --help/features list and
/usr/bin/claude 2.1.293 --help. Both retain the same outer filesystem isolation;
Claude has no extra inner network sandbox. Neither family's shell egress is
technically blocked; the prompts prohibit external lookups.
The allowlist also binds resolved DNS/CA targets outside /etc and /usr (not all
of /run), and preserves proxy and custom CA environment settings for transport.
No model calls occur with --dry-run or in bench.test_codex_harness.
--check-connectivity runs only unauthenticated DNS/TLS probes in the same isolation.

python3 -m bench.codex_harness --configs luna-low,luna-medium,sol61-medium,haiku-low,haiku-high,sonnet-medium --repeats 1-5 --lanes 3
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import ssl
import subprocess
import tempfile
import threading
import time

from bench import problems
from bench.grade import grade_text
from bench.grade_all import FIELDS
from bench.run import parse_codex as parse_codex_usage, parse_reps

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache" / "codex_harness"
OUT = ROOT / "results" / "appendix" / "codex_harness.jsonl"
CODEX = os.environ.get("CODEX_BIN", "codex")
CLAUDE = "/usr/bin/claude"
BWRAP = shutil.which("bwrap") or "bwrap"
CODEX_PACKAGE_DIR = "/opt/codex-release"
CODEX_TOOL_PATH = f"{CODEX_PACKAGE_DIR}/codex-path:/usr/bin:/bin"
TIMEOUT = 1200
CONFIGS = {
    "luna-low": ("gpt-6-luna", "low"),
    "luna-medium": ("gpt-6-luna", "medium"),
    "sol61-medium": ("gpt-6.1-sol", "medium"),
    "haiku-low": ("claude-haiku-5-5", "low"),
    "haiku-high": ("claude-haiku-5-5", "high"),
    "sonnet-medium": ("claude-sonnet-5-5", "medium"),
}
CLAUDE_CONFIGS = frozenset(("haiku-low", "haiku-high", "sonnet-medium"))

# All features below appear in the installed 0.163.0 `codex features list`.
DISABLED = ("apps", "plugins", "remote_plugin", "memories", "multi_agent",
            "multi_agent_v2", "hooks", "skill_search", "skill_mcp_dependency_install",
            "browser_use", "browser_use_external", "computer_use", "in_app_browser",
            "image_generation", "view_image", "goals", "sleep_tool", "tool_suggest",
            "workspace_dependencies", "worktrees", "shell_snapshot")
CODEX_FLAGS = [
    "--ignore-user-config", "--ignore-rules", "--strict-config", "--json",
    "--ephemeral", "--skip-git-repo-check", "--sandbox", "workspace-write",
    "-c", 'approval_policy="never"', "-c", 'service_tier="default"',
    "-c", 'model_reasoning_summary="none"', "-c", 'web_search="disabled"',
    "-c", "skills.include_instructions=false", "-c", "project_doc_max_bytes=0",
    "-c", "allow_login_shell=false", "-c", "sandbox_workspace_write.network_access=true",
    "-c", 'shell_environment_policy.inherit="none"',
    "-c", 'shell_environment_policy.set={PATH="' + CODEX_TOOL_PATH + '",HOME="/home/codex",LANG="C.UTF-8",TMPDIR="/tmp"}',
    "--enable", "code_mode_host",
] + [arg for feature in DISABLED for arg in ("--disable", feature)]

CLAUDE_FLAGS = [
    "--safe-mode", "--setting-sources", "", "--strict-mcp-config",
    "--mcp-config", '{"mcpServers":{}}', "--disable-slash-commands", "--no-chrome",
    "--no-session-persistence", "--output-format", "json",
    "--tools", "Bash,Read,Edit,Write", "--allowedTools", "Bash,Read,Edit,Write",
    "--permission-mode", "dontAsk", "--permission-prompts", "none",
]

TEMPLATE = """Implement the Python 3 function specified below in /work/solution.py.
Use only the Python standard library. The file must be importable with no input,
printing, or test execution at import time. Include any helpers and imports needed.

<problem>
{statement}
</problem>

Required top-level function signature:
```python
{signature}
```

Before finishing, check the algorithm against the full input bounds and the exact
rules in the statement. Use Python in this workspace to test the worked examples
and edge cases you derive yourself. For a nontrivial algorithm, small randomized
checks against a simple implementation you write can help. Fix any issues you find
within this session. Keep scratch tests separate from solution.py.

Only this statement is available: do not search for existing solutions or tests,
use the network, delegate, or install packages. Do not ask for clarification; follow
the stated contract. Your submitted answer is the final contents of solution.py.
Finish with a short confirmation; do not repeat the source in your final message.
"""

CLAUDE_TEMPLATE = """<task>
Solve the problem in Python 3. Implement the required top-level function in
/work/solution.py, using only the Python standard library. Include all needed
imports and helpers. Importing the file must not read input, print, or run tests.
</task>

<problem>
{statement}
</problem>

<signature>
{signature}
</signature>

<validation>
Check that your algorithm meets the full input bounds and follows every stated
rule. Use Bash to run Python checks of the worked examples and edge cases you
derive yourself. When useful, compare small randomized inputs against a simple
implementation you write. Fix issues within this session. Put scratch tests in
separate files. Do not search for existing solutions or tests, use the network,
delegate, or install packages. Follow the stated contract without clarification.
</validation>

<submission>
The final contents of /work/solution.py are your only submitted answer. Finish
with a short confirmation; do not repeat the source in your final response.
</submission>
"""

# Paths are deliberately an allowlist, not `--ro-bind / /` with a hidden cwd.
RUNTIME_PATHS = ("/usr", "/bin", "/sbin", "/lib", "/lib64", "/etc")
PROXY_ENV_KEYS = ("HTTPS_PROXY", "HTTP_PROXY", "ALL_PROXY", "NO_PROXY",
                  "https_proxy", "http_proxy", "all_proxy", "no_proxy")
CA_ENV_KEYS = ("SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "NODE_EXTRA_CA_CERTS")
ENV_KEYS = ("OPENAI_API_KEY", "CODEX_API_KEY") + PROXY_ENV_KEYS + CA_ENV_KEYS
CLAUDE_ENV_KEYS = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN",
                   "ANTHROPIC_BASE_URL", "CLAUDE_CODE_OAUTH_SCOPES") + PROXY_ENV_KEYS + CA_ENV_KEYS


def cli_for(config):
    return "claude" if config in CLAUDE_CONFIGS else "codex"


def child_env(family="codex"):
    keys = CLAUDE_ENV_KEYS if family == "claude" else ENV_KEYS
    env = {k: os.environ[k] for k in keys if k in os.environ}
    for key in CA_ENV_KEYS:
        if env.get(key):
            env[key] = str(Path(env[key]).expanduser().resolve(strict=True))
    env.update(PATH=CODEX_TOOL_PATH if family == "codex" else "/usr/bin:/bin", HOME="/home/codex",
               SHELL="/bin/bash", LANG="C.UTF-8", TMPDIR="/tmp")
    env["CLAUDE_CONFIG_DIR" if family == "claude" else "CODEX_HOME"] = f"/home/codex/.{family}"
    return env


def prepare_dirs(base, family="codex"):
    work, home = base / "work", base / "home"
    work.mkdir()
    (home / f".{family}").mkdir(parents=True)
    if family == "claude":
        (home / ".claude.json").write_text(json.dumps({"hasCompletedOnboarding": True}))
    return work, home


def auth_path():
    home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    path = home / "auth.json"
    return path.resolve() if path.is_file() else None


def codex_binary():
    exe = shutil.which(CODEX)
    if not exe:
        raise RuntimeError(f"Codex executable not found: {CODEX}")
    return Path(exe).resolve()


def codex_package(executable):
    """Recognize and validate the installed layout from its own manifest.

    Unpackaged executable overrides retain the single-file layout. Official
    standalone packages must have all verified companions before a call starts.
    No host home/config/session directory is exposed with the release.
    """
    root = executable.resolve().parent.parent
    manifest = root / "codex-package.json"
    if not manifest.is_file():
        return None
    data = json.loads(manifest.read_text())
    if data.get("layoutVersion") != 1:
        raise RuntimeError("Unsupported Codex standalone package layout")
    paths = {}
    for key in ("entrypoint", "resourcesDir", "pathDir"):
        path = (root / data[key]).resolve(strict=True)
        if not path.is_relative_to(root):
            raise RuntimeError(f"Codex package {key} escapes the release directory")
        paths[key] = path
    if paths["entrypoint"] != executable.resolve():
        raise RuntimeError("Codex package entrypoint does not match the executable")
    required = [executable.with_name("codex-code-mode-host"),
                paths["pathDir"] / "rg", paths["resourcesDir"] / "bwrap"]
    for path in required:
        if not path.is_file() or not os.access(path, os.X_OK):
            raise RuntimeError(f"Missing executable in Codex package: {path.name}")
    return root


def sandbox_codex_binary(executable):
    package = codex_package(executable)
    return str(Path(CODEX_PACKAGE_DIR) / executable.resolve().relative_to(package)) if package else "/opt/codex"


def claude_auth_path():
    home = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude")))
    path = home / ".credentials.json"
    return path.resolve() if path.is_file() else None


def claude_binary():
    return Path(CLAUDE).resolve(strict=True)


def network_bindings():
    """Expose only resolved DNS/trust targets missing from the runtime mounts.

    /etc/resolv.conf can point into /run/systemd/resolve. Bind that target file
    at its real path, keeping the symlink intact without exposing /run sockets.
    CA symlink targets and explicit CA environment paths receive the same treatment.
    """
    defaults = ssl.get_default_verify_paths()
    paths = [Path("/etc/resolv.conf").resolve(strict=True)]
    paths += [Path(p).resolve(strict=True) for p in (defaults.openssl_cafile, defaults.openssl_capath)
              if p and Path(p).exists()]
    paths += [Path(os.environ[key]).expanduser().resolve(strict=True)
              for key in CA_ENV_KEYS if os.environ.get(key)]
    return sorted({p for p in paths if not any(p.is_relative_to(root) for root in RUNTIME_PATHS)})


def isolation_prefix(work, home, executable, auth, family="codex"):
    cmd = [BWRAP, "--die-with-parent", "--unshare-user", "--unshare-pid",
           "--unshare-ipc", "--unshare-uts"]
    for path in RUNTIME_PATHS:
        if Path(path).exists():
            cmd += ["--ro-bind", path, path]
    # Do not inherit machine-wide Codex instructions/settings either.
    if Path("/etc/codex").exists():
        cmd += ["--tmpfs", "/etc/codex"]
    cmd += ["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
            "--bind", str(work), "/work", "--bind", str(home), "/home/codex"]
    package = codex_package(executable) if family == "codex" else None
    if package:
        cmd += ["--ro-bind", str(package), CODEX_PACKAGE_DIR]
    else:
        cmd += ["--ro-bind", str(executable), f"/opt/{family}"]
    for path in network_bindings():
        cmd += ["--ro-bind", str(path), str(path)]
    if auth:
        dest = "/home/codex/.claude/.credentials.json" if family == "claude" else "/home/codex/.codex/auth.json"
        cmd += ["--ro-bind", str(auth), dest]
    return cmd + ["--chdir", "/work", "--"]


def command_for(config, work, home, executable, auth):
    mid, effort = CONFIGS[config]
    if cli_for(config) == "claude":
        return isolation_prefix(work, home, executable, auth, "claude") + [
            "/opt/claude", "--model", mid, "--effort", effort, *CLAUDE_FLAGS, "-p",
        ]
    return isolation_prefix(work, home, executable, auth) + [
        sandbox_codex_binary(executable), "--no-daemon", "exec", "--model", mid,
        "-c", f'model_reasoning_effort="{effort}"',
        *CODEX_FLAGS, "-C", "/work", "-o", "/work/final.txt", "-",
    ]


CONNECTIVITY_PROBE = r'''
import socket, ssl, urllib.error, urllib.request
from pathlib import Path
context = ssl.create_default_context()
print('resolver_readable=' + str(Path('/etc/resolv.conf').is_file()) +
      '; trusted_CAs=' + str(len(context.get_ca_certs())) + '; TLS_verification=required', flush=True)
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM):
        print('TCP_socket_creation=OK', flush=True)
except OSError as exc:
    print('TCP_socket_creation=FAIL errno=' + str(exc.errno), flush=True)
ok = True
for host in ('api.anthropic.com', 'chatgpt.com', 'api.openai.com'):
    try:
        addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        print(host + ' DNS_OK addresses=' + str(len(addresses)), flush=True)
    except OSError as exc:
        ok = False
        print(host + ' DNS_FAIL type=' + type(exc).__name__ + ' errno=' + str(exc.errno), flush=True)
    try:
        request = urllib.request.Request('https://' + host + '/', method='HEAD')
        with urllib.request.urlopen(request, context=context, timeout=10) as response:
            print(host + ' HTTPS_OK status=' + str(response.status), flush=True)
    except urllib.error.HTTPError as exc:
        # A 4xx/5xx still proves DNS, TCP, certificate validation and HTTP transport.
        print(host + ' HTTPS_OK status=' + str(exc.code) + ' (unauthenticated HTTP response)', flush=True)
    except Exception as exc:
        ok = False
        reason = getattr(exc, 'reason', exc)
        print(host + ' HTTPS_FAIL type=' + type(reason).__name__ +
              ' errno=' + str(getattr(reason, 'errno', None)), flush=True)
raise SystemExit(0 if ok else 1)
'''


def check_connectivity(family):
    """No auth mounts, authorization headers, model calls, or result-cache writes."""
    with tempfile.TemporaryDirectory(prefix="mrb-connectivity-") as d:
        work, home = prepare_dirs(Path(d), family)
        executable = claude_binary() if family == "claude" else codex_binary()
        cmd = isolation_prefix(work, home, executable, auth=None, family=family)
        cmd += ["/usr/bin/python3", "-c", CONNECTIVITY_PROBE]
        env = child_env(family)
        for key in ("OPENAI_API_KEY", "CODEX_API_KEY", "ANTHROPIC_API_KEY",
                    "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN"):
            env.pop(key, None)
        print(f"[connectivity] family={family}; no credentials mounted", flush=True)
        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=50)
        except subprocess.TimeoutExpired:
            print("connectivity probe exceeded 50s", flush=True)
            return False
        print(result.stdout, end="", flush=True)
        if result.stderr:
            # Avoid dumping arbitrary environment-sensitive diagnostics.
            print(f"probe stderr bytes={len(result.stderr)}", flush=True)
        return result.returncode == 0


def prompt_for(pid, config="luna-low"):
    m = problems.load(pid)
    template = CLAUDE_TEMPLATE if cli_for(config) == "claude" else TEMPLATE
    return template.format(statement=m.STATEMENT, signature=m.SIGNATURE)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def key_for(config, pid, rep, prompt, version, bwrap_version):
    # Include code to cover extraction, timeout, environment and mount-policy edits.
    flags = CLAUDE_FLAGS if cli_for(config) == "claude" else CODEX_FLAGS
    policy = dict(prompt=prompt, flags=flags, timeout=TIMEOUT,
                  source_sha=digest(Path(__file__).read_text()))
    prompt_flags_sha = digest(json.dumps(policy, sort_keys=True))
    blob = dict(config=config, model=CONFIGS[config][0], effort=CONFIGS[config][1],
                cli_version=version, bwrap_version=bwrap_version, problem=pid,
                repeat=rep, prompt_flags_sha=prompt_flags_sha)
    return digest(json.dumps(blob, sort_keys=True))


def extract_answer(work):
    """The artifact IS the answer; never choose from messages or scratch files."""
    path = work / "solution.py"
    if path.is_symlink() or not path.is_file():
        return ""
    return path.read_bytes().decode("utf-8")


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, indent=1) + "\n")
    tmp.replace(path)


def parse_claude(stdout):
    """Extract accounting from the single JSON result; its prose is not source."""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        data = None
    if not isinstance(data, dict) or data.get("type") != "result":
        return dict(text="", error="Claude returned no valid JSON result", cost_usd=None,
                    cost_kind="unreported (CLI total_cost_usd missing)")
    usage = data.get("usage") or {}
    error = None
    if data.get("is_error"):
        error = str(data.get("errors") or data.get("result") or data.get("subtype") or "Claude error")[:300]
    return dict(text=data.get("result") or "", error=error,
                in_tok=sum(usage.get(k, 0) for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
                cached_tok=usage.get("cache_read_input_tokens", 0),
                cache_write_tok=usage.get("cache_creation_input_tokens", 0),
                out_tok=usage.get("output_tokens", 0),
                reasoning_tok=(usage.get("output_tokens_details") or {}).get("thinking_tokens", 0),
                api_duration_ms=data.get("duration_api_ms"), turns=data.get("num_turns"),
                tool_items=None, cost_usd=data.get("total_cost_usd"),
                cost_kind="measured (CLI total_cost_usd)" if data.get("total_cost_usd") is not None
                else "unreported (CLI total_cost_usd missing)")


def parse_codex(stdout):
    """Keep accounting, but distinguish tool failures from successful execution."""
    parsed = parse_codex_usage(stdout)
    parsed.update(tool_items=0, successful_tool_items=0, tool_error=None)
    completed = False
    tool_types = {"command_execution", "file_change", "mcp_tool_call", "web_search",
                  "tool_call", "function_call", "custom_tool_call", "code_mode", "code_execution"}
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        completed |= event.get("type") == "turn.completed"
        if event.get("type") == "item.failed":
            parsed["tool_error"] = parsed["tool_error"] or ("Codex tool error: " + str(event.get("item") or event))[:300]
            parsed["error"] = parsed["error"] or parsed["tool_error"]
        if event.get("type") != "item.completed":
            continue
        item = event.get("item") or {}
        kind = item.get("type")
        status = item.get("status")
        result = item.get("result")
        result_error = isinstance(result, dict) and (result.get("isError") or result.get("is_error"))
        ordinary_exit = kind == "command_execution" and item.get("exit_code") is not None
        tool_error = (kind == "error" or item.get("error") or item.get("is_error") or result_error
                      or (kind in tool_types and status == "failed" and not ordinary_exit))
        if tool_error:
            detail = item.get("message") or item.get("error") or item.get("text") or item
            parsed["tool_error"] = parsed["tool_error"] or ("Codex tool error: " + str(detail))[:300]
            parsed["error"] = parsed["error"] or parsed["tool_error"]
        if kind in tool_types:
            parsed["tool_items"] += 1
            success = item.get("exit_code") == 0 if kind == "command_execution" else status in ("completed", "success", "succeeded")
            if success and not tool_error:
                parsed["successful_tool_items"] += 1
    if not completed and not parsed["error"]:
        parsed["error"] = "Codex returned no completed turn"
    return parsed


def code_mode_stderr_error(stderr):
    for line in stderr.splitlines():
        lower = line.lower()
        if "failed to spawn code-mode host" in lower or "code mode will fail closed" in lower:
            return line[-300:]
    return None


def codex_entry_failure(entry, inspect_raw=False):
    """Also invalidate old no_code cache hits whose raw log proves tools failed."""
    if entry.get("cli") != "codex":
        return None
    reason = entry.get("tool_error")
    if inspect_raw:
        raw_id = entry.get("raw_id") or entry.get("key")
        if raw_id:
            raw = CACHE / "raw" / f"{raw_id}.out"
            if raw.is_file():
                parsed = parse_codex(raw.read_text())
                entry["successful_tool_items"] = parsed["successful_tool_items"]
                entry["tool_items"] = parsed["tool_items"]
                reason = reason or parsed["error"]
            stderr = CACHE / "raw" / f"{raw_id}.err"
            if stderr.is_file():
                reason = reason or code_mode_stderr_error(stderr.read_text())
    if reason:
        return str(reason)
    if not entry.get("text", "").strip() and not entry.get("successful_tool_items", 0):
        return "Codex produced no solution.py and no successful tool items"
    return None


def call_codex(config, prompt, key):
    return call_model(config, prompt, key)


def call_claude(config, prompt, key):
    return call_model(config, prompt, key)


def call_model(config, prompt, key):
    family = cli_for(config)
    executable, auth = (claude_binary(), claude_auth_path()) if family == "claude" else (codex_binary(), auth_path())
    with tempfile.TemporaryDirectory(prefix=f"mrb-{family}-") as d:
        work, home = prepare_dirs(Path(d), family)
        cmd = command_for(config, work, home, executable, auth)
        started = time.monotonic()
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, cwd=work, env=child_env(family), start_new_session=True)
        timed_out = False
        try:
            stdout, stderr = p.communicate(prompt, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(p.pid, signal.SIGKILL)
            stdout, stderr = p.communicate()
        wall = time.monotonic() - started
        res = parse_claude(stdout) if family == "claude" else parse_codex(stdout)
        res["final_message"] = res.pop("text")
        try:
            res["text"] = extract_answer(work)
        except UnicodeDecodeError:
            res["text"] = ""
            res["error"] = "solution.py is not UTF-8"
        if family == "codex":
            res["error"] = (res["error"] or code_mode_stderr_error(stderr)
                            or codex_entry_failure(dict(res, cli="codex")))
        if timed_out:
            res["error"] = f"{family} invocation exceeded {TIMEOUT}s (no retry)"
        elif p.returncode and not res["error"]:
            res["error"] = stderr.strip()[-300:] or f"{family} exited {p.returncode}"
        res.update(wall_s=wall, is_error=bool(res["error"]))
        if family == "codex":
            res.update(cost_usd=None, cost_kind="proxy (list price x tokens)")
        if res["error"]:
            res["error"] = res["error"].replace(d, "<scratch>").replace(str(Path.home()), "~")
        raw = CACHE / "raw"
        raw.mkdir(parents=True, exist_ok=True)
        raw_id = f"{key}-{time.time_ns()}"
        (raw / f"{raw_id}.out").write_text(stdout)
        (raw / f"{raw_id}.err").write_text(stderr)
        res["raw_id"] = raw_id
        return res


def archive_failure(entry, key):
    """A diagnostic receipt is not a reusable completion or a graded candidate."""
    atomic_json(CACHE / "errors" / f"{key}-{time.time_ns()}.json",
                dict(entry, key=key, is_error=True, outcome="harness_error"))


def clear_failed_cache():
    """Migrate old harness versions' error entries out of the result cache."""
    failures = {}
    for path in (CACHE / "calls").glob("*.json"):
        entry = json.loads(path.read_text())
        reason = codex_entry_failure(entry, inspect_raw=True)
        if reason:
            entry.update(is_error=True, error=reason)
        if entry.get("is_error", True) or entry.get("error"):
            failures[path.stem] = entry.get("error") or "CLI failure"
            archive_failure(entry, path.stem)
            path.unlink()
    return failures


def one(config, pid, rep, lanes, version, bwrap_version):
    prompt = prompt_for(pid, config)
    key = key_for(config, pid, rep, prompt, version, bwrap_version)
    path = CACHE / "calls" / f"{key}.json"
    if path.exists():
        cached = json.loads(path.read_text())
        reason = codex_entry_failure(cached, inspect_raw=True)
        if reason:
            cached.update(is_error=True, error=reason)
        if not cached.get("is_error", True) and not cached.get("error"):
            return cached
        archive_failure(cached, key)
        path.unlink()
    pending = CACHE / "pending" / f"{key}.json"
    if pending.exists():
        archive_failure(json.loads(pending.read_text()), key)
    mid, effort = CONFIGS[config]
    entry = dict(key=key, ts=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                 phase="codex_harness", config=config, cli=cli_for(config), cli_version=version,
                 model=mid, effort=effort, problem=pid, repeat=rep, lanes=lanes,
                 prompt_sha=digest(prompt)[:12], harness="codex-designed",
                 bwrap_version=bwrap_version, text="", wall_s=0.0, is_error=True,
                 error="attempt interrupted after reservation; eligible to retry next invocation")
    atomic_json(pending, entry)
    try:
        call = call_claude if cli_for(config) == "claude" else call_codex
        entry.update(call(config, prompt, key))
    except (OSError, RuntimeError) as exc:
        entry.update(is_error=True, error=str(exc)[:300])
    reason = codex_entry_failure(entry)
    if reason and not entry.get("error"):
        entry.update(is_error=True, error=reason)
    entry["is_error"] = bool(entry.get("is_error") or entry.get("error"))
    if entry["is_error"]:
        archive_failure(entry, key)
    else:
        atomic_json(path, entry)
    pending.unlink()
    return entry


def grade_entry(entry):
    reason = codex_entry_failure(entry)
    if reason and not entry.get("error"):
        entry = dict(entry, is_error=True, error=reason)
    code = entry.get("text", "")
    if entry["is_error"] or entry.get("error"):
        g = dict(outcome="harness_error", detail=entry.get("error"))
    elif not code.strip():
        g = dict(outcome="no_code", detail="missing or empty solution.py")
    else:
        # Match existing grading, but version the grade cache by grader bytes too.
        files = [Path(problems.path(entry["problem"])), ROOT / "bench" / "grade.py",
                 ROOT / "bench" / "sandbox_exec.py"]
        grade_key = digest(json.dumps([digest(p.read_text()) for p in files] + [code]))
        path = CACHE / "grades" / f"{grade_key}.json"
        if path.exists():
            g = json.loads(path.read_text())
        else:
            g = grade_text(entry["problem"], code)
            atomic_json(path, g)
    row = {field: entry.get(field) for field in FIELDS}
    row.update(rung=problems.load(entry["problem"]).RUNG, outcome=g["outcome"],
               passed=g["outcome"] == "pass", grade_detail=g.get("detail"),
               code_lines=code.count("\n"), harness="codex-designed")
    return row


def export(entries, prior_failures=None):
    # Preserve earlier invocations and prompt/flag variants, deduplicate by key.
    rows = {r["key"]: r for r in map(json.loads, OUT.read_text().splitlines())} if OUT.exists() else {}
    for row in rows.values():
        reason = (prior_failures or {}).get(row["key"])
        if row.get("cli") == "codex" and row.get("outcome") == "no_code" and not row.get("tool_items"):
            reason = reason or "Codex produced no solution.py and no successful tool items"
        if reason:
            row.update(is_error=True, error=reason)
        if row.get("is_error") or row.get("error"):
            row.update(outcome="harness_error", passed=False, grade_detail=row.get("error"))
    for entry in entries:
        row = grade_entry(entry)
        rows[row["key"]] = row
        print(f"[grade] {row['config']} {row['problem']} r{row['repeat']}: {row['outcome']}", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    with tmp.open("w") as f:
        for row in sorted(rows.values(), key=lambda r: (r["ts"], r["config"], r["problem"], r["repeat"], r["key"])):
            f.write(json.dumps(row) + "\n")
    tmp.replace(OUT)
    print(f"{len(rows)} rows -> {OUT.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--configs", default=",".join(CONFIGS))
    ap.add_argument("--repeats", default="1-5")
    ap.add_argument("--lanes", type=int, default=3)
    ap.add_argument("--problems", default="all", help="all (L1-L6), or comma-separated problem IDs")
    ap.add_argument("--dry-run", action="store_true", help="print one exact invocation and prompt; no model calls")
    ap.add_argument("--check-connectivity", action="store_true", help="unauthenticated DNS/HTTPS probes only; no model calls")
    args = ap.parse_args()
    configs = args.configs.split(",")
    pids = problems.MAIN if args.problems == "all" else args.problems.split(",")
    try:
        reps = parse_reps(args.repeats)
    except ValueError:
        ap.error("--repeats must be an integer or inclusive range, e.g. 1-5")
    if not 1 <= args.lanes <= 4:
        ap.error("--lanes must be between 1 and 4")
    if not reps or any(r < 1 for r in reps):
        ap.error("repeats must be positive integers")
    if len(set(configs)) != len(configs) or any(c not in CONFIGS for c in configs):
        ap.error("configs must be unique members of " + ",".join(CONFIGS))
    if len(set(pids)) != len(pids) or any(p not in problems.MAIN for p in pids):
        ap.error("problems must be unique L1-L6 problem IDs")
    if args.dry_run and args.check_connectivity:
        ap.error("choose either --dry-run or --check-connectivity")
    if args.check_connectivity:
        outcomes = [check_connectivity(family) for family in sorted({cli_for(c) for c in configs})]
        if not all(outcomes):
            raise SystemExit(1)
        return
    versions = {family: subprocess.run([CLAUDE if family == "claude" else CODEX, "--version"],
                                      capture_output=True, text=True, check=True).stdout.strip()
                for family in sorted({cli_for(config) for config in configs})}
    bv = subprocess.run([BWRAP, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    if args.dry_run:
        with tempfile.TemporaryDirectory(prefix="mrb-codex-dry-") as d:
            family = cli_for(configs[0])
            work, home = prepare_dirs(Path(d), family)
            executable, auth = (claude_binary(), claude_auth_path()) if family == "claude" else (codex_binary(), auth_path())
            cmd = command_for(configs[0], work, home, executable, auth)
            print(f"CLI: {versions[family]}; {bv}")
            print(f"Cell: {configs[0]} {pids[0]} r{reps[0]}; timeout={TIMEOUT}s")
            config_home = "CLAUDE_CONFIG_DIR" if family == "claude" else "CODEX_HOME"
            print(f"Environment: isolated HOME/{config_home}; auth mounted read-only if available; "
                  "only family auth/endpoint/proxy variables inherited (values never printed)")
            print("Command (prompt supplied verbatim on stdin):\n" + shlex.join(cmd))
            print("Prompt:\n" + prompt_for(pids[0], configs[0]), end="")
        return
    CACHE.mkdir(parents=True, exist_ok=True)
    # An exclusive process lock prevents duplicate attempts from competing runners.
    with (CACHE / ".lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            ap.error("another codex_harness runner owns this cache")
        prior_failures = clear_failed_cache()
        stop = threading.Event()

        def lane(config):
            entries = []
            for rep in reps:
                for pid in pids:
                    if stop.is_set():
                        return entries
                    entry = one(config, pid, rep, args.lanes, versions[cli_for(config)], bv)
                    entries.append(entry)
                    print(f"[generate] {config} {pid} r{rep}: {entry['wall_s']:.1f}s"
                          f"{' ERROR ' + str(entry.get('error')) if entry['is_error'] else ''}", flush=True)
                    if any(s in (entry.get("error") or "").lower()
                           for s in ("quota", "rate limit", "rate_limit", "usage limit")):
                        stop.set()
            return entries

        with ThreadPoolExecutor(args.lanes) as pool:
            entries = [entry for batch in pool.map(lane, configs) for entry in batch]
        export(entries, prior_failures)  # No timed grading overlaps generation, including other lanes.
        if stop.is_set():
            raise SystemExit("quota/rate limit: stopped new calls; completed cells exported, others missing")


if __name__ == "__main__":
    main()
